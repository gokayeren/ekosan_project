"""add persistent support rate limits

Revision ID: m3b4c5d6e7f8
Revises: l2a3b4c5d6e7
"""
from alembic import op
import sqlalchemy as sa

revision = 'm3b4c5d6e7f8'
down_revision = 'l2a3b4c5d6e7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('ai_support_settings', sa.Column('reconnect_cooldown_minutes', sa.Integer(), nullable=False, server_default='30'))
    op.add_column('ai_support_settings', sa.Column('max_conversations_per_hour', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('ai_support_settings', sa.Column('message_cooldown_seconds', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('ai_support_settings', sa.Column('max_messages_per_minute', sa.Integer(), nullable=False, server_default='8'))
    op.add_column('ai_support_settings', sa.Column('max_messages_per_hour', sa.Integer(), nullable=False, server_default='60'))
    op.create_index('ix_support_conversations_ip_created', 'support_conversations', ['ip_address', 'created_at'])
    op.create_index('ix_support_messages_conversation_sender_created', 'support_messages', ['conversation_id', 'sender', 'created_at'])


def downgrade():
    op.drop_index('ix_support_messages_conversation_sender_created', table_name='support_messages')
    op.drop_index('ix_support_conversations_ip_created', table_name='support_conversations')
    op.drop_column('ai_support_settings', 'max_messages_per_hour')
    op.drop_column('ai_support_settings', 'max_messages_per_minute')
    op.drop_column('ai_support_settings', 'message_cooldown_seconds')
    op.drop_column('ai_support_settings', 'max_conversations_per_hour')
    op.drop_column('ai_support_settings', 'reconnect_cooldown_minutes')
