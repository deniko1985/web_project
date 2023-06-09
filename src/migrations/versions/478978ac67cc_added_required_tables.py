"""Added required tables

Revision ID: 478978ac67cc
Revises: 13daf22d20bf
Create Date: 2023-04-10 09:21:39.837478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '478978ac67cc'
down_revision = '13daf22d20bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_tokens_refresh_token', table_name='tokens')
    op.drop_column('tokens', 'refresh_token')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tokens', sa.Column('refresh_token', sa.VARCHAR(length=256), autoincrement=False, nullable=False))
    op.create_index('ix_tokens_refresh_token', 'tokens', ['refresh_token'], unique=False)
    # ### end Alembic commands ###
