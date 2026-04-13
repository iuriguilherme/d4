import uuid
import logging
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.app.models.behavior import BehaviorEvent, Session as UserSession

logger = logging.getLogger(__name__)


async def close_session(
    db: AsyncSession,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    started_at: datetime,
) -> None:
    """Aggregate BehaviorEvents for this session into a Session record."""
    try:
        result = await db.execute(
            select(BehaviorEvent)
            .where(BehaviorEvent.session_id == session_id)
            .where(BehaviorEvent.user_id == user_id)
        )
        events = result.scalars().all()

        features_used = list({e.event_type for e in events if e.event_type.startswith("feature_")})
        entry_count = sum(1 for e in events if e.event_type == "entry_created")
        word_count = sum(e.event_data.get("word_count", 0) for e in events)
        ended_at = datetime.now(UTC)
        duration = int((ended_at - started_at).total_seconds())

        sess = UserSession(
            id=session_id,
            user_id=user_id,
            started_at=started_at,
            ended_at=ended_at,
            duration_seconds=duration,
            entry_count=entry_count,
            word_count=word_count,
            features_used=features_used,
        )
        db.add(sess)
        await db.commit()
    except Exception as exc:
        logger.error("Session close failed: %s session=%s", exc, session_id)
