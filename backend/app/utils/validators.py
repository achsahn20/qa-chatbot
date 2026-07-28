from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import get_settings


def validate_pdf_upload(upload_file: UploadFile, file_size: int) -> None:
    settings = get_settings()
    suffix = Path(upload_file.filename or "").suffix.lower()
    if suffix != ".pdf":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF files are supported.")
    if upload_file.content_type not in {"application/pdf", "application/octet-stream", None}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type.")
    if file_size > settings.max_upload_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds upload limit.")
