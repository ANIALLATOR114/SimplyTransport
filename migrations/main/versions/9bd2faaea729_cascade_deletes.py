"""cascade deletes

Revision ID: 9bd2faaea729
Revises: b6e8cde14fdb
Create Date: 2023-12-17 17:03:58.215262

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9bd2faaea729"
down_revision: str | None = "b6e8cde14fdb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("rt_stop")
    op.drop_constraint("fk_rt_stop_time_trip_id_trip", "rt_stop_time", type_="foreignkey")
    op.drop_constraint("fk_rt_stop_time_stop_id_stop", "rt_stop_time", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_rt_stop_time_stop_id_stop"), "rt_stop_time", "stop", ["stop_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        op.f("fk_rt_stop_time_trip_id_trip"), "rt_stop_time", "trip", ["trip_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("fk_rt_trip_trip_id_trip", "rt_trip", type_="foreignkey")
    op.drop_constraint("fk_rt_trip_route_id_route", "rt_trip", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_rt_trip_trip_id_trip"), "rt_trip", "trip", ["trip_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        op.f("fk_rt_trip_route_id_route"), "rt_trip", "route", ["route_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("fk_rt_trip_route_id_route"), "rt_trip", type_="foreignkey")
    op.drop_constraint(op.f("fk_rt_trip_trip_id_trip"), "rt_trip", type_="foreignkey")
    op.create_foreign_key("fk_rt_trip_route_id_route", "rt_trip", "route", ["route_id"], ["id"])
    op.create_foreign_key("fk_rt_trip_trip_id_trip", "rt_trip", "trip", ["trip_id"], ["id"])
    op.drop_constraint(op.f("fk_rt_stop_time_trip_id_trip"), "rt_stop_time", type_="foreignkey")
    op.drop_constraint(op.f("fk_rt_stop_time_stop_id_stop"), "rt_stop_time", type_="foreignkey")
    op.create_foreign_key("fk_rt_stop_time_stop_id_stop", "rt_stop_time", "stop", ["stop_id"], ["id"])
    op.create_foreign_key("fk_rt_stop_time_trip_id_trip", "rt_stop_time", "trip", ["trip_id"], ["id"])
    op.create_table(
        "rt_stop",
        sa.Column("id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_rt_stop"),
    )
    # ### end Alembic commands ###
