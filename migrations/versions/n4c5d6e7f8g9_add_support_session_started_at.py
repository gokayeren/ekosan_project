"""add support session start timestamp

Revision ID: n4c5d6e7f8g9
Revises: m3b4c5d6e7f8
"""
from alembic import op
import sqlalchemy as sa

revision = 'n4c5d6e7f8g9'
down_revision = 'm3b4c5d6e7f8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('support_conversations', sa.Column('session_started_at', sa.DateTime(), nullable=True))
    op.execute('UPDATE support_conversations SET session_started_at = created_at WHERE session_started_at IS NULL')


def downgrade():
    op.drop_column('support_conversations', 'session_started_at')
