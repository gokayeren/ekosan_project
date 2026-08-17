"""add slider item video url

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-08-17 08:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'g7b8c9d0e1f2'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('slider_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('video_url', sa.String(length=500), nullable=True))


def downgrade():
    with op.batch_alter_table('slider_items', schema=None) as batch_op:
        batch_op.drop_column('video_url')
