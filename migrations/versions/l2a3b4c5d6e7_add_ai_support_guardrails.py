"""add ai support guardrails

Revision ID: l2a3b4c5d6e7
Revises: k1f2a3b4c5d6
"""
from alembic import op
import sqlalchemy as sa

revision = 'l2a3b4c5d6e7'
down_revision = 'k1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ai_support_settings', sa.Column('conversation_timeout_minutes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('ai_support_settings', sa.Column('closing_message', sa.Text(), nullable=True))
    op.add_column('ai_support_settings', sa.Column('never_send_links', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('ai_support_settings', sa.Column('strict_site_scope', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('ai_support_settings', sa.Column('out_of_scope_message', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('ai_support_settings', 'out_of_scope_message')
    op.drop_column('ai_support_settings', 'strict_site_scope')
    op.drop_column('ai_support_settings', 'never_send_links')
    op.drop_column('ai_support_settings', 'closing_message')
    op.drop_column('ai_support_settings', 'conversation_timeout_minutes')
