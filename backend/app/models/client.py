"""
SQLAlchemy model for the `clients` table.

Every client belongs to an org_id — this is the primary tenant-scoping key.
All queries touching clients MUST filter by org_id (enforced via the
get_current_org dependency, not Postgres RLS in MVP).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        "Organization", back_populates="clients", lazy="noload"
    )
    connected_accounts: Mapped[list["ConnectedAccount"]] = relationship(  # noqa: F821
        "ConnectedAccount", back_populates="client", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id!r} name={self.name!r} org_id={self.org_id!r}>"
