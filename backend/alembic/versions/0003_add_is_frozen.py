"""add frozen account flag

Revision ID: 0003_add_is_frozen
Revises: 0002_admin_and_counterparty
Create Date: 2026-02-20 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_add_is_frozen"
down_revision: Union[str, Sequence[str], None] = "0002_admin_and_counterparty"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_frozen", sa.Boolean(), nullable=False, server_default=sa.text("false")))


def downgrade() -> None:
    op.drop_column("users", "is_frozen")
