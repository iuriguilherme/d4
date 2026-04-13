from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.app.models.entry import Entry, EntryType


async def compute_streak(habit_id: str, user_id, db: AsyncSession) -> int:
    """Walk back from today counting consecutive daily check-ins."""
    result = await db.execute(
        select(Entry.entry_date)
        .where(Entry.user_id == user_id)
        .where(Entry.type == EntryType.habit_checkin)
        .where(Entry.deleted_at.is_(None))
        .where(Entry.attributes["habit_id"].astext == habit_id)
        .order_by(Entry.entry_date.desc())
    )
    check_in_dates = {row[0] for row in result.all()}

    streak = 0
    current = date.today()
    while current in check_in_dates:
        streak += 1
        current = current - timedelta(days=1)
    return streak
