"""add_error_message_to_videos

Revision ID: 002_add_error_message
Revises: 001_initial
Create Date: 2026-04-26

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_add_error_message"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("videos", sa.Column("error_message", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("videos", "error_message")
