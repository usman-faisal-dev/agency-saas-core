"""
Security utilities:
  - Clerk JWT verification (using Clerk's JWKS endpoint)
  - Fernet-based field-level encryption for token columns
    (scaffolded here; actively used from Phase 1 onward)

IMPORTANT: Tokens must NEVER appear in logs or API responses.
"""
import base64
import logging
from functools import lru_cache

import httpx
from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from app.config import get_settings
from app.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Clerk JWT verification
# ---------------------------------------------------------------------------

@lru_cache
def _get_jwks() -> dict:
    """
    Fetch and cache Clerk's JWKS (JSON Web Key Set).
    Called once per process; the lru_cache means it won't hit the network
    on every request.  If you need key rotation, restart the process.
    """
    settings = get_settings()
    resp = httpx.get(settings.clerk_jwks_url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def verify_clerk_jwt(token: str) -> dict:
    """
    Verify a Clerk-issued JWT and return its claims dict.
    Raises AuthenticationError on any failure.

    Expected claims returned:
      sub        — Clerk user ID (e.g. "user_2abc...")
      email      — primary email address
      exp, iat   — standard timing claims (validated by jose)
    """
    try:
        jwks = _get_jwks()
        # Decode header to find the key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Find matching key in the JWKS
        rsa_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key.get("use", "sig"),
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if rsa_key is None:
            raise AuthenticationError("No matching JWKS key found for token kid")

        claims = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # Clerk tokens have no audience by default
        )
        return claims

    except JWTError as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise AuthenticationError("Invalid or expired token") from exc
    except httpx.HTTPError as exc:
        logger.error("Failed to fetch Clerk JWKS: %s", exc)
        raise AuthenticationError("Could not validate credentials") from exc


# ---------------------------------------------------------------------------
# Fernet field-level encryption (for token columns in connected_accounts)
# ---------------------------------------------------------------------------

def _get_fernet() -> Fernet:
    settings = get_settings()
    return Fernet(settings.encryption_key.encode())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a plaintext token string. Returns a URL-safe base64 string."""
    fernet = _get_fernet()
    return fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """
    Decrypt an encrypted token string.
    Raises ValueError if the ciphertext is invalid or the key has changed.
    """
    fernet = _get_fernet()
    try:
        return fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        logger.error("Token decryption failed — key mismatch or corrupted ciphertext")
        raise ValueError("Token decryption failed") from exc
