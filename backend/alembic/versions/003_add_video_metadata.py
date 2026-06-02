"""Add video metadata fields

Revision ID: 003_add_video_metadata
Revises: 002_add_error_message
Create Date: 2026-05-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003_add_video_metadata"
down_revision = "002_add_error_message"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("videos", sa.Column("thumbnail", sa.String(length=500), nullable=True))
    op.add_column("videos", sa.Column("uploader", sa.String(length=500), nullable=True))
    op.add_column("videos", sa.Column("upload_date", sa.String(length=20), nullable=True))
    op.add_column("videos", sa.Column("view_count", sa.Float(), nullable=True))
    op.add_column("videos", sa.Column("like_count", sa.Float(), nullable=True))
    op.add_column("videos", sa.Column("metadata_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("videos", "metadata_json")
    op.drop_column("videos", "like_count")
    op.drop_column("videos", "view_count")
    op.drop_column("videos", "upload_date")
    op.drop_column("videos", "uploader")
    op.drop_column("videos", "thumbnail")
