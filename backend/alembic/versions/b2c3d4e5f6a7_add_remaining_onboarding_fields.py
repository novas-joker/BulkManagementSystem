"""add remaining onboarding fields

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("business_industry", sa.String(length=80), nullable=True))
    op.add_column("users", sa.Column("business_website", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("compliance_address", sa.JSON(), nullable=True))
    op.add_column("users", sa.Column("user_primary_goal", sa.String(length=80), nullable=True))
    op.add_column("users", sa.Column("product_updates_consent", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("onboarding_phase", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("users", sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("users", "onboarding_completed")
    op.drop_column("users", "onboarding_phase")
    op.drop_column("users", "product_updates_consent")
    op.drop_column("users", "user_primary_goal")
    op.drop_column("users", "compliance_address")
    op.drop_column("users", "business_website")
    op.drop_column("users", "business_industry")