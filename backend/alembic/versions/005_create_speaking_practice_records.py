"""create_speaking_practice_records

Revision ID: 005_create_speaking_practice_records
Revises: 004_remove_courses
Create Date: 2026-06-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '005_create_speaking_practice_records'
down_revision: Union[str, None] = '004_remove_courses'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'speaking_practice_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('video_id', sa.String(36), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('segment_start', sa.Float(), nullable=False),
        sa.Column('segment_end', sa.Float(), nullable=False),
        sa.Column('character_text', sa.Text(), nullable=False),
        sa.Column('user_recording_path', sa.String(500), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('attempts', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('speaking_practice_records')