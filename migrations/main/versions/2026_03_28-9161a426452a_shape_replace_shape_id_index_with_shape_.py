"""shape replace shape_id index with shape_id sequence

Revision ID: 9161a426452a
Revises: 08fc2a5bcb3e
Create Date: 2026-03-28 12:58:23.155627

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9161a426452a"
down_revision: str | None = "08fc2a5bcb3e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_shape_shape_id"), table_name="shape")
    op.create_index(
        op.f("ix_shape_shape_id_sequence"),
        "shape",
        ["shape_id", "sequence"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_shape_shape_id_sequence"), table_name="shape")
    op.create_index(op.f("ix_shape_shape_id"), "shape", ["shape_id"], unique=False)
