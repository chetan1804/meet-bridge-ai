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


def test_search_returns_relevant_documents() -> None:
    response = client.post(
        "/api/knowledge/search",
        json={"question": "How can we improve RAG accuracy?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert payload[0]["title"] == "RAG tuning guide"
    assert payload[0]["score"] > 0.5


def test_upload_text_document_to_knowledge_base() -> None:
    response = client.post(
        "/api/knowledge/documents/upload",
        files={"file": ("rag-notes.md", b"# RAG notes\n\nMeasure recall and precision before reranking.", "text/markdown")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "rag-notes.md"
    assert "Measure recall" in payload["content"]


def test_knowledge_documents_can_be_filtered_by_workspace_and_owner() -> None:
    workspace_response = client.post(
        "/api/knowledge/documents",
        json={
            "title": "Workspace retrieval guide",
            "content": "Use metadata filters and reranking to improve recall.",
            "source": "workspace-docs",
            "workspace_id": "workspace-42",
            "owner_id": "team-bot",
            "visibility": "workspace",
        },
    )
    personal_response = client.post(
        "/api/knowledge/documents",
        json={
            "title": "Personal retrieval notes",
            "content": "Measure prompt quality and latency before changing rules.",
            "source": "personal-docs",
            "workspace_id": "workspace-42",
            "owner_id": "user-99",
            "visibility": "personal",
        },
    )

    assert workspace_response.status_code == 200
    assert personal_response.status_code == 200

    filtered_response = client.get(
        "/api/knowledge/documents",
        params={"workspace_id": "workspace-42", "owner_id": "user-99"},
    )
    assert filtered_response.status_code == 200
    payload = filtered_response.json()
    assert payload
    assert all(doc["workspace_id"] == "workspace-42" for doc in payload)
    assert all(doc["owner_id"] == "user-99" for doc in payload)
