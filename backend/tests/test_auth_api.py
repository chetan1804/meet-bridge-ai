from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app
from tests.conftest import engine


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_registration_login_and_current_user() -> None:
    credentials = {"email": "person@example.com", "password": "a-long-secret-password"}

    registration = client.post("/api/auth/register", json=credentials)
    assert registration.status_code == 201
    token = registration.json()["access_token"]

    current_user = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current_user.status_code == 200
    assert current_user.json()["email"] == credentials["email"]

    login = client.post("/api/auth/login", json=credentials)
    assert login.status_code == 200
    assert login.json()["access_token"]


def test_auth_rejects_duplicate_invalid_and_missing_credentials() -> None:
    credentials = {"email": "person@example.com", "password": "a-long-secret-password"}
    assert client.post("/api/auth/register", json=credentials).status_code == 201
    assert client.post("/api/auth/register", json=credentials).status_code == 409
    assert client.post("/api/auth/login", json={**credentials, "password": "wrong-password-value"}).status_code == 401
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.value"}).status_code == 401
