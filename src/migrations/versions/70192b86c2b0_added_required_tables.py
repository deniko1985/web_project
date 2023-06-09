"""Added required tables

Revision ID: 70192b86c2b0
Revises: 95d48c5259db
Create Date: 2023-04-18 15:46:02.177048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70192b86c2b0'
down_revision = '95d48c5259db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('notes', sa.JSON(), nullable=True))
    op.drop_index('name_notes_gin', table_name='notes')
    op.drop_index('name_notes_gist', table_name='notes')
    op.drop_index('text_notes_gin', table_name='notes')
    op.drop_index('text_notes_gist', table_name='notes')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('text_notes_gist', 'notes', ['text_notes'], unique=False)
    op.create_index('text_notes_gin', 'notes', ['text_notes'], unique=False)
    op.create_index('name_notes_gist', 'notes', ['name_notes'], unique=False)
    op.create_index('name_notes_gin', 'notes', ['name_notes'], unique=False)
    op.drop_column('notes', 'notes')
    # ### end Alembic commands ###
