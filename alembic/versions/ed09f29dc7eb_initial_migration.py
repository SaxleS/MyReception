"""Initial migration

Revision ID: ed09f29dc7eb
Revises: 556367263336
Create Date: 2024-10-13 01:17:07.234614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed09f29dc7eb'
down_revision: Union[str, None] = '556367263336'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('created_by', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'tasks', 'users', ['created_by'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'created_by')
    # ### end Alembic commands ###