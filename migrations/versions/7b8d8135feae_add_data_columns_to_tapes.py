"""Add data columns to tapes

Revision ID: 7b8d8135feae
Revises: 3741e36575e8
Create Date: 2025-03-21 14:43:25.370587

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '7b8d8135feae'
down_revision = '3741e36575e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tape', sa.Column('tape', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('tape', sa.Column('incard', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('tape', sa.Column('args', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('tape', sa.Column('entropy', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('tape', 'tape')
    op.drop_column('tape', 'incard')
    op.drop_column('tape', 'args')
    op.drop_column('tape', 'entropy')
