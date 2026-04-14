import uuid
from datetime import datetime, date, UTC
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Date, JSON, ForeignKey, Enum, Text, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from api.app.core.database import Base


class EntryType(str, PyEnum):
    task = "task"
    note = "note"
    event = "event"
    habit_checkin = "habit_checkin"
    goal = "goal"
    time_block = "time_block"
    review = "review"


class ReviewStatus(str, PyEnum):
    pending = "pending"
    reviewed = "reviewed"
    dismissed = "dismissed"


class Entry(Base):
    __tablename__ = "entries"
    __table_args__ = (
        Index("ix_entries_attributes_gin", "attributes", postgresql_using="gin"),
        Index("ix_entries_user_date", "user_id", "entry_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[EntryType] = mapped_column(
        Enum(EntryType, name="entry_type"), nullable=False, default=EntryType.note
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_rich: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    attributes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entries.id", ondelete="SET NULL"), nullable=True
    )
    review_status: Mapped[ReviewStatus | None] = mapped_column(
        Enum(ReviewStatus, name="review_status"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
