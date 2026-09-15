from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_conversation_buffer_route_adds_and_analyzes_utterance() -> None:
    response = client.post("/api/conversation/buffer", json={"utterance": "How would you improve RAG accuracy?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"] == "How would you improve RAG accuracy?"
    assert payload["is_question"] is True
    assert payload["question_type"] == "how-to"


def test_conversation_context_route_returns_window() -> None:
    client.post("/api/conversation/buffer", json={"utterance": "We should evaluate retrieval quality."})
    client.post("/api/conversation/buffer", json={"utterance": "How would you improve RAG accuracy?"})

    response = client.get("/api/conversation/context")

    assert response.status_code == 200
    payload = response.json()
    assert "How would you improve RAG accuracy?" in payload["context"]
