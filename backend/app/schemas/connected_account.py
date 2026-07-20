"""
Pydantic schemas for the ConnectedAccount resource.
Never expose encrypted token fields in API responses.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ConnectedAccountCreate(BaseModel):
    client_id: str
    provider: Literal["ga4", "google_ads"]


class ConnectedAccountRead(BaseModel):
    id: str
    client_id: str
    provider: str
    status: str
    token_expiry: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
