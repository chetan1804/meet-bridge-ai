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


def test_security_audit_logs_and_uploads_are_protected() -> None:
    token = register("owner@example.com")

    audit_event = client.post(
        "/api/security/audit",
        json={
            "action": "workspace_access",
            "resource": "organizations/acme",
            "details": "tenant access checked",
        },
        headers=authorization(token),
    )
    assert audit_event.status_code == 200
    assert audit_event.json()["action"] == "workspace_access"

    audit_list = client.get("/api/security/audit", headers=authorization(token))
    assert audit_list.status_code == 200
    assert any(item["action"] == "workspace_access" for item in audit_list.json())

    rate_check = client.post(
        "/api/security/rate-limit/check",
        json={"action": "workspace_access", "limit": 5},
        headers=authorization(token),
    )
    assert rate_check.status_code == 200
    assert rate_check.json()["allowed"] is True

    upload = client.post(
        "/api/security/uploads/secure",
        json={"filename": "internal-notes.pdf", "content": "secret internal plan"},
        headers=authorization(token),
    )
    assert upload.status_code == 200
    assert upload.json()["secure"] is True
    assert upload.json()["retention_days"] == 30
    assert "secret" not in upload.json()["storage_key"]
