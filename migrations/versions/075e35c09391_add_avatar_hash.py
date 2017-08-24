"""add avatar_hash

Revision ID: 075e35c09391
Revises: 593f65c4ed0a
Create Date: 2017-08-23 11:50:33.214322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '075e35c09391'
down_revision = '593f65c4ed0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar_hash', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar_hash')
    # ### end Alembic commands ###