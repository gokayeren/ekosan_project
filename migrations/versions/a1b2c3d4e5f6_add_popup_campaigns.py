"""add popup campaigns

Revision ID: a1b2c3d4e5f6
Revises: 6476554f2de9
Create Date: 2026-05-20 12:45:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '6476554f2de9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'popup_campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('display_type', sa.String(length=30), nullable=True),
        sa.Column('pages', sa.String(length=500), nullable=True),
        sa.Column('exclude_pages', sa.String(length=500), nullable=True),
        sa.Column('position', sa.String(length=30), nullable=True),
        sa.Column('delay_seconds', sa.Integer(), nullable=True),
        sa.Column('auto_close_seconds', sa.Integer(), nullable=True),
        sa.Column('frequency', sa.String(length=30), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('font_family', sa.String(length=120), nullable=True),
        sa.Column('html_content', sa.Text(), nullable=True),
        sa.Column('button_text', sa.String(length=80), nullable=True),
        sa.Column('button_url', sa.String(length=500), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('popup_campaigns')
