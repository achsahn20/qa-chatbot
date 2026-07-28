from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.document import DocumentRead, ProcessDocumentRequest, UploadResponse
from app.services.document_service import document_service


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
def upload_documents(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    documents = []
    for upload_file in files:
        document = document_service.create_document_record(db, current_user, upload_file)
        documents.append(document)
        background_tasks.add_task(document_service.process_document, str(document.id))

    return UploadResponse(
        documents=[
            {"id": document.id, "original_file_name": document.original_file_name, "status": document.status}
            for document in documents
        ]
    )


@router.get("", response_model=PaginatedResponse[DocumentRead])
def list_documents(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[DocumentRead]:
    items, total = document_service.get_user_documents(db, current_user, page, limit, status, search)
    return PaginatedResponse(items=[DocumentRead.model_validate(item) for item in items], total=total, page=page, limit=limit)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    document = document_service.get_document_for_user(db, document_id, current_user)
    return DocumentRead.model_validate(document)


@router.post("/{document_id}/process", response_model=MessageResponse)
def process_document(
    document_id: uuid.UUID,
    payload: ProcessDocumentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    document = document_service.get_document_for_user(db, document_id, current_user)
    background_tasks.add_task(document_service.process_document, str(document.id), payload.force_reprocess)
    return MessageResponse(message="Document processing started.")


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    document = document_service.get_document_for_user(db, document_id, current_user)
    document_service.delete_document(db, document)
    return MessageResponse(message="Document deleted.")
