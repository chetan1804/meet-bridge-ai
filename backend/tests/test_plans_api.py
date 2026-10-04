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


def test_plan_catalog_and_usage_limits_are_exposed() -> None:
    token = register("owner@example.com")

    catalog = client.get("/api/plans", headers=authorization(token))
    assert catalog.status_code == 200
    keys = {item["key"] for item in catalog.json()}
    assert {"FREE", "PRO", "TEAM"}.issubset(keys)

    plan = client.get("/api/plans/me", headers=authorization(token))
    assert plan.status_code == 200
    assert plan.json()["plan"] == "FREE"

    upgrade = client.post(
        "/api/plans/me",
        json={"plan": "PRO"},
        headers=authorization(token),
    )
    assert upgrade.status_code == 200
    assert upgrade.json()["plan"] == "PRO"

    blocked = client.post(
        "/api/plans/usage/record",
        json={"feature": "ai_requests", "amount": 2},
        headers=authorization(token),
    )
    assert blocked.status_code == 200

    over_limit = client.post(
        "/api/plans/usage/record",
        json={"feature": "ai_requests", "amount": 9000},
        headers=authorization(token),
    )
    assert over_limit.status_code == 403
