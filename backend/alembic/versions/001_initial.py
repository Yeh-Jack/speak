"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2025-04-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "videos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="youtube"),
        sa.Column("youtube_url", sa.String(1000), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("duration", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("chunk_duration", sa.Float(), nullable=False, server_default="300.0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("idx_videos_status", "videos", ["status"])

    op.create_table(
        "video_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "video_id",
            sa.String(36),
            sa.ForeignKey("videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("duration", sa.Float(), nullable=False),
        sa.Column("transcript", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("video_id", "chunk_index", name="uq_video_chunk_index"),
    )
    op.create_index("idx_chunks_video_id", "video_chunks", ["video_id"])

    op.create_table(
        "courses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("current_video_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "course_videos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "course_id",
            sa.String(36),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "video_id",
            sa.String(36),
            sa.ForeignKey("videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("study_plan", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("course_id", "order_index", name="uq_course_video_order"),
    )

    op.create_table(
        "transcripts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "video_id",
            sa.String(36),
            sa.ForeignKey("videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(50), nullable=False, server_default="youtube"),
        sa.Column("segments", sa.JSON(), nullable=True),
        sa.Column("full_text", sa.Text(), nullable=True),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "study_plans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "video_id",
            sa.String(36),
            sa.ForeignKey("videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=True),
        sa.Column("objectives", sa.JSON(), nullable=True),
        sa.Column("vocabulary", sa.JSON(), nullable=True),
        sa.Column("grammar", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("overall_difficulty", sa.String(10), nullable=True),
        sa.Column("estimated_time", sa.String(50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    op.create_table(
        "vocabularies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("word", sa.String(200), nullable=False),
        sa.Column("definition", sa.Text(), nullable=True),
        sa.Column("context", sa.Text(), nullable=True),
        sa.Column("cefr_level", sa.String(10), nullable=True),
        sa.Column("pronunciation", sa.String(200), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("next_review", sa.Date(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("word", name="uq_vocabulary_word"),
    )

    op.create_table(
        "study_progress",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "video_id",
            sa.String(36),
            sa.ForeignKey("videos.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("current_timestamp", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("sentence_index", sa.Integer(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("video_id", "chunk_index", name="uq_progress_video_chunk"),
    )


def downgrade() -> None:
    op.drop_table("study_progress")
    op.drop_table("vocabularies")
    op.drop_table("study_plans")
    op.drop_table("transcripts")
    op.drop_table("course_videos")
    op.drop_table("courses")
    op.drop_index("idx_chunks_video_id", table_name="video_chunks")
    op.drop_table("video_chunks")
    op.drop_index("idx_videos_status", table_name="videos")
    op.drop_table("videos")
