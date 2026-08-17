"""add form notification status

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-17 04:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('form_submissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notification_status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('notification_error', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('notified_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('form_submissions', schema=None) as batch_op:
        batch_op.drop_column('notified_at')
        batch_op.drop_column('notification_error')
        batch_op.drop_column('notification_status')
