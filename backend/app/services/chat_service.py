from __future__ import annotations

from datetime import datetime, timezone
import time
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.user import User
from app.rag.citations import build_citations
from app.rag.generator import get_answer_generator
from app.rag.retriever import retrieve_chunks


settings = get_settings()


class ChatService:
    def __init__(self) -> None:
        self.answer_generator = get_answer_generator()

    def create_session(self, db: Session, user: User, title: str | None = None) -> ChatSession:
        session = ChatSession(user_id=user.id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_session_for_user(self, db: Session, session_id: uuid.UUID, user: User) -> ChatSession:
        session = db.get(ChatSession, session_id)
        if session is None or session.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found.")
        return session

    def list_sessions(self, db: Session, user: User, page: int, limit: int) -> tuple[list[ChatSession], int]:
        query = select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.last_message_at.desc())
        total = db.scalar(select(func.count()).select_from(ChatSession).where(ChatSession.user_id == user.id)) or 0
        items = db.scalars(query.offset((page - 1) * limit).limit(limit)).all()
        return items, total

    def get_messages(self, db: Session, session: ChatSession) -> list[ChatMessage]:
        return db.scalars(
            select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc())
        ).all()

    def ask_question(
        self,
        db: Session,
        user: User,
        session: ChatSession,
        question: str,
        document_ids: list[uuid.UUID] | None = None,
        top_k: int | None = None,
    ) -> tuple[ChatMessage, str, list[dict]]:
        allowed_document_ids: list[str] | None = None
        if document_ids:
            owned_documents = db.scalars(
                select(Document).where(Document.owner_id == user.id, Document.id.in_(document_ids))
            ).all()
            allowed_document_ids = [str(document.id) for document in owned_documents]
            if not allowed_document_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No matching documents found.")

        user_message = ChatMessage(session_id=session.id, user_id=user.id, role="user", content=question)
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        started = time.perf_counter()
        retrieved_chunks = retrieve_chunks(
            question=question,
            owner_id=str(user.id),
            document_ids=allowed_document_ids,
            top_k=top_k,
        )
        generated = self.answer_generator.generate(question=question, chunks=retrieved_chunks)
        citations = build_citations(generated.source_ids, retrieved_chunks)
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        assistant_message = ChatMessage(
            session_id=session.id,
            user_id=user.id,
            role="assistant",
            content=generated.answer,
            retrieval_filters={"document_ids": allowed_document_ids or [], "top_k": top_k or settings.default_top_k},
            source_chunk_ids=[citation["chunk_id"] for citation in citations],
            citations_json=citations,
            context_snapshot=retrieved_chunks,
            model_name=generated.model_name,
            latency_ms=elapsed_ms,
            status="success",
        )
        db.add(assistant_message)

        if not session.title:
            session.title = question[:80]
        session.last_message_at = datetime.now(timezone.utc)
        session.updated_at = session.last_message_at
        db.add(session)
        db.commit()
        db.refresh(assistant_message)
        return assistant_message, generated.answer, citations


chat_service = ChatService()
