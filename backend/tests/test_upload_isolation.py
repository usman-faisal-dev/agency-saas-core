"""
Tenant-isolation test for the logo upload endpoint.

Ensures that POST /api/v1/upload/logo resolves org_id exclusively from the
authenticated session dependency (CurrentOrgId), never from any client-supplied
value. A malicious client sending an org_id in form data, query params, or
headers must NOT be able to write files under another org's key prefix.
"""
import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.dependencies import get_current_org
from app.main import create_app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

LEGIT_ORG_ID = "legit-org-aaaaaaaa"
EVIL_ORG_ID = "evil-org-zzzzzzzz"


def _make_png_bytes() -> bytes:
    """Return a minimal valid 1x1 red PNG in memory."""
    img = Image.new("RGB", (1, 1), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """
    Build a test client with the upload router and a mocked auth dependency
    that always returns LEGIT_ORG_ID.
    """
    app = create_app()

    # Override the session-based org dependency to return our known legit org
    app.dependency_overrides[get_current_org] = lambda: LEGIT_ORG_ID

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUploadTenantIsolation:
    """
    The upload endpoint must ALWAYS use the org_id from the authenticated
    session dependency — never from client-supplied values.
    """

    @patch("app.api.v1.upload.upload_logo", return_value="https://cdn.example.com/logos/x.png")
    def test_org_id_comes_from_session_not_form(self, mock_upload, client):
        """
        Even if a malicious client sends an 'org_id' form field, the endpoint
        must ignore it and use the session-derived org_id.
        """
        png = _make_png_bytes()

        # Send org_id as a form field alongside the file — the endpoint must ignore it
        response = client.post(
            "/api/v1/upload/logo",
            files={"logo": ("test.png", png, "image/png")},
            data={"org_id": EVIL_ORG_ID},  # malicious injection attempt
        )

        assert response.status_code == 200, response.text
        assert mock_upload.called, "upload_logo should have been called"

        # The 4th positional arg is org_id — verify it's the legit one
        call_args = mock_upload.call_args
        actual_org_id = call_args.args[3]  # upload_logo(data, filename, content_type, org_id)
        assert actual_org_id == LEGIT_ORG_ID, (
            f"upload_logo received org_id={actual_org_id!r}, "
            f"expected {LEGIT_ORG_ID!r} (session dependency). "
            f"Client-supplied org_id was ignored correctly."
        )

    @patch("app.api.v1.upload.upload_logo", return_value="https://cdn.example.com/logos/x.png")
    def test_org_id_comes_from_session_not_query_param(self, mock_upload, client):
        """
        A query-param ?org_id=... must also be ignored.
        """
        png = _make_png_bytes()

        response = client.post(
            f"/api/v1/upload/logo?org_id={EVIL_ORG_ID}",
            files={"logo": ("test.png", png, "image/png")},
        )

        assert response.status_code == 200, response.text
        call_args = mock_upload.call_args
        actual_org_id = call_args.args[3]
        assert actual_org_id == LEGIT_ORG_ID

    @patch("app.storage.get_storage")
    def test_uploaded_key_is_scoped_to_legit_org(self, mock_get_storage, client):
        """
        The storage key generated must live under the legit org's prefix,
        confirming that a malicious client cannot write to another org's path.
        """
        mock_provider = mock_get_storage.return_value
        mock_provider.upload.return_value = "https://cdn.example.com/logos/x.png"

        png = _make_png_bytes()

        response = client.post(
            "/api/v1/upload/logo",
            files={"logo": ("test.png", png, "image/png")},
            data={"org_id": EVIL_ORG_ID},
        )

        assert response.status_code == 200, response.text
        assert mock_provider.upload.called, "storage.upload should have been called"
        call_args = mock_provider.upload.call_args
        key = call_args.args[0]  # first positional arg to upload() is the key
        assert key.startswith(f"logos/{LEGIT_ORG_ID}/"), (
            f"Storage key {key!r} is not scoped to legit org {LEGIT_ORG_ID!r}"
        )
        assert EVIL_ORG_ID not in key, (
            f"Storage key {key!r} contains the malicious org_id {EVIL_ORG_ID!r}"
        )
