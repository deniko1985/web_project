"""Added required tables

Revision ID: bd6c4a20baf7
Revises: 91db622adab5
Create Date: 2023-04-12 10:27:01.997661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd6c4a20baf7'
down_revision = '91db622adab5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('favourites', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notes', 'favourites')
    # ### end Alembic commands ###
