"""add transaction status

Revision ID: 0004_add_transaction_status
Revises: 0003_add_is_frozen
Create Date: 2026-02-20 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_add_transaction_status"
down_revision: Union[str, Sequence[str], None] = "0003_add_is_frozen"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("transactions", sa.Column("status", sa.String(), nullable=False, server_default="SUCCESS"))


def downgrade() -> None:
    op.drop_column("transactions", "status")
