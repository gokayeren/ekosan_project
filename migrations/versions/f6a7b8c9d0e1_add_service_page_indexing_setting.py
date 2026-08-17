"""add service page indexing setting

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-17 06:30:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'seo_index_service_pages', sa.Boolean(), nullable=False, server_default=sa.true()
        ))


def downgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.drop_column('seo_index_service_pages')
