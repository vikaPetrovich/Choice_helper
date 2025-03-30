"""add is_completed to session_participants

Revision ID: a3a7612a981a
Revises: 6461519d4e44
Create Date: 2025-03-30 15:13:36.643073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3a7612a981a'
down_revision: Union[str, None] = '6461519d4e44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('session_participants', sa.Column('is_completed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('session_participants', 'is_completed')
    # ### end Alembic commands ###
