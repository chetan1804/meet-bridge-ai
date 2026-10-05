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


def test_evaluation_dataset_and_scoring_are_available() -> None:
    token = register("analyst@example.com")

    sample_dataset = client.get("/api/evaluation/dataset", headers=authorization(token))
    assert sample_dataset.status_code == 200
    dataset = sample_dataset.json()
    assert len(dataset) >= 1
    assert dataset[0]["question"]

    score = client.post(
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
            "completion_tokens": 90,
            "latency_ms": 420,
        },
        headers=authorization(token),
    )
    assert score.status_code == 200
    payload = score.json()
    assert 0.0 <= payload["retrieval_relevance"] <= 1.0
    assert 0.0 <= payload["context_precision"] <= 1.0
    assert 0.0 <= payload["context_recall"] <= 1.0
    assert 0.0 <= payload["answer_relevance"] <= 1.0
    assert 0.0 <= payload["groundedness"] <= 1.0
    assert payload["total_tokens"] == 210
    assert payload["estimated_cost_usd"] > 0
