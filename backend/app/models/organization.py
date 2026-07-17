"""
SQLAlchemy model for the `organizations` table.

MVP: single row for one agency.
Schema is forward-compatible with multi-org support — every tenant table
carries org_id so future Postgres RLS is a policy addition, not a migration.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # logo_url stores a URL reference to the uploaded file in object storage
    logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships (populated by later migrations)
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User", back_populates="organization", lazy="noload"
    )
    clients: Mapped[list["Client"]] = relationship(  # noqa: F821
        "Client", back_populates="organization", lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id!r} name={self.name!r}>"
