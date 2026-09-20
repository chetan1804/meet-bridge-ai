from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_list_knowledge_documents() -> None:
    payload = {
        "title": "RAG tuning guide",
        "content": "Measure recall and precision on a labeled dataset before changing chunking or reranking.",
        "source": "internal-docs",
    }

    create_response = client.post("/api/knowledge/documents", json=payload)
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["title"] == "RAG tuning guide"
    assert created["source"] == "internal-docs"

    list_response = client.get("/api/knowledge/documents")
    assert list_response.status_code == 200
    documents = list_response.json()
    assert any(doc["title"] == "RAG tuning guide" for doc in documents)


def test_knowledge_documents_require_content() -> None:
    response = client.post(
        "/api/knowledge/documents",
        json={"title": "Missing content", "source": "internal-docs"},
    )

    assert response.status_code == 422
