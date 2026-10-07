"""Add subscription plan to users.

Revision ID: 0005_add_user_plan
Revises: 0004_add_meetings
Create Date: 2026-10-07 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_add_user_plan"
down_revision: Union[str, None] = "0004_add_meetings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("plan", sa.String(length=20), server_default="FREE", nullable=False),
    )
    op.alter_column("users", "plan", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "plan")
