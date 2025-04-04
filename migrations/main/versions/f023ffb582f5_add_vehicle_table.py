"""Add Vehicle table

Revision ID: f023ffb582f5
Revises: 9411c450cbca
Create Date: 2024-01-22 00:15:20.937614

"""

from collections.abc import Sequence

import advanced_alchemy.types.datetime
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f023ffb582f5"
down_revision: str | None = "9411c450cbca"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "rt_vehicle",
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("trip_id", sa.String(length=1000), nullable=False),
        sa.Column("time_of_update", sa.DateTime(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("dataset", sa.String(length=80), nullable=False),
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
        sa.Column("updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trip.id"], name=op.f("fk_rt_vehicle_trip_id_trip")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rt_vehicle")),
    )
    op.create_index(op.f("ix_rt_vehicle_trip_id"), "rt_vehicle", ["trip_id"], unique=False)
    op.drop_table("rt_stop")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "rt_stop",
        sa.Column("id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_rt_stop"),
    )
    op.drop_index(op.f("ix_rt_vehicle_trip_id"), table_name="rt_vehicle")
    op.drop_table("rt_vehicle")
    # ### end Alembic commands ###
