"""add support message seen timestamp

Revision ID: k1f2a3b4c5d6
Revises: j0e1f2a3b4c5
"""
from alembic import op
import sqlalchemy as sa

revision = 'k1f2a3b4c5d6'
down_revision = 'j0e1f2a3b4c5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('support_messages', sa.Column('seen_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('support_messages', 'seen_at')
