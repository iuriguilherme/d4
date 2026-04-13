import uuid
from datetime import date, datetime, UTC

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.app.core.database import get_db, AsyncSessionLocal
from api.app.dependencies.auth import get_current_user
from api.app.dependencies.session import get_session_id
from api.app.services.behavior import emit_event


async def _emit(user_id, event_type, data, session_id):
    async with AsyncSessionLocal() as bg_db:
        await emit_event(bg_db, user_id, event_type, data, session_id)
from api.app.models.habit import Habit
from api.app.models.entry import Entry, EntryType
from api.app.models.user import User
from api.app.schemas.habit import HabitCreate, HabitResponse, HabitCheckinResponse
from api.app.services.habit_streak import compute_streak

router = APIRouter(prefix="/api/v1/habits", tags=["habits"])

MAX_HABITS = 5


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    body: HabitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count_result = await db.execute(
        select(func.count())
        .select_from(Habit)
        .where(Habit.user_id == current_user.id)
        .where(Habit.archived_at.is_(None))
    )
    count = count_result.scalar()
    if count >= MAX_HABITS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum of {MAX_HABITS} active habits allowed",
        )

    habit = Habit(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        color=body.color,
        icon=body.icon,
        target_value=body.target_value,
        unit=body.unit,
    )
    db.add(habit)
    await db.commit()
    await db.refresh(habit)

    habit_dict = {c.key: getattr(habit, c.key) for c in habit.__table__.columns}
    habit_dict["streak"] = 0
    return HabitResponse(**habit_dict)


@router.get("", response_model=list[HabitResponse])
async def list_habits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Habit)
        .where(Habit.user_id == current_user.id)
        .where(Habit.archived_at.is_(None))
        .order_by(Habit.created_at)
    )
    habits = result.scalars().all()

    response = []
    for habit in habits:
        streak = await compute_streak(str(habit.id), current_user.id, db)
        habit_dict = {c.key: getattr(habit, c.key) for c in habit.__table__.columns}
        habit_dict["streak"] = streak
        response.append(HabitResponse(**habit_dict))
    return response


@router.post("/{habit_id}/checkin", response_model=HabitCheckinResponse)
async def checkin_habit(
    habit_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_id: uuid.UUID | None = Depends(get_session_id),
):
    # Verify habit exists and belongs to user
    result = await db.execute(
        select(Habit)
        .where(Habit.id == habit_id)
        .where(Habit.user_id == current_user.id)
        .where(Habit.archived_at.is_(None))
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")

    today = date.today()

    # Idempotent: return existing check-in if already done today
    existing = await db.execute(
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .where(Entry.type == EntryType.habit_checkin)
        .where(Entry.entry_date == today)
        .where(Entry.deleted_at.is_(None))
        .where(Entry.attributes["habit_id"].astext == str(habit_id))
    )
    existing_entry = existing.scalar_one_or_none()

    if existing_entry:
        streak = await compute_streak(str(habit_id), current_user.id, db)
        return HabitCheckinResponse(
            entry_id=existing_entry.id,
            habit_id=habit_id,
            streak=streak,
            entry_date=str(today),
        )

    entry = Entry(
        user_id=current_user.id,
        type=EntryType.habit_checkin,
        content=f"Checked in: {habit.name}",
        entry_date=today,
        attributes={"habit_id": str(habit_id), "value": 1, "target": habit.target_value},
    )
    db.add(entry)
    await db.commit()

    streak = await compute_streak(str(habit_id), current_user.id, db)
    background_tasks.add_task(
        _emit,
        current_user.id,
        "habit_checked",
        {"habit_id": str(habit_id), "streak_at_time": streak},
        session_id,
    )
    return HabitCheckinResponse(
        entry_id=entry.id,
        habit_id=habit_id,
        streak=streak,
        entry_date=str(today),
    )


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Habit)
        .where(Habit.id == habit_id)
        .where(Habit.user_id == current_user.id)
        .where(Habit.archived_at.is_(None))
    )
    habit = result.scalar_one_or_none()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    habit.archived_at = datetime.now(UTC)
    await db.commit()
