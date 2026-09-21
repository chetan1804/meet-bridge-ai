from __future__ import annotations

from app.schemas.knowledge import KnowledgeDocument, KnowledgeDocumentCreate

_documents: list[KnowledgeDocument] = [
    KnowledgeDocument(
        id="demo-doc-1",
        title="RAG tuning guide",
        content="Measure recall and precision on a labeled dataset before changing chunking or reranking.",
        source="internal-docs",
        metadata={"topic": "retrieval"},
    ),
    KnowledgeDocument(
        id="demo-doc-2",
        title="Chunking best practices",
        content="Use smaller chunks and metadata filters to improve recall across long transcripts.",
        source="internal-docs",
        metadata={"topic": "chunking"},
    ),
]


def list_knowledge_documents() -> list[KnowledgeDocument]:
    return list(_documents)


def add_knowledge_document(payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
    document = KnowledgeDocument(**payload.model_dump())
    _documents.append(document)
    return document
