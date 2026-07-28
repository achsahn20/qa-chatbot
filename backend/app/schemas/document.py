from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import APIModel


class DocumentRead(APIModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    original_file_name: str
    mime_type: str
    file_size: int
    page_count: int | None
    status: str
    processing_error: str | None
    uploaded_at: datetime
    processed_at: datetime | None
    updated_at: datetime


class DocumentUploadItem(APIModel):
    id: uuid.UUID
    original_file_name: str
    status: str


class UploadResponse(BaseModel):
    documents: list[DocumentUploadItem]


class ProcessDocumentRequest(BaseModel):
    force_reprocess: bool = False
