"""add product detail toggle

Revision ID: h8c9d0e1f2a3
Revises: g7b8c9d0e1f2
Create Date: 2026-08-18 09:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'h8c9d0e1f2a3'
down_revision = 'g7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.add_column(sa.Column(
            'product_detail_enabled', sa.Boolean(), nullable=False, server_default=sa.false()
        ))


def downgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.drop_column('product_detail_enabled')
