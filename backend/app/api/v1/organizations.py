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
from app.dependencies import CurrentOrgId
from app.models.organization import Organization
from app.schemas.organization import OrganizationRead, OrganizationUpdate
from app.storage import delete_logo, extract_logo_key

import logging
logger = logging.getLogger(__name__)

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

    old_logo_url = None
    update_data = payload.model_dump(exclude_none=True)
    if "logo_url" in update_data and update_data["logo_url"] != org.logo_url:
        old_logo_url = org.logo_url

    for field, value in update_data.items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)
    
    if old_logo_url:
        key = extract_logo_key(old_logo_url)
        if key:
            try:
                delete_logo(key)
            except Exception as e:
                logger.error(f"Failed to delete old organization logo {key}: {e}")

    return org
