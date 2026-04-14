import logging
import uuid
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession

from api.app.models.behavior import BehaviorEvent

logger = logging.getLogger(__name__)


async def emit_event(
    db: AsyncSession,
    user_id: uuid.UUID,
    event_type: str,
    event_data: dict,
    session_id: uuid.UUID | None = None,
) -> None:
    """
    Write a BehaviorEvent. Fire-and-forget — called from BackgroundTasks.
    Never raises; logs exceptions instead.
    """
    try:
        event = BehaviorEvent(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            session_id=session_id,
            occurred_at=datetime.now(UTC),
        )
        db.add(event)
        await db.commit()
    except Exception as exc:
        logger.error("BehaviorEvent write failed: %s event=%s user=%s", exc, event_type, user_id)
