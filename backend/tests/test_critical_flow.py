from fastapi.testclient import TestClient

from app.db.base import Base
from app.main import app
from tests.conftest import engine


client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_end_to_end_meeting_and_rag_flow() -> None:
    auth = client.post(
        "/api/auth/register",
        json={"email": "critical-flow@example.com", "password": "a-long-secret-password"},
    )
    token = auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    orgs = client.get("/api/organizations", headers=headers)
    assert orgs.status_code == 200
    organization = orgs.json()[0]

    meeting = client.post(
        f"/api/organizations/{organization['id']}/meetings",
        headers=headers,
        json={"title": "RAG QA review"},
    )
    assert meeting.status_code == 201
    meeting_id = meeting.json()["id"]

    response = client.post(
        "/api/conversation/buffer",
        json={"utterance": "How do we improve retrieval quality for RAG?"},
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_question"] is True
    assert payload["question_type"] == "how-to"

    state = client.get("/api/meeting/state", headers=headers)
    assert state.status_code == 200
    meeting_state = state.json()
    assert meeting_state["current_question"] == "How do we improve retrieval quality for RAG?"
    assert "How do we improve retrieval quality for RAG?" in meeting_state["transcript"]

    search = client.get(
        "/api/meeting/search?q=retrieval%20quality%20RAG",
        headers=headers,
    )
    assert search.status_code == 200
    results = search.json()
    assert isinstance(results, list)

    evaluation = client.post(
        "/api/evaluation/score",
        json={
            "question": "How do we improve retrieval quality for RAG?",
            "answer": "Improve retrieval quality by tuning chunking and reranking.",
            "retrieved_contexts": [
                "Chunking and reranking improve retrieval quality in RAG systems.",
                "Answer relevance matters when selecting evidence.",
            ],
            "expected_contexts": [
                "Chunking and reranking improve retrieval quality in RAG systems.",
            ],
            "prompt_tokens": 120,
            "completion_tokens": 80,
            "latency_ms": 310,
        },
        headers=headers,
    )
    assert evaluation.status_code == 200
    score = evaluation.json()
    assert score["total_tokens"] == 200
    assert score["estimated_cost_usd"] > 0

    websocket = client.websocket_connect(
        f"/api/ws/organizations/{organization['id']}/meetings/{meeting_id}?token={token}"
    )
    with websocket:
        assert websocket.receive_json() == {"type": "connected", "meeting_id": meeting_id}
        websocket.send_json({"type": "ping"})
        assert websocket.receive_json() == {"type": "pong"}
