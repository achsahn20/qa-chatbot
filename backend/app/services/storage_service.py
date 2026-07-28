from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import uuid

from fastapi import UploadFile

from app.config import get_settings


class LocalStorageService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def save_upload(self, upload_file: UploadFile, owner_id: str) -> dict:
        target_dir = self.settings.uploads_dir / owner_id
        target_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(upload_file.filename or "document.pdf").suffix or ".pdf"
        file_name = f"{uuid.uuid4()}{suffix}"
        target_path = target_dir / file_name

        hasher = hashlib.sha256()
        size = 0
        with target_path.open("wb") as buffer:
            upload_file.file.seek(0)
            while chunk := upload_file.file.read(1024 * 1024):
                size += len(chunk)
                hasher.update(chunk)
                buffer.write(chunk)
        upload_file.file.seek(0)

        return {
            "storage_key": str(target_path.relative_to(self.settings.uploads_dir.parent)),
            "absolute_path": str(target_path),
            "file_size": size,
            "sha256_hash": hasher.hexdigest(),
        }

    def get_absolute_path(self, storage_key: str) -> Path:
        return self.settings.uploads_dir.parent / storage_key

    def delete_file(self, storage_key: str) -> None:
        path = self.get_absolute_path(storage_key)
        if path.exists():
            path.unlink()

        parent = path.parent
        if parent.exists() and not any(parent.iterdir()):
            shutil.rmtree(parent, ignore_errors=True)
