import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HabitCreate(BaseModel):
    name: str
    description: str = ""
    color: str = "#6366f1"
    icon: str = ""
    target_value: int = 1
    unit: str = ""


class HabitResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str
    frequency: str
    target_value: int
    unit: str
    color: str
    icon: str
    created_at: datetime
    archived_at: Optional[datetime]
    streak: int = 0

    model_config = {"from_attributes": True}


class HabitCheckinResponse(BaseModel):
    entry_id: uuid.UUID
    habit_id: uuid.UUID
    streak: int
    entry_date: str
