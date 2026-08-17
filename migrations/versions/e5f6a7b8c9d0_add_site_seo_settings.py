"""add site seo settings

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-08-17 06:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'seo_canonical_url', sa.String(length=255), nullable=False,
            server_default='https://ekosanmuhendislik.com'
        ))
        batch_op.add_column(sa.Column('seo_default_description', sa.String(length=320), nullable=True))
        batch_op.add_column(sa.Column(
            'seo_homepage_only', sa.Boolean(), nullable=False, server_default=sa.true()
        ))


def downgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.drop_column('seo_homepage_only')
        batch_op.drop_column('seo_default_description')
        batch_op.drop_column('seo_canonical_url')
