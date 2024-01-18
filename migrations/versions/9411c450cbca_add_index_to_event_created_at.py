"""Add index to event created at

Revision ID: 9411c450cbca
Revises: 9bd2faaea729
Create Date: 2024-01-13 16:11:30.289689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9411c450cbca'
down_revision: Union[str, None] = '9bd2faaea729'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_event_created_at', 'event', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_event_created_at', table_name='event')
    # ### end Alembic commands ###