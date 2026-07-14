"""
Pydantic schemas for the Client resource.
Mirrors the Client SQLAlchemy model for API request/response.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    logo_url: str | None = Field(None)


class ClientRead(BaseModel):
    id: str
    org_id: str
    name: str
    logo_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    logo_url: str | None = Field(None)
