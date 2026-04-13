import uuid
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.app.models.user import User
from api.app.models.entry import Entry
from api.app.models.habit import Habit
from api.app.models.tag import Tag


def _serialize(obj) -> dict:
    """Convert SQLAlchemy model to JSON-serializable dict."""
    result = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        elif isinstance(val, uuid.UUID):
            val = str(val)
        result[col.name] = val
    return result


async def build_export(user: User, db: AsyncSession) -> dict:
    entries_result = await db.execute(
        select(Entry)
        .where(Entry.user_id == user.id)
        .where(Entry.deleted_at.is_(None))
        .order_by(Entry.entry_date.desc(), Entry.created_at.desc())
    )
    entries = entries_result.scalars().all()

    habits_result = await db.execute(
        select(Habit)
        .where(Habit.user_id == user.id)
        .where(Habit.archived_at.is_(None))
        .order_by(Habit.created_at)
    )
    habits = habits_result.scalars().all()

    tags_result = await db.execute(
        select(Tag)
        .where(Tag.user_id == user.id)
        .order_by(Tag.name)
    )
    tags = tags_result.scalars().all()

    return {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "timezone": user.timezone,
            "created_at": user.created_at.isoformat(),
        },
        "entries": [_serialize(e) for e in entries],
        "habits": [_serialize(h) for h in habits],
        "tags": [_serialize(t) for t in tags],
    }
