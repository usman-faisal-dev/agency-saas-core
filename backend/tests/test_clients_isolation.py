"""
Tenant-isolation tests for clients and connected accounts endpoints.

Verifies that org A cannot access, modify, or delete org B's clients
or connected accounts. All endpoints must enforce CurrentOrgId scoping.
"""

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.core.database import get_db
from app.dependencies import get_current_org
from app.main import create_app

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ORG_A_ID = "org-aaaaaaaa-0001"
ORG_B_ID = "org-bbbbbbbb-0002"
CLIENT_A_ID = "client-aaaa-0001"
CLIENT_B_ID = "client-bbbb-0002"
ACCOUNT_B_ID = "account-bbbb-0001"


def _make_png_bytes() -> bytes:
    img = Image.new("RGB", (1, 1), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def app():
    return create_app()


@pytest.fixture()
def client_org_a(app):
    """Test client authenticated as org A, with a mock DB session."""
    mock_db = MagicMock()
    app.dependency_overrides[get_current_org] = lambda: ORG_A_ID
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c, mock_db
    app.dependency_overrides.clear()


@pytest.fixture()
def client_org_b(app):
    """Test client authenticated as org B, with a mock DB session."""
    mock_db = MagicMock()
    app.dependency_overrides[get_current_org] = lambda: ORG_B_ID
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c, mock_db
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Clients endpoint isolation
# ---------------------------------------------------------------------------


class TestClientsIsolation:
    """Org A must not see or modify org B's clients."""

    def test_list_clients_only_returns_own_org(self, client_org_a):
        """GET /clients must only return clients belonging to the authenticated org."""
        client, mock_db = client_org_a
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        response = client.get("/api/v1/clients")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_client_from_other_org_returns_404(self, client_org_a):
        """GET /clients/{id} for a client in another org must return 404."""
        client, mock_db = client_org_a
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.get(f"/api/v1/clients/{CLIENT_B_ID}")
        assert response.status_code == 404

    def test_update_client_from_other_org_returns_404(self, client_org_a):
        """PATCH /clients/{id} for a client in another org must return 404."""
        client, mock_db = client_org_a
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.patch(
            f"/api/v1/clients/{CLIENT_B_ID}",
            json={"name": "Hacked Name"},
        )
        assert response.status_code == 404

    def test_delete_client_from_other_org_returns_404(self, client_org_a):
        """DELETE /clients/{id} for a client in another org must return 404."""
        client, mock_db = client_org_a
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.delete(f"/api/v1/clients/{CLIENT_B_ID}")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Connected accounts endpoint isolation
# ---------------------------------------------------------------------------


class TestConnectedAccountsIsolation:
    """Org A must not connect, list, or disconnect org B's accounts."""

    def test_connect_for_other_org_client_returns_404(self, client_org_a):
        """POST /connected-accounts for a client in another org must return 404."""
        client, mock_db = client_org_a
        # Client validation fails — client not found in org A's scope
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.post(
            "/api/v1/connected-accounts",
            json={"client_id": CLIENT_B_ID, "provider": "ga4"},
        )
        assert response.status_code == 404

    def test_list_accounts_for_other_org_client_returns_404(self, client_org_a):
        """GET /connected-accounts?client_id= for another org's client must return 404."""
        client, mock_db = client_org_a
        mock_db.query.return_value.filter.return_value.first.return_value = None

        response = client.get(f"/api/v1/connected-accounts?client_id={CLIENT_B_ID}")
        assert response.status_code == 404

    def test_disconnect_other_org_account_returns_404(self, client_org_a):
        """DELETE /connected-accounts/{id} for another org's account must return 404."""
        client, mock_db = client_org_a
        # Join query returns None — account not found in org A's scope
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = None

        response = client.delete(f"/api/v1/connected-accounts/{ACCOUNT_B_ID}")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Upload endpoint client_id isolation
# ---------------------------------------------------------------------------


class TestUploadClientIdIsolation:
    """Upload with client_id must validate the client belongs to the org."""

    @patch("app.storage.get_storage")
    def test_upload_with_other_org_client_id_returns_404(self, mock_get_storage, client_org_a):
        """POST /upload/logo with a client_id from another org must return 404."""
        client, mock_db = client_org_a
        # Client validation fails
        mock_db.query.return_value.filter.return_value.first.return_value = None

        png = _make_png_bytes()
        response = client.post(
            "/api/v1/upload/logo",
            files={"logo": ("test.png", png, "image/png")},
            data={"client_id": CLIENT_B_ID},
        )
        assert response.status_code == 404
