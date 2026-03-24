"""event composite event_type created_at index

Revision ID: 08fc2a5bcb3e
Revises: a25dd6dfdbac
Create Date: 2026-03-24 23:34:05.427444

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "08fc2a5bcb3e"
down_revision: str | None = "a25dd6dfdbac"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_event_event_type"), table_name="event")
    op.create_index(
        "ix_event_event_type_created_at",
        "event",
        ["event_type", sa.literal_column("created_at DESC")],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_event_event_type_created_at", table_name="event")
    op.create_index(op.f("ix_event_event_type"), "event", ["event_type"], unique=False)
