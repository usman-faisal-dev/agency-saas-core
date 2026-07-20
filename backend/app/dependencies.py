"""
Shared FastAPI dependencies.

These are the primary entry points for route handlers:
  - get_db            → yields a database Session
  - get_current_user  → verifies Clerk JWT, upserts User row, returns User
  - get_current_org   → returns the org_id string for the current user

The org_id scoping pattern:
  Every route that accesses tenant data must declare `org_id: str = Depends(get_current_org)`.
  This ensures the pattern is used from the very first query onward (PLAN.md Phase 0 requirement).
"""

import logging
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthenticationError
from app.core.security import verify_clerk_jwt
from app.models.organization import Organization
from app.models.user import User

logger = logging.getLogger(__name__)


# Re-export get_db so routes can import from one place
DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    """
    1. Extracts the Bearer token from the Authorization header.
    2. Verifies it against Clerk's JWKS.
    3. Upserts a User row (create on first login, update email if changed).
    4. Returns the User ORM object.

    Raises AuthenticationError if the token is missing or invalid.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthenticationError("Missing Bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    claims = verify_clerk_jwt(token)

    clerk_user_id: str = claims.get("sub", "")
    email: str = (
        claims.get("email", "") or claims.get("email_addresses", [{}])[0].get("email_address", "")
        if isinstance(claims.get("email_addresses"), list)
        else claims.get("email", "")
    )

    if not clerk_user_id:
        raise AuthenticationError("Token missing sub claim")

    # Upsert: find existing user or bootstrap one (MVP: single org)
    user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()

    if user is None:
        # First login: ensure the single org exists, then create the user
        org = db.query(Organization).first()
        if org is None:
            # Bootstrap the org on very first sign-in
            org = Organization(name="My Agency")
            db.add(org)
            db.flush()  # get org.id without committing

        user = User(
            clerk_user_id=clerk_user_id,
            org_id=org.id,
            email=email,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Created new user %s in org %s", clerk_user_id, org.id)
    elif user.email != email and email:
        # Keep email in sync with Clerk
        user.email = email
        db.commit()

    return user


def get_current_org(
    current_user: Annotated[User, Depends(get_current_user)],
) -> str:
    """
    Returns the org_id of the authenticated user.

    Usage in route handlers:
        @router.get("/something")
        def my_route(org_id: str = Depends(get_current_org), db: Session = Depends(get_db)):
            results = db.query(MyModel).filter(MyModel.org_id == org_id).all()
    """
    return current_user.org_id


# Convenience type aliases for annotated dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentOrgId = Annotated[str, Depends(get_current_org)]
