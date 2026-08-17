"""add form notification settings

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-17 04:30:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('form_notification_provider', sa.String(length=20), nullable=False, server_default='formsubmit'))
        batch_op.add_column(sa.Column('smtp_host', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('smtp_port', sa.Integer(), nullable=True, server_default='587'))
        batch_op.add_column(sa.Column('smtp_user', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('smtp_password', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('smtp_from', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('smtp_use_ssl', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.drop_column('smtp_use_ssl')
        batch_op.drop_column('smtp_from')
        batch_op.drop_column('smtp_password')
        batch_op.drop_column('smtp_user')
        batch_op.drop_column('smtp_port')
        batch_op.drop_column('smtp_host')
        batch_op.drop_column('form_notification_provider')
