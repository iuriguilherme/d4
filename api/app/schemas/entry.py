import uuid
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel

from api.app.models.entry import EntryType, ReviewStatus


class EntryCreate(BaseModel):
    id: Optional[uuid.UUID] = None
    type: EntryType = EntryType.note
    content: str = ""
    content_rich: Optional[dict] = None
    entry_date: Optional[date] = None
    attributes: dict = {}
    tags: list[str] = []
    parent_id: Optional[uuid.UUID] = None
    review_status: Optional[ReviewStatus] = None


class EntryUpdate(BaseModel):
    type: Optional[EntryType] = None
    content: Optional[str] = None
    content_rich: Optional[dict] = None
    entry_date: Optional[date] = None
    attributes: Optional[dict] = None
    tags: Optional[list[str]] = None
    review_status: Optional[ReviewStatus] = None


class EntryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: EntryType
    content: str
    content_rich: Optional[dict]
    entry_date: date
    attributes: dict
    tags: list
    parent_id: Optional[uuid.UUID]
    review_status: Optional[ReviewStatus]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    model_config = {"from_attributes": True}


class EntryListResponse(BaseModel):
    items: list[EntryResponse]
    total: int
    page: int
    per_page: int
