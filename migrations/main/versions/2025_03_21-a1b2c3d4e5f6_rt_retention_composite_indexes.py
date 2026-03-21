"""Composite indexes for realtime retention and DISTINCT-friendly lookups

Revision ID: a1b2c3d4e5f6
Revises: f8b40d24637e
Create Date: 2025-03-21

Replaces single-column created_at indexes on rt_stop_time and rt_trip with
(dataset, created_at) for DELETE ... WHERE dataset = ? AND created_at < ?.
Adds the same pattern on rt_vehicle for retention deletes.
"""

from collections.abc import Sequence

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "f8b40d24637e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_rt_stop_time_created_at", table_name="rt_stop_time")
    op.drop_index("ix_rt_trip_created_at", table_name="rt_trip")
    op.create_index(
        "ix_rt_stop_time_dataset_created_at",
        "rt_stop_time",
        ["dataset", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_rt_trip_dataset_created_at",
        "rt_trip",
        ["dataset", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_rt_vehicle_dataset_created_at",
        "rt_vehicle",
        ["dataset", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_rt_vehicle_dataset_created_at", table_name="rt_vehicle")
    op.drop_index("ix_rt_trip_dataset_created_at", table_name="rt_trip")
    op.drop_index("ix_rt_stop_time_dataset_created_at", table_name="rt_stop_time")
    op.create_index("ix_rt_stop_time_created_at", "rt_stop_time", ["created_at"], unique=False)
    op.create_index("ix_rt_trip_created_at", "rt_trip", ["created_at"], unique=False)
