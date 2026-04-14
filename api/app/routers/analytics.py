import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.app.core.database import get_db
from api.app.dependencies.auth import get_current_user
from api.app.models.behavior import BehaviorEvent
from api.app.models.user import User
from pydantic import BaseModel
from datetime import datetime


class BehaviorEventResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    event_data: dict
    session_id: Optional[uuid.UUID]
    occurred_at: datetime

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/behavior", response_model=list[BehaviorEventResponse])
async def list_behavior_events(
    session_id: Optional[uuid.UUID] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(BehaviorEvent)
        .where(BehaviorEvent.user_id == current_user.id)
        .order_by(BehaviorEvent.occurred_at.desc())
    )
    if session_id:
        query = query.where(BehaviorEvent.session_id == session_id)

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()
