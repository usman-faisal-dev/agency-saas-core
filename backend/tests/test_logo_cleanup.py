"""
Tests for R2 orphaned-file cleanup (Logo Replacement and Client Deletion).
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.dependencies import get_current_org
from app.main import create_app
from app.models.client import Client
from app.models.organization import Organization

ORG_ID = "org-test-cleanup"
CLIENT_ID = "client-test-cleanup"
NOW = datetime.now(timezone.utc)

@pytest.fixture()
def app():
    return create_app()

@pytest.fixture()
def client_app(app):
    """Test client authenticated with a mock DB session."""
    mock_db = MagicMock()
    app.dependency_overrides[get_current_org] = lambda: ORG_ID
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c, mock_db
    app.dependency_overrides.clear()


@patch("app.api.v1.clients.delete_logo")
def test_client_logo_replacement_calls_delete_logo(mock_delete_logo, client_app):
    client, mock_db = client_app
    
    mock_client = Client(id=CLIENT_ID, org_id=ORG_ID, name="Old Name", logo_url="https://bucket.com/logos/org/clients/client/old.png")
    mock_client.created_at = NOW
    mock_client.updated_at = NOW
    mock_db.query.return_value.filter.return_value.first.return_value = mock_client

    response = client.patch(
        f"/api/v1/clients/{CLIENT_ID}",
        json={"logo_url": "https://bucket.com/logos/org/clients/client/new.png"},
    )
    
    assert response.status_code == 200
    mock_delete_logo.assert_called_once_with("logos/org/clients/client/old.png")


@patch("app.api.v1.clients.delete_logo")
def test_client_logo_replacement_handles_delete_error(mock_delete_logo, client_app):
    client, mock_db = client_app
    
    mock_client = Client(id=CLIENT_ID, org_id=ORG_ID, name="Old Name", logo_url="https://bucket.com/logos/org/clients/client/old.png")
    mock_client.created_at = NOW
    mock_client.updated_at = NOW
    mock_db.query.return_value.filter.return_value.first.return_value = mock_client

    # delete_logo raises exception
    mock_delete_logo.side_effect = Exception("S3 bucket offline")

    response = client.patch(
        f"/api/v1/clients/{CLIENT_ID}",
        json={"logo_url": "https://bucket.com/logos/org/clients/client/new.png"},
    )
    
    # Should still succeed
    assert response.status_code == 200
    mock_delete_logo.assert_called_once_with("logos/org/clients/client/old.png")
    assert response.json()["logo_url"] == "https://bucket.com/logos/org/clients/client/new.png"


@patch("app.api.v1.clients.delete_logo")
def test_client_deletion_calls_delete_logo(mock_delete_logo, client_app):
    client, mock_db = client_app
    
    mock_client = Client(id=CLIENT_ID, org_id=ORG_ID, name="Old Name", logo_url="https://bucket.com/logos/org/clients/client/logo.png")
    mock_client.created_at = NOW
    mock_client.updated_at = NOW
    mock_db.query.return_value.filter.return_value.first.return_value = mock_client

    response = client.delete(f"/api/v1/clients/{CLIENT_ID}")
    
    assert response.status_code == 204
    mock_delete_logo.assert_called_once_with("logos/org/clients/client/logo.png")


@patch("app.api.v1.clients.delete_logo")
def test_client_deletion_handles_delete_error(mock_delete_logo, client_app):
    client, mock_db = client_app
    
    mock_client = Client(id=CLIENT_ID, org_id=ORG_ID, name="Old Name", logo_url="https://bucket.com/logos/org/clients/client/logo.png")
    mock_client.created_at = NOW
    mock_client.updated_at = NOW
    mock_db.query.return_value.filter.return_value.first.return_value = mock_client

    mock_delete_logo.side_effect = Exception("S3 bucket offline")

    response = client.delete(f"/api/v1/clients/{CLIENT_ID}")
    
    assert response.status_code == 204
    mock_delete_logo.assert_called_once_with("logos/org/clients/client/logo.png")


@patch("app.api.v1.organizations.delete_logo")
def test_organization_logo_replacement_calls_delete_logo(mock_delete_logo, client_app):
    client, mock_db = client_app
    
    mock_org = Organization(id=ORG_ID, name="Old Name", logo_url="https://bucket.com/logos/org/old.png")
    mock_org.created_at = NOW
    mock_org.updated_at = NOW
    mock_db.query.return_value.filter.return_value.first.return_value = mock_org

    response = client.patch(
        "/api/v1/organizations/me",
        json={"logo_url": "https://bucket.com/logos/org/new.png"},
    )
    
    assert response.status_code == 200
    mock_delete_logo.assert_called_once_with("logos/org/old.png")


@patch("app.api.v1.organizations.delete_logo")
def test_organization_logo_replacement_handles_delete_error(mock_delete_logo, client_app):
    client, mock_db = client_app
    
    mock_org = Organization(id=ORG_ID, name="Old Name", logo_url="https://bucket.com/logos/org/old.png")
    mock_org.created_at = NOW
    mock_org.updated_at = NOW
    mock_db.query.return_value.filter.return_value.first.return_value = mock_org

    mock_delete_logo.side_effect = Exception("S3 bucket offline")

    response = client.patch(
        "/api/v1/organizations/me",
        json={"logo_url": "https://bucket.com/logos/org/new.png"},
    )
    
    assert response.status_code == 200
    mock_delete_logo.assert_called_once_with("logos/org/old.png")
    assert response.json()["logo_url"] == "https://bucket.com/logos/org/new.png"
