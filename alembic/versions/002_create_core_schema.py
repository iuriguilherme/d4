"""create core schema: entries, habits, behavior_events, sessions, archetype_snapshots, tags

Revision ID: 002
Revises: 001
Create Date: 2026-04-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # entry_type enum
    op.execute("CREATE TYPE entry_type AS ENUM ('task','note','event','habit_checkin','goal','time_block','review')")
    op.execute("CREATE TYPE review_status AS ENUM ('pending','reviewed','dismissed')")

    op.create_table(
        "entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("task","note","event","habit_checkin","goal","time_block","review", name="entry_type"), nullable=False, server_default="note"),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("content_rich", JSON, nullable=True),
        sa.Column("entry_date", sa.Date, nullable=False),
        sa.Column("attributes", JSON, nullable=False, server_default="{}"),
        sa.Column("tags", JSON, nullable=False, server_default="[]"),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("review_status", sa.Enum("pending","reviewed","dismissed", name="review_status"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_entries_user_id", "entries", ["user_id"])
    op.create_index("ix_entries_user_date", "entries", ["user_id", "entry_date"])
    op.execute("CREATE INDEX ix_entries_attributes_gin ON entries USING gin (attributes)")

    op.create_table(
        "habits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("frequency", sa.String(32), nullable=False, server_default="daily"),
        sa.Column("target_value", sa.Integer, nullable=False, server_default="1"),
        sa.Column("unit", sa.String(64), nullable=False, server_default=""),
        sa.Column("color", sa.String(16), nullable=False, server_default="#6366f1"),
        sa.Column("icon", sa.String(64), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_habits_user_id", "habits", ["user_id"])

    # BehaviorEvent: no FK constraints intentionally
    op.create_table(
        "behavior_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("event_data", JSON, nullable=False, server_default="{}"),
        sa.Column("session_id", UUID(as_uuid=True), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_behavior_events_user_id", "behavior_events", ["user_id"])
    op.create_index("ix_behavior_events_event_type", "behavior_events", ["event_type"])
    op.create_index("ix_behavior_events_session_id", "behavior_events", ["session_id"])
    op.create_index("ix_behavior_events_occurred_at", "behavior_events", ["occurred_at"])

    op.create_table(
        "sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("entry_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("word_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("features_used", JSON, nullable=False, server_default="[]"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    op.create_table(
        "archetype_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("scores", JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_archetype_snapshots_user_id", "archetype_snapshots", ["user_id"])

    op.create_table(
        "tags",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("color", sa.String(16), nullable=False, server_default="#6366f1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "name", name="uq_tags_user_name"),
    )
    op.create_index("ix_tags_user_id", "tags", ["user_id"])


def downgrade() -> None:
    op.drop_table("tags")
    op.drop_table("archetype_snapshots")
    op.drop_table("sessions")
    op.drop_table("behavior_events")
    op.drop_table("habits")
    op.drop_index("ix_entries_attributes_gin", table_name="entries")
    op.drop_index("ix_entries_user_date", table_name="entries")
    op.drop_index("ix_entries_user_id", table_name="entries")
    op.drop_table("entries")
    op.execute("DROP TYPE IF EXISTS review_status")
    op.execute("DROP TYPE IF EXISTS entry_type")
