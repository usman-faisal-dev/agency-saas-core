"""
Organizations API — Agency Profile endpoints.

Routes:
  GET  /api/v1/organizations/me  → return the current org's profile
  PATCH /api/v1/organizations/me → update agency name / logo_url
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.dependencies import CurrentOrgId, CurrentUser
from app.models.organization import Organization
from app.schemas.organization import OrganizationRead, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationRead)
def get_my_organization(
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> Organization:
    """Return the agency profile for the authenticated user's organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org is None:
        raise NotFoundError("Organization not found")
    return org


@router.patch("/me", response_model=OrganizationRead)
def update_my_organization(
    payload: OrganizationUpdate,
    org_id: CurrentOrgId,
    db: Session = Depends(get_db),
) -> Organization:
    """
    Update agency name and/or logo.
    Only non-None fields in the payload are applied (partial update).
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if org is None:
        raise NotFoundError("Organization not found")

    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)
    return org
