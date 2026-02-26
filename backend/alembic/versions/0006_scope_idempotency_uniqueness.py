"""scope idempotency key uniqueness by user and endpoint

Revision ID: 0006_scope_idem_unique
Revises: 0005_add_idempotency_keys
Create Date: 2026-02-20 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "0006_scope_idem_unique"
down_revision: Union[str, Sequence[str], None] = "0005_add_idempotency_keys"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_idempotency_keys_key", table_name="idempotency_keys")
    op.create_index("ix_idempotency_keys_key", "idempotency_keys", ["key"], unique=False)
    op.drop_constraint("idempotency_keys_key_key", "idempotency_keys", type_="unique")
    op.create_unique_constraint("uq_idempotency_key_user_endpoint", "idempotency_keys", ["key", "user_id", "endpoint"])


def downgrade() -> None:
    op.drop_constraint("uq_idempotency_key_user_endpoint", "idempotency_keys", type_="unique")
    op.create_unique_constraint("idempotency_keys_key_key", "idempotency_keys", ["key"])
    op.drop_index("ix_idempotency_keys_key", table_name="idempotency_keys")
    op.create_index("ix_idempotency_keys_key", "idempotency_keys", ["key"], unique=True)
