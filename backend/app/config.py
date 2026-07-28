from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STORAGE_DIR = BACKEND_DIR / "storage"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Document Q&A Chatbot"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    database_url: str = f"sqlite:///{(DEFAULT_STORAGE_DIR / 'app.db').as_posix()}"
    uploads_dir: Path = DEFAULT_STORAGE_DIR / "uploads"
    chroma_persist_directory: Path = DEFAULT_STORAGE_DIR / "chroma"
    chroma_collection_name: str = "document_chunks"

    max_upload_size_mb: int = 20
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    embedding_provider: str = "hash"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 384
    openai_api_key: str = ""
    llm_provider: str = "fallback"
    llm_model: str = "gpt-4.1-mini"

    default_top_k: int = 8
    max_context_chunks: int = 6
    chunk_size_chars: int = 1800
    chunk_overlap_chars: int = 250
    similarity_threshold: float = 0.35

    seed_admin_email: str = "admin@example.com"
    seed_admin_password: str = "Admin123!"
    seed_admin_name: str = "Platform Admin"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_persist_directory.mkdir(parents=True, exist_ok=True)
    return settings
