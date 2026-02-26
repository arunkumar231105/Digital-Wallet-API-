"""remove idempotency keys table

Revision ID: 0007_remove_idempotency_keys
Revises: 0006_scope_idem_unique
Create Date: 2026-02-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_remove_idempotency_keys"
down_revision: Union[str, Sequence[str], None] = "0006_scope_idem_unique"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("idempotency_keys")


def downgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("response_data", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "user_id", "endpoint", name="uq_idempotency_key_user_endpoint"),
    )
    op.create_index("ix_idempotency_keys_id", "idempotency_keys", ["id"], unique=False)
    op.create_index("ix_idempotency_keys_key", "idempotency_keys", ["key"], unique=False)
