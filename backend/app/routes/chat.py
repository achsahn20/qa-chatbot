from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.chat import (
    AnswerResponse,
    AskQuestionRequest,
    ChatMessageRead,
    ChatSessionRead,
    CreateChatSessionRequest,
)
from app.schemas.common import PaginatedResponse
from app.services.chat_service import chat_service


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/sessions", response_model=ChatSessionRead)
def create_session(
    payload: CreateChatSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSessionRead:
    session = chat_service.create_session(db, current_user, payload.title)
    return ChatSessionRead.model_validate(session)


@router.get("/sessions", response_model=PaginatedResponse[ChatSessionRead])
def list_sessions(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ChatSessionRead]:
    items, total = chat_service.list_sessions(db, current_user, page, limit)
    return PaginatedResponse(items=[ChatSessionRead.model_validate(item) for item in items], total=total, page=page, limit=limit)


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageRead])
def get_messages(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatMessageRead]:
    session = chat_service.get_session_for_user(db, session_id, current_user)
    messages = chat_service.get_messages(db, session)
    return [ChatMessageRead.model_validate(message) for message in messages]


@router.post("/sessions/{session_id}/ask", response_model=AnswerResponse)
def ask_question(
    session_id: uuid.UUID,
    payload: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnswerResponse:
    session = chat_service.get_session_for_user(db, session_id, current_user)
    message, answer, citations = chat_service.ask_question(
        db,
        current_user,
        session,
        payload.question,
        payload.document_ids,
        payload.top_k,
    )
    return AnswerResponse(answer=answer, citations=citations, session_id=session.id, message_id=message.id)
