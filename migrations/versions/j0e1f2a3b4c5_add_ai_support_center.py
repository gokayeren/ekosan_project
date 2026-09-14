"""add ai support center

Revision ID: j0e1f2a3b4c5
Revises: i9d0e1f2a3b4
"""
from alembic import op
import sqlalchemy as sa

revision = 'j0e1f2a3b4c5'
down_revision = 'i9d0e1f2a3b4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('ai_support_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('widget_title', sa.String(100), nullable=False, server_default='Size nasıl yardımcı olabiliriz?'),
        sa.Column('welcome_message', sa.Text(), nullable=False, server_default='Merhaba! Destek kanalınızı seçebilirsiniz.'),
        sa.Column('provider', sa.String(20), nullable=False, server_default='openai'),
        sa.Column('model_name', sa.String(100)), sa.Column('api_key', sa.Text()),
        sa.Column('system_prompt', sa.Text()), sa.Column('knowledge_urls', sa.Text()),
        sa.Column('company_information', sa.Text()), sa.Column('customer_context', sa.Text()),
        sa.Column('support_form_id', sa.Integer(), sa.ForeignKey('forms.id')),
        sa.Column('updated_at', sa.DateTime()))
    op.create_table('support_conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('public_token', sa.String(36), nullable=False, unique=True),
        sa.Column('channel', sa.String(20), nullable=False, server_default='ai'),
        sa.Column('status', sa.String(20), nullable=False, server_default='open'),
        sa.Column('visitor_name', sa.String(120)), sa.Column('visitor_email', sa.String(160)),
        sa.Column('visitor_phone', sa.String(50)), sa.Column('page_url', sa.String(500)),
        sa.Column('ip_address', sa.String(50)),
        sa.Column('human_takeover', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime()), sa.Column('updated_at', sa.DateTime()))
    op.create_table('support_messages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('conversation_id', sa.Integer(), sa.ForeignKey('support_conversations.id'), nullable=False),
        sa.Column('sender', sa.String(20), nullable=False), sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime()))
    op.create_index('ix_support_messages_conversation_id', 'support_messages', ['conversation_id'])


def downgrade():
    op.drop_index('ix_support_messages_conversation_id', table_name='support_messages')
    op.drop_table('support_messages')
    op.drop_table('support_conversations')
    op.drop_table('ai_support_settings')
