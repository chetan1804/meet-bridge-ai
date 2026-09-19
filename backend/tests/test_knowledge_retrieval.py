from app.services.knowledge_service import KnowledgeService


def test_retrieve_relevant_evidence_for_rag_question() -> None:
    documents = [
        {
            "title": "Retrieval quality tuning",
            "content": "Measure recall and precision on a labeled dataset before changing chunking or reranking.",
        },
        {
            "title": "Meeting follow-up process",
            "content": "Summaries should be concise, action-oriented, and easy to read for a busy team.",
        },
    ]

    result = KnowledgeService().retrieve("How would you improve RAG accuracy?", documents)

    assert result
    assert result[0].title == "Retrieval quality tuning"
    assert result[0].score > 0.5


def test_retrieve_returns_empty_for_blank_query() -> None:
    result = KnowledgeService().retrieve("   ")

    assert result == []
