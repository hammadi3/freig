"""empty message

Revision ID: a08ecb20f6f6
Revises: d6c9996b7d60
Create Date: 2020-08-06 12:35:20.810940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a08ecb20f6f6'
down_revision = 'd6c9996b7d60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('freigabe', sa.Column('Auslaufdatum', sa.DateTime(timezone=True), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('freigabe', 'Auslaufdatum')
    # ### end Alembic commands ###
