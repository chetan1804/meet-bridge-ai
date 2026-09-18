from fastapi.testclient import TestClient

from app.main import app
from app.services.meeting_state_service import service


client = TestClient(app)


def setup_function() -> None:
    service.reset()


def test_get_meeting_state() -> None:
    response = client.get("/api/meeting/state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Q3 Product Review"
    assert payload["current_question"] == "How would you improve RAG accuracy?"


def test_update_meeting_state() -> None:
    response = client.post(
        "/api/meeting/state",
        json={
            "meeting_id": "demo-meeting",
            "title": "Q3 Product Review",
            "current_question": "What is the main bottleneck?",
            "why_they_are_asking": "They want the biggest blocker.",
            "important_topics": ["retrieval latency", "indexing"],
            "suggested_answer": "The main bottleneck is likely retrieval quality.",
            "transcript": ["We are reviewing retrieval performance."],
            "listening": True,
            "connected": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_question"] == "What is the main bottleneck?"
    assert payload["important_topics"] == ["retrieval latency", "indexing"]


def test_meeting_state_includes_structured_insights() -> None:
    response = client.get("/api/meeting/state")

    assert response.status_code == 200
    payload = response.json()
    assert "meeting_insights" in payload
    assert "retrieval" in payload["meeting_insights"]["summary"].lower()
    assert payload["meeting_insights"]["open_questions"]
