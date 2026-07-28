from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import APIModel


class CreateChatSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)


class ChatSessionRead(APIModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime


class CitationRead(BaseModel):
    chunk_id: str
    file_name: str
    page_number: int
    quote: str
    score: float | None = None


class ChatMessageRead(APIModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    citations_json: list[CitationRead] | None = None
    created_at: datetime


class AskQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    document_ids: list[uuid.UUID] | None = None
    top_k: int | None = Field(default=None, ge=1, le=20)


class AnswerResponse(BaseModel):
    answer: str
    citations: list[CitationRead]
    session_id: uuid.UUID
    message_id: uuid.UUID
