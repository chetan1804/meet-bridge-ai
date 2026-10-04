from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app
from tests.conftest import engine


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def register(email: str) -> str:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": "a-long-secret-password"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


def authorization(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_integration_catalog_lists_sample_integration() -> None:
    token = register("owner@example.com")

    response = client.get("/api/integrations", headers=authorization(token))

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    slack = next(item for item in data if item["key"] == "slack")
    assert slack["name"] == "Slack"
    assert slack["connected"] is False
    assert slack["credential_label"] == "Bot token"


def test_integration_connection_uses_masked_credentials() -> None:
    token = register("owner@example.com")

    response = client.post(
        "/api/integrations/slack/connect",
        json={"token": "slack-token-1234"},
        headers=authorization(token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "slack"
    assert data["connected"] is True
    assert data["credential_preview"].endswith("1234")
    assert data["credential_preview"] != "slack-token-1234"
