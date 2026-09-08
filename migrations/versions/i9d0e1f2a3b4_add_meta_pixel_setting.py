"""add meta pixel setting

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
Create Date: 2026-09-08 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'i9d0e1f2a3b4'
down_revision = 'h8c9d0e1f2a3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meta_pixel_id', sa.String(length=32), nullable=True))


def downgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.drop_column('meta_pixel_id')
