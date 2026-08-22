"""add phase one onboarding fields

Revision ID: a1b2c3d4e5f6
Revises: c66ba4a5c897
Create Date: 2026-08-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "c66ba4a5c897"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("subscriber_count_bracket", sa.String(length=40), nullable=True))
    op.add_column("users", sa.Column("previous_tool", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "previous_tool")
    op.drop_column("users", "subscriber_count_bracket")