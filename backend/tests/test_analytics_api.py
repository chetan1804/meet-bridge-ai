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


def test_usage_metrics_are_recorded_and_exposed() -> None:
    token = register("owner@example.com")

    response = client.post(
        "/api/analytics/usage/record",
        json={
            "event_type": "llm",
            "prompt_tokens": 1200,
            "completion_tokens": 400,
            "latency_ms": 2800,
            "stt_minutes": 2.5,
        },
        headers=authorization(token),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ai_requests"] == 1
    assert payload["total_tokens"] == 1600
    assert payload["stt_minutes"] == 2.5
    assert payload["avg_latency_ms"] == 2800
    assert payload["estimated_cost_usd"] > 0

    summary = client.get("/api/analytics/usage", headers=authorization(token))
    assert summary.status_code == 200
    assert summary.json()["ai_requests"] == 1
    assert summary.json()["total_tokens"] == 1600
