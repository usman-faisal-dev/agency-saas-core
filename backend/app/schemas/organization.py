"""
Pydantic schemas for the Organization resource.
Mirrors the Organization SQLAlchemy model for API request/response.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationRead(BaseModel):
    id: str
    name: str
    logo_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    # logo_url is a URL reference to the uploaded file (stored via /api/v1/upload/logo)
    logo_url: str | None = Field(None)
