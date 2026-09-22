"""Establish the migration baseline.

Revision ID: 0001_database_foundation
Revises:
Create Date: 2026-09-22 00:00:00
"""

from typing import Sequence, Union


revision: str = "0001_database_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create no feature tables; feature migrations own their schemas."""


def downgrade() -> None:
    """Revert the empty baseline migration."""
