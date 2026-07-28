from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.config import get_settings
from app.database.session import SessionLocal
from app.rag.vector_store import get_vector_store


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    settings = get_settings()
    db_status = "ok"
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    vector_status = "ok"
    try:
        get_vector_store().stats()
    except Exception:
        vector_status = "error"

    return {
        "status": "ok" if db_status == "ok" and vector_status == "ok" else "degraded",
        "db": db_status,
        "vector_db": vector_status,
        "storage": "ok" if settings.uploads_dir.exists() else "error",
        "llm": settings.llm_provider,
    }
