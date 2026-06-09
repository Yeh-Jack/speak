"""Add interval, ease_factor, repetition_number to vocabularies.

Revision ID: 007
Revises: 006_add_notes_zh
Create Date: 2026-06-09

"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006_add_notes_zh'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('vocabularies', sa.Column('interval', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('vocabularies', sa.Column('ease_factor', sa.Float(), nullable=False, server_default='2.5'))
    op.add_column('vocabularies', sa.Column('repetition_number', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('vocabularies', 'repetition_number')
    op.drop_column('vocabularies', 'ease_factor')
    op.drop_column('vocabularies', 'interval')