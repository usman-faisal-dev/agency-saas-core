"""create_connected_accounts

Phase 1: connected_accounts table with encrypted token columns.
Production-shaped schema populated via simulated OAuth flow + sandbox credentials.

Revision ID: 004
Revises: 003
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "connected_accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "client_id",
            sa.String(36),
            sa.ForeignKey("clients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="connected"),
        sa.Column("access_token_encrypted", sa.Text(), nullable=False),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=False),
        sa.Column("token_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("client_id", "provider", name="uq_connected_accounts_client_provider"),
    )
    op.create_index("ix_connected_accounts_client_id", "connected_accounts", ["client_id"])


def downgrade() -> None:
    op.drop_index("ix_connected_accounts_client_id", table_name="connected_accounts")
    op.drop_table("connected_accounts")
