from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.user import User


def get_dashboard_data(db: Session) -> dict:
    totals = {
        "total_users": db.scalar(select(func.count()).select_from(User)) or 0,
        "total_documents": db.scalar(select(func.count()).select_from(Document)) or 0,
        "ready_documents": db.scalar(select(func.count()).select_from(Document).where(Document.status == "ready")) or 0,
        "processing_documents": db.scalar(select(func.count()).select_from(Document).where(Document.status == "processing")) or 0,
        "failed_documents": db.scalar(select(func.count()).select_from(Document).where(Document.status == "failed")) or 0,
        "total_sessions": db.scalar(select(func.count()).select_from(ChatSession)) or 0,
        "total_messages": db.scalar(select(func.count()).select_from(ChatMessage)) or 0,
    }

    latest_documents = db.scalars(select(Document).order_by(Document.uploaded_at.desc()).limit(5)).all()
    latest_activity = [
        {
            "type": "document_upload",
            "file_name": doc.original_file_name,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at.isoformat(),
        }
        for doc in latest_documents
    ]

    return {"totals": totals, "latest_activity": latest_activity}


def build_analytics(db: Session, days: int) -> dict:
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    upload_map: dict[str, int] = defaultdict(int)
    message_map: dict[str, int] = defaultdict(int)

    uploads = db.scalars(select(Document).where(Document.uploaded_at >= start_date)).all()
    messages = db.scalars(
        select(ChatMessage).where(ChatMessage.created_at >= start_date, ChatMessage.role == "assistant")
    ).all()

    for document in uploads:
        key = document.uploaded_at.date().isoformat()
        upload_map[key] += 1

    total_latency = 0
    latency_count = 0
    for message in messages:
        key = message.created_at.date().isoformat()
        message_map[key] += 1
        if message.latency_ms:
            total_latency += message.latency_ms
            latency_count += 1

    return {
        "uploads": [{"date": key, "count": upload_map[key]} for key in sorted(upload_map)],
        "questions": [{"date": key, "count": message_map[key]} for key in sorted(message_map)],
        "summary": {
            "range_days": days,
            "documents_uploaded": len(uploads),
            "answers_generated": len(messages),
            "average_latency_ms": round(total_latency / latency_count, 2) if latency_count else 0,
        },
    }
