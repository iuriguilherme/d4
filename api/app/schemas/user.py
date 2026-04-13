import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel


class UserUpdate(BaseModel):
    timezone: Optional[str] = None
    preferences: Optional[dict[str, Any]] = None


class UserMeResponse(BaseModel):
    id: uuid.UUID
    email: str
    timezone: str
    preferences: dict
    created_at: datetime

    model_config = {"from_attributes": True}
