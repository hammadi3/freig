"""empty message

Revision ID: 42642243bde9
Revises: a08ecb20f6f6
Create Date: 2020-08-06 12:35:57.400153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42642243bde9'
down_revision = 'a08ecb20f6f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('freigabe', sa.Column('Freigabeart', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('freigabe', 'Freigabeart')
    # ### end Alembic commands ###
