"""index trip stop route dataset

Revision ID: a25dd6dfdbac
Revises: a1b2c3d4e5f6
Create Date: 2026-03-22 14:56:12.341103

"""

from collections.abc import Sequence

from alembic import op

revision: str = "a25dd6dfdbac"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(op.f("ix_route_dataset"), "route", ["dataset"], unique=False)
    op.create_index(op.f("ix_stop_dataset"), "stop", ["dataset"], unique=False)
    op.create_index(op.f("ix_trip_dataset"), "trip", ["dataset"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trip_dataset"), table_name="trip")
    op.drop_index(op.f("ix_stop_dataset"), table_name="stop")
    op.drop_index(op.f("ix_route_dataset"), table_name="route")
