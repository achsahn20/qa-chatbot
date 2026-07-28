from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.session import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.rag.chunker import chunk_pages
from app.rag.embeddings import get_embedding_service
from app.rag.parser import extract_pdf_pages
from app.rag.vector_store import get_vector_store
from app.services.storage_service import LocalStorageService
from app.utils.validators import validate_pdf_upload


settings = get_settings()


class DocumentService:
    def __init__(self) -> None:
        self.storage = LocalStorageService()
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()

    def create_document_record(self, db: Session, owner: User, upload_file: UploadFile) -> Document:
        upload_meta = self.storage.save_upload(upload_file, str(owner.id))
        try:
            validate_pdf_upload(upload_file, upload_meta["file_size"])
        except Exception:
            self.storage.delete_file(upload_meta["storage_key"])
            raise

        document = Document(
            owner_id=owner.id,
            original_file_name=upload_file.filename or "document.pdf",
            storage_key=upload_meta["storage_key"],
            mime_type=upload_file.content_type or "application/pdf",
            file_size=upload_meta["file_size"],
            sha256_hash=upload_meta["sha256_hash"],
            status="uploaded",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_user_documents(
        self,
        db: Session,
        user: User,
        page: int,
        limit: int,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> tuple[list[Document], int]:
        filters = [Document.owner_id == user.id]
        if status_filter:
            filters.append(Document.status == status_filter)
        if search:
            filters.append(Document.original_file_name.ilike(f"%{search}%"))

        query = select(Document).where(*filters).order_by(Document.uploaded_at.desc())
        total = db.scalar(select(func.count()).select_from(Document).where(*filters)) or 0
        items = db.scalars(query.offset((page - 1) * limit).limit(limit)).all()
        return items, total

    def get_document_for_user(self, db: Session, document_id: uuid.UUID, user: User) -> Document:
        document = db.get(Document, document_id)
        if document is None or document.owner_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        return document

    def delete_document(self, db: Session, document: Document) -> None:
        self.vector_store.delete_by_document(str(document.id))
        self.storage.delete_file(document.storage_key)
        db.delete(document)
        db.commit()

    def process_document(self, document_id: str, force_reprocess: bool = False) -> None:
        with SessionLocal() as db:
            document = db.get(Document, uuid.UUID(document_id))
            if document is None:
                return

            if document.status == "ready" and not force_reprocess:
                return

            document.status = "processing"
            document.processing_error = None
            db.add(document)
            db.commit()

            try:
                self.vector_store.delete_by_document(str(document.id))
                existing_chunks = db.scalars(select(DocumentChunk).where(DocumentChunk.document_id == document.id)).all()
                for chunk in existing_chunks:
                    db.delete(chunk)
                db.commit()

                file_path = self.storage.get_absolute_path(document.storage_key)
                pages = extract_pdf_pages(file_path)
                chunks = chunk_pages(pages)
                embeddings = self.embedding_service.embed_texts([chunk.content for chunk in chunks])

                chunk_records: list[DocumentChunk] = []
                vector_ids: list[str] = []
                vector_documents: list[str] = []
                vector_metadatas: list[dict[str, Any]] = []

                for chunk, embedding in zip(chunks, embeddings, strict=False):
                    vector_id = f"chunk_{uuid.uuid4()}"
                    source_id = f"CTX_{len(vector_ids) + 1:02d}"
                    record = DocumentChunk(
                        document_id=document.id,
                        owner_id=document.owner_id,
                        chunk_index=chunk.chunk_index,
                        page_number=chunk.page_number,
                        section_title=chunk.section_title,
                        content=chunk.content,
                        token_count=chunk.token_count,
                        char_start=chunk.char_start,
                        char_end=chunk.char_end,
                        vector_id=vector_id,
                        embedding_model=settings.embedding_model,
                        metadata_json={"source_id": source_id},
                    )
                    chunk_records.append(record)
                    vector_ids.append(vector_id)
                    vector_documents.append(chunk.content)
                    vector_metadatas.append(
                        {
                            "chunk_id": str(record.id),
                            "document_id": str(document.id),
                            "owner_id": str(document.owner_id),
                            "file_name": document.original_file_name,
                            "page_number": chunk.page_number,
                            "section_title": chunk.section_title or "",
                            "source_id": source_id,
                        }
                    )

                db.add_all(chunk_records)
                db.flush()

                for meta, record in zip(vector_metadatas, chunk_records, strict=False):
                    meta["chunk_id"] = str(record.id)

                self.vector_store.upsert_chunks(
                    chunk_ids=vector_ids,
                    documents=vector_documents,
                    embeddings=embeddings,
                    metadatas=vector_metadatas,
                )

                document.page_count = len(pages)
                document.status = "ready"
                document.processed_at = datetime.now(timezone.utc)
                document.processing_error = None
                db.add(document)
                db.commit()
            except Exception as exc:
                document.status = "failed"
                document.processing_error = str(exc)
                db.add(document)
                db.commit()


document_service = DocumentService()
