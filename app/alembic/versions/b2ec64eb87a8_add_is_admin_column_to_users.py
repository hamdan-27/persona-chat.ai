"""add is_admin column to users

Revision ID: b2ec64eb87a8
Revises: 
Create Date: 2024-05-01 21:54:54.919634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2ec64eb87a8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('is_admin', sa.Boolean(), nullable=True, default=False))


def downgrade() -> None:
    op.drop_column('user', 'is_admin')
