"""adding fields for ts stop times

Revision ID: 56f6a9c93651
Revises: 1d1c9dc66800
Create Date: 2024-09-25 13:13:47.918281

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "56f6a9c93651"
down_revision: str | None = "1d1c9dc66800"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("ts_stop_times", sa.Column("stop_id", sa.String(length=1000), nullable=False))
    op.add_column("ts_stop_times", sa.Column("route_code", sa.String(length=1000), nullable=False))
    op.add_column("ts_stop_times", sa.Column("scheduled_time", sa.Time(), nullable=False))
    op.add_column("ts_stop_times", sa.Column("actual_time", sa.Time(), nullable=True))
    op.add_column("ts_stop_times", sa.Column("delay_in_seconds", sa.Integer(), nullable=False))
    op.create_index(op.f("ix_ts_stop_times_route_code"), "ts_stop_times", ["route_code"], unique=False)
    op.create_index(
        op.f("ix_ts_stop_times_scheduled_time"), "ts_stop_times", ["scheduled_time"], unique=False
    )
    op.create_index(op.f("ix_ts_stop_times_stop_id"), "ts_stop_times", ["stop_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_ts_stop_times_stop_id"), table_name="ts_stop_times")
    op.drop_index(op.f("ix_ts_stop_times_scheduled_time"), table_name="ts_stop_times")
    op.drop_index(op.f("ix_ts_stop_times_route_code"), table_name="ts_stop_times")
    op.drop_column("ts_stop_times", "delay_in_seconds")
    op.drop_column("ts_stop_times", "actual_time")
    op.drop_column("ts_stop_times", "scheduled_time")
    op.drop_column("ts_stop_times", "route_code")
    op.drop_column("ts_stop_times", "stop_id")
    # ### end Alembic commands ###
