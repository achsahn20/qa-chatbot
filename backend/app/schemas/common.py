from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(APIModel):
    message: str


T = TypeVar("T")


class PaginatedResponse(APIModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    timestamp: datetime | None = None
