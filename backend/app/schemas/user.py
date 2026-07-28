from __future__ import annotations

import uuid
from datetime import datetime

from app.schemas.common import APIModel


class UserRead(APIModel):
    id: uuid.UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
