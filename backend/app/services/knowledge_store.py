from __future__ import annotations

from app.schemas.knowledge import KnowledgeDocument, KnowledgeDocumentCreate

_documents: list[KnowledgeDocument] = [
    KnowledgeDocument(
        id="demo-doc-1",
        title="RAG tuning guide",
        content="Measure recall and precision on a labeled dataset before changing chunking or reranking.",
        source="internal-docs",
        workspace_id="default-workspace",
        owner_id="system",
        visibility="workspace",
        metadata={"topic": "retrieval"},
    ),
    KnowledgeDocument(
        id="demo-doc-2",
        title="Chunking best practices",
        content="Use smaller chunks and metadata filters to improve recall across long transcripts.",
        source="internal-docs",
        workspace_id="default-workspace",
        owner_id="system",
        visibility="workspace",
        metadata={"topic": "chunking"},
    ),
]


def list_knowledge_documents(
    workspace_id: str | None = None,
    owner_id: str | None = None,
    visibility: str | None = None,
) -> list[KnowledgeDocument]:
    filtered = list(_documents)
    if workspace_id is not None:
        filtered = [doc for doc in filtered if doc.workspace_id == workspace_id]
    if owner_id is not None:
        filtered = [doc for doc in filtered if doc.owner_id == owner_id]
    if visibility is not None:
        filtered = [doc for doc in filtered if doc.visibility == visibility]
    return filtered


def add_knowledge_document(payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
    document = KnowledgeDocument(**payload.model_dump())
    _documents.append(document)
    return document
