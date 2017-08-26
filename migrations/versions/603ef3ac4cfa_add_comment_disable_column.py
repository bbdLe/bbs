"""add comment disable column

Revision ID: 603ef3ac4cfa
Revises: 62927cb9329c
Create Date: 2017-08-26 12:18:19.590551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '603ef3ac4cfa'
down_revision = '62927cb9329c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('disable', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comments', 'disable')
    # ### end Alembic commands ###
