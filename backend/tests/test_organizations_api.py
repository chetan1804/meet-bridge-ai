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


def test_personal_and_shared_workspaces_are_scoped_to_member() -> None:
    owner_token = register("owner@example.com")
    member_token = register("member@example.com")
    outsider_token = register("outsider@example.com")

    created = client.post(
        "/api/organizations", json={"name": "Acme"}, headers=authorization(owner_token)
    )
    assert created.status_code == 201
    organization_id = created.json()["id"]
    assert created.json()["role"] == "OWNER"

    added = client.post(
        f"/api/organizations/{organization_id}/members",
        json={"email": "member@example.com", "role": "MEMBER"},
        headers=authorization(owner_token),
    )
    assert added.status_code == 201

    member_workspaces = client.get("/api/organizations", headers=authorization(member_token))
    assert organization_id in {workspace["id"] for workspace in member_workspaces.json()}

    blocked_detail = client.get(f"/api/organizations/{organization_id}", headers=authorization(outsider_token))
    blocked_members = client.get(f"/api/organizations/{organization_id}/members", headers=authorization(outsider_token))
    assert blocked_detail.status_code == 404
    assert blocked_members.status_code == 404


def test_member_cannot_add_workspace_members() -> None:
    owner_token = register("owner@example.com")
    member_token = register("member@example.com")
    organization_id = client.post(
        "/api/organizations", json={"name": "Acme"}, headers=authorization(owner_token)
    ).json()["id"]
    assert client.post(
        f"/api/organizations/{organization_id}/members",
        json={"email": "member@example.com"},
        headers=authorization(owner_token),
    ).status_code == 201

    response = client.post(
        f"/api/organizations/{organization_id}/members",
        json={"email": "owner@example.com"},
        headers=authorization(member_token),
    )
    assert response.status_code == 403
