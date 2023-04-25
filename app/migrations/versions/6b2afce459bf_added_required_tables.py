"""Added required tables

Revision ID: 6b2afce459bf
Revises: 1818566eeba3
Create Date: 2023-04-04 17:59:07.295413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6b2afce459bf'
down_revision = '1818566eeba3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=256), nullable=False),
    sa.Column('refresh_token', sa.String(length=256), nullable=False),
    sa.Column('expires', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tokens_refresh_token'), 'tokens', ['refresh_token'], unique=True)
    op.create_index(op.f('ix_tokens_token'), 'tokens', ['token'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tokens_token'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_refresh_token'), table_name='tokens')
    op.drop_table('tokens')
    # ### end Alembic commands ###
