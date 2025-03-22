"""add_auth_swipes

Revision ID: e30165d39688
Revises: 869e0da156b7
Create Date: 2025-03-16 09:57:57.778746

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e30165d39688'
down_revision: Union[str, None] = '869e0da156b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('refresh_token', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('brackets',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('session_id', sa.UUID(), nullable=False),
    sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('results', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('bracket')
    op.drop_constraint('board_cards_card_id_fkey', 'board_cards', type_='foreignkey')
    op.drop_constraint('board_cards_board_id_fkey', 'board_cards', type_='foreignkey')
    op.create_foreign_key(None, 'board_cards', 'boards', ['board_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'board_cards', 'cards', ['card_id'], ['id'], ondelete='CASCADE')
    op.add_column('boards', sa.Column('owner_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'boards', 'users', ['owner_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'boards', type_='foreignkey')
    op.drop_column('boards', 'owner_id')
    op.drop_constraint(None, 'board_cards', type_='foreignkey')
    op.drop_constraint(None, 'board_cards', type_='foreignkey')
    op.create_foreign_key('board_cards_board_id_fkey', 'board_cards', 'boards', ['board_id'], ['id'])
    op.create_foreign_key('board_cards_card_id_fkey', 'board_cards', 'cards', ['card_id'], ['id'])
    op.create_table('bracket',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('session_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('structure', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('results', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], name='bracket_session_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='bracket_pkey')
    )
    op.drop_table('brackets')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
