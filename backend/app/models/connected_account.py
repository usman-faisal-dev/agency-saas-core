"""
SQLAlchemy model for the `connected_accounts` table.

Each row represents a client's connected ad/analytics provider (GA4, Google Ads).
Tokens are stored encrypted at rest via Fernet (see app.core.security).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # 'ga4' | 'google_ads'
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="connected"
    )  # 'connected' | 'disconnected' | 'error'
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    client: Mapped["Client"] = relationship(  # noqa: F821
        "Client", back_populates="connected_accounts", lazy="noload"
    )

    def __repr__(self) -> str:
        return (
            f"<ConnectedAccount id={self.id!r}"
            f" client_id={self.client_id!r}"
            f" provider={self.provider!r}>"
        )
