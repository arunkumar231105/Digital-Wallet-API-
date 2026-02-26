"""add idempotency keys table

Revision ID: 0005_add_idempotency_keys
Revises: 0004_add_transaction_status
Create Date: 2026-02-20 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_add_idempotency_keys"
down_revision: Union[str, Sequence[str], None] = "0004_add_transaction_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("response_data", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_idempotency_keys_id"), "idempotency_keys", ["id"], unique=False)
    op.create_index(op.f("ix_idempotency_keys_key"), "idempotency_keys", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_idempotency_keys_key"), table_name="idempotency_keys")
    op.drop_index(op.f("ix_idempotency_keys_id"), table_name="idempotency_keys")
    op.drop_table("idempotency_keys")
