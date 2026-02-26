"""add admin and transfer counterparty fields

Revision ID: 0002_admin_and_counterparty
Revises: 0001_initial
Create Date: 2026-02-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_admin_and_counterparty"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.add_column("transactions", sa.Column("sender_id", sa.Integer(), nullable=True))
    op.add_column("transactions", sa.Column("receiver_id", sa.Integer(), nullable=True))

    op.create_foreign_key("fk_transactions_sender_id_users", "transactions", "users", ["sender_id"], ["id"])
    op.create_foreign_key("fk_transactions_receiver_id_users", "transactions", "users", ["receiver_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_transactions_receiver_id_users", "transactions", type_="foreignkey")
    op.drop_constraint("fk_transactions_sender_id_users", "transactions", type_="foreignkey")

    op.drop_column("transactions", "receiver_id")
    op.drop_column("transactions", "sender_id")

    op.drop_column("users", "is_admin")
