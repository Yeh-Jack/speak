"""add_notes_zh_to_study_plans

Revision ID: 006_add_notes_zh
Revises: 005_create_speaking_practice_records
Create Date: 2026-06-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '006_add_notes_zh'
down_revision: Union[str, None] = '005_create_speaking_practice_records'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('study_plans', sa.Column('notes_zh', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('study_plans', 'notes_zh')