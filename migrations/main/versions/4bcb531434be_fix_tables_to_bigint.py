"""fix tables to bigint

Revision ID: 4bcb531434be
Revises: 7ed310cb14c2
Create Date: 2024-03-08 00:57:30.040812

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4bcb531434be"
down_revision: str | None = "7ed310cb14c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "calendar_date",
        "id",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "event",
        "id",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "stop_time",
        "id",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        existing_nullable=False,
        autoincrement=True,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "stop_time",
        "id",
        existing_type=sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        type_=sa.INTEGER(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "event",
        "id",
        existing_type=sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        type_=sa.INTEGER(),
        existing_nullable=False,
        autoincrement=True,
    )
    op.alter_column(
        "calendar_date",
        "id",
        existing_type=sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
        type_=sa.INTEGER(),
        existing_nullable=False,
        autoincrement=True,
    )
    # ### end Alembic commands ###
