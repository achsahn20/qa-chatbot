from __future__ import annotations

from pydantic import BaseModel


class DashboardTotals(BaseModel):
    total_users: int
    total_documents: int
    ready_documents: int
    processing_documents: int
    failed_documents: int
    total_sessions: int
    total_messages: int


class DashboardResponse(BaseModel):
    totals: DashboardTotals
    latest_activity: list[dict]


class AnalyticsResponse(BaseModel):
    uploads: list[dict]
    questions: list[dict]
    summary: dict
