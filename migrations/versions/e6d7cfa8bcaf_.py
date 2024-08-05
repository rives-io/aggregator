"""empty message

Revision ID: e6d7cfa8bcaf
Revises: 84a62aef8e07
Create Date: 2024-07-26 08:49:28.109735

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'e6d7cfa8bcaf'
down_revision = '84a62aef8e07'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('awardedconsoleachievement', sa.Column('tape_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.alter_column('awardedconsoleachievement', 'points',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'awardedconsoleachievement', 'tape', ['tape_id'], ['id'])
    op.alter_column('consoleachievement', 'points',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('consoleachievement', 'points',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_constraint(None, 'awardedconsoleachievement', type_='foreignkey')
    op.alter_column('awardedconsoleachievement', 'points',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('awardedconsoleachievement', 'tape_id')
    # ### end Alembic commands ###