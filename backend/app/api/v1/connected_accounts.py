"""
Connected Accounts API — simulated OAuth connect flow.

Routes:
  POST   /api/v1/connected-accounts              → simulate connecting a provider
  GET    /api/v1/connected-accounts?client_id=   → list connections for a client
  DELETE /api/v1/connected-accounts/{account_id} → disconnect (soft delete)

In MVP, the OAuth flow is simulated: sandbox credentials from env vars are
encrypted and stored. The schema is production-shaped for a future real OAuth flow.
"""

import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.database import get_db
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import encrypt_token
from app.dependencies import CurrentOrgId
from app.models.client import Client
from app.models.connected_account import ConnectedAccount
from app.schemas.connected_account import ConnectedAccountCreate, ConnectedAccountRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/connected-accounts", tags=["connected-accounts"])

# Map provider → sandbox credential settings keys
_SANDBOX_TOKENS = {
    "ga4": ("ga4_sandbox_access_token", "ga4_sandbox_refresh_token"),
    "google_ads": ("google_ads_sandbox_access_token", "google_ads_sandbox_refresh_token"),
}


def _validate_client(client_id: str, org_id: str, db: Session) -> Client:
    """Ensure the client exists and belongs to the current org."""
    client = db.query(Client).filter(Client.id == client_id, Client.org_id == org_id).first()
    if client is None:
        raise NotFoundError("Client not found")
    return client


@router.post("", response_model=ConnectedAccountRead, status_code=201)
def connect_account(
    payload: ConnectedAccountCreate,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> ConnectedAccount:
    """
    Simulate connecting a GA4 or Google Ads account for a client.

    Encrypts sandbox credentials and stores them. If a disconnected/error
    connection already exists for this (client, provider), it is re-activated
    with fresh tokens instead of creating a duplicate row.
    """
    _validate_client(payload.client_id, org_id, db)
    settings = get_settings()

    access_key, refresh_key = _SANDBOX_TOKENS[payload.provider]
    access_token = getattr(settings, access_key)
    refresh_token = getattr(settings, refresh_key)

    # Check for existing connection
    existing = (
        db.query(ConnectedAccount)
        .filter(
            ConnectedAccount.client_id == payload.client_id,
            ConnectedAccount.provider == payload.provider,
        )
        .first()
    )

    if existing and existing.status == "connected":
        raise ConflictError(f"{payload.provider} is already connected for this client")

    token_expiry = datetime.now(UTC) + timedelta(hours=1)

    if existing:
        # Reconnect: update existing row with fresh encrypted tokens
        existing.access_token_encrypted = encrypt_token(access_token)
        existing.refresh_token_encrypted = encrypt_token(refresh_token)
        existing.status = "connected"
        existing.token_expiry = token_expiry
        db.commit()
        db.refresh(existing)
        logger.info(
            "Reconnected %s for client %s (account %s)",
            payload.provider,
            payload.client_id,
            existing.id,
        )
        return existing

    # New connection
    account = ConnectedAccount(
        client_id=payload.client_id,
        provider=payload.provider,
        status="connected",
        access_token_encrypted=encrypt_token(access_token),
        refresh_token_encrypted=encrypt_token(refresh_token),
        token_expiry=token_expiry,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    logger.info(
        "Connected %s for client %s (account %s)",
        payload.provider,
        payload.client_id,
        account.id,
    )
    return account


@router.get("", response_model=list[ConnectedAccountRead])
def list_connected_accounts(
    org_id: CurrentOrgId,
    client_id: str = Query(..., description="Client ID to list connections for"),
    db: Session = Depends(get_db),
) -> list[ConnectedAccount]:
    """List all connected accounts for a client, scoped to the current org."""
    _validate_client(client_id, org_id, db)
    return (
        db.query(ConnectedAccount)
        .filter(ConnectedAccount.client_id == client_id)
        .order_by(ConnectedAccount.created_at.desc())
        .all()
    )


@router.delete("/{account_id}", status_code=204)
def disconnect_account(
    account_id: str,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> None:
    """
    Soft-disconnect a connected account.
    Sets status='disconnected' but preserves encrypted tokens for future reconnect.
    """
    account = (
        db.query(ConnectedAccount)
        .join(Client, ConnectedAccount.client_id == Client.id)
        .filter(ConnectedAccount.id == account_id, Client.org_id == org_id)
        .first()
    )
    if account is None:
        raise NotFoundError("Connected account not found")

    account.status = "disconnected"
    db.commit()
    logger.info("Disconnected account %s (provider=%s)", account.id, account.provider)
