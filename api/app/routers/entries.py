import uuid
from datetime import date, datetime, UTC
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.app.core.database import get_db, AsyncSessionLocal
from api.app.dependencies.auth import get_current_user
from api.app.dependencies.session import get_session_id
from api.app.models.entry import Entry, EntryType, ReviewStatus
from api.app.models.user import User
from api.app.schemas.entry import EntryCreate, EntryUpdate, EntryResponse, EntryListResponse
from api.app.services.behavior import emit_event

router = APIRouter(prefix="/api/v1/entries", tags=["entries"])


async def _emit(user_id: uuid.UUID, event_type: str, data: dict, session_id: uuid.UUID | None):
    async with AsyncSessionLocal() as bg_db:
        await emit_event(bg_db, user_id, event_type, data, session_id)


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    body: EntryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_id: uuid.UUID | None = Depends(get_session_id),
):
    entry_id = body.id or uuid.uuid4()

    # Check for UUID collision
    if body.id:
        existing = await db.execute(select(Entry).where(Entry.id == entry_id))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Entry ID already exists")

    entry_date = body.entry_date or date.today()
    review_status = body.review_status
    if body.type == EntryType.note and review_status is None:
        review_status = ReviewStatus.pending

    entry = Entry(
        id=entry_id,
        user_id=current_user.id,
        type=body.type,
        content=body.content,
        content_rich=body.content_rich,
        entry_date=entry_date,
        attributes=body.attributes,
        tags=body.tags,
        parent_id=body.parent_id,
        review_status=review_status,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    word_count = len(body.content.split()) if body.content else 0
    background_tasks.add_task(
        _emit,
        current_user.id,
        "entry_created",
        {
            "entry_type": body.type.value if body.type else "note",
            "word_count": word_count,
            "entry_date": str(entry_date),
            "hour_of_day": datetime.now(UTC).hour,
        },
        session_id,
    )
    return entry


@router.get("", response_model=EntryListResponse)
async def list_entries(
    entry_date: Optional[date] = Query(None),
    type: Optional[EntryType] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .where(Entry.deleted_at.is_(None))
    )
    if entry_date:
        query = query.where(Entry.entry_date == entry_date)
    else:
        query = query.where(Entry.entry_date == date.today())
    if type:
        query = query.where(Entry.type == type)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.order_by(Entry.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()

    return EntryListResponse(items=list(items), total=total, page=page, per_page=per_page)


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Entry)
        .where(Entry.id == entry_id)
        .where(Entry.user_id == current_user.id)
        .where(Entry.deleted_at.is_(None))
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return entry


@router.patch("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: uuid.UUID,
    body: EntryUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_id: uuid.UUID | None = Depends(get_session_id),
):
    result = await db.execute(
        select(Entry)
        .where(Entry.id == entry_id)
        .where(Entry.user_id == current_user.id)
        .where(Entry.deleted_at.is_(None))
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)

    # If type changed to non-note from note, mark as reviewed
    if body.type is not None and body.type != EntryType.note:
        if entry.review_status == ReviewStatus.pending:
            entry.review_status = ReviewStatus.reviewed

    # Detect task completion
    completed = (
        body.attributes is not None and body.attributes.get("completed") is True
        or (body.attributes and body.attributes.get("completed"))
    )

    entry.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(entry)

    if completed and entry.type == EntryType.task:
        background_tasks.add_task(
            _emit,
            current_user.id,
            "task_completed",
            {"entry_id": str(entry_id)},
            session_id,
        )

    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Entry)
        .where(Entry.id == entry_id)
        .where(Entry.user_id == current_user.id)
        .where(Entry.deleted_at.is_(None))
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    entry.deleted_at = datetime.now(UTC)
    await db.commit()
