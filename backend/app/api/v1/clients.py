"""
Clients API — CRUD endpoints for agency clients.

Routes:
  POST   /api/v1/clients              → create a new client
  GET    /api/v1/clients              → list all clients for the current org
  GET    /api/v1/clients/{client_id}  → get a single client
  PATCH  /api/v1/clients/{client_id}  → update client name/logo
  DELETE /api/v1/clients/{client_id}  → delete a client (cascades to connected_accounts)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.dependencies import CurrentOrgId
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])


def _get_client_or_404(client_id: str, org_id: str, db: Session) -> Client:
    """Fetch a client scoped to the current org, or raise 404."""
    client = db.query(Client).filter(Client.id == client_id, Client.org_id == org_id).first()
    if client is None:
        raise NotFoundError("Client not found")
    return client


@router.post("", response_model=ClientRead, status_code=201)
def create_client(
    payload: ClientCreate,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> Client:
    """Create a new client for the current org."""
    client = Client(
        org_id=org_id,
        name=payload.name,
        logo_url=payload.logo_url,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("", response_model=list[ClientRead])
def list_clients(
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> list[Client]:
    """List all clients for the current org, newest first."""
    return db.query(Client).filter(Client.org_id == org_id).order_by(Client.created_at.desc()).all()


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: str,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> Client:
    """Get a single client by ID, scoped to the current org."""
    return _get_client_or_404(client_id, org_id, db)


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: str,
    payload: ClientUpdate,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> Client:
    """Update client name and/or logo_url. Only non-None fields are applied."""
    client = _get_client_or_404(client_id, org_id, db)

    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=204)
def delete_client(
    client_id: str,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> None:
    """Delete a client. Connected accounts are removed via ON DELETE CASCADE."""
    client = _get_client_or_404(client_id, org_id, db)
    db.delete(client)
    db.commit()
