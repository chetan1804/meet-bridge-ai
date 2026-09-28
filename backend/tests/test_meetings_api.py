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


def test_meeting_crud_is_scoped_to_workspace() -> None:
    owner_token = register("owner@example.com")
    member_token = register("member@example.com")

    organization = client.post(
        "/api/organizations",
        json={"name": "Acme"},
        headers=authorization(owner_token),
    )
    workspace_id = organization.json()["id"]

    meeting = client.post(
        f"/api/organizations/{workspace_id}/meetings",
        headers=authorization(owner_token),
        json={"title": "Q3 planning review"},
    )
    assert meeting.status_code == 201
    meeting_id = meeting.json()["id"]

    listed = client.get(
        f"/api/organizations/{workspace_id}/meetings",
        headers=authorization(owner_token),
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [meeting_id]

    single = client.get(
        f"/api/organizations/{workspace_id}/meetings/{meeting_id}",
        headers=authorization(owner_token),
    )
    assert single.status_code == 200
    assert single.json()["title"] == "Q3 planning review"

    updated = client.patch(
        f"/api/organizations/{workspace_id}/meetings/{meeting_id}",
        headers=authorization(owner_token),
        json={"title": "Q3 roadmap review", "status": "LIVE"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Q3 roadmap review"
    assert updated.json()["status"] == "LIVE"

    blocked = client.get(
        f"/api/organizations/{workspace_id}/meetings/{meeting_id}",
        headers=authorization(member_token),
    )
    assert blocked.status_code == 404
