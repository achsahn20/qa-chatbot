from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_admin_user
from app.database.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.admin import AnalyticsResponse, DashboardResponse, DashboardTotals
from app.schemas.common import PaginatedResponse
from app.schemas.document import DocumentRead
from app.schemas.user import UserRead
from app.services.admin_service import build_analytics, get_dashboard_data


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    data = get_dashboard_data(db)
    return DashboardResponse(totals=DashboardTotals(**data["totals"]), latest_activity=data["latest_activity"])


@router.get("/users", response_model=PaginatedResponse[UserRead])
def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[UserRead]:
    query = select(User).order_by(User.created_at.desc())
    items = db.scalars(query.offset((page - 1) * limit).limit(limit)).all()
    total = len(db.scalars(select(User)).all())
    return PaginatedResponse(items=[UserRead.model_validate(item) for item in items], total=total, page=page, limit=limit)


@router.get("/documents", response_model=PaginatedResponse[DocumentRead])
def list_documents(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[DocumentRead]:
    query = select(Document).order_by(Document.uploaded_at.desc())
    items = db.scalars(query.offset((page - 1) * limit).limit(limit)).all()
    total = len(db.scalars(select(Document)).all())
    return PaginatedResponse(items=[DocumentRead.model_validate(item) for item in items], total=total, page=page, limit=limit)


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(
    range: str = Query(default="30d"),
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> AnalyticsResponse:
    days = 30
    if range == "7d":
        days = 7
    elif range == "90d":
        days = 90
    data = build_analytics(db, days)
    return AnalyticsResponse(**data)
