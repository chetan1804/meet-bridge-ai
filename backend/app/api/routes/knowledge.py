from fastapi import APIRouter

from app.schemas.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentCreate,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalResult,
)
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
service = KnowledgeService()

_documents: list[KnowledgeDocument] = [
    KnowledgeDocument(
        id="demo-doc-1",
        title="RAG tuning guide",
        content="Measure recall and precision on a labeled dataset before changing chunking or reranking.",
        source="internal-docs",
        metadata={"topic": "retrieval"},
    )
]


@router.get("/documents", response_model=list[KnowledgeDocument])
def list_documents() -> list[KnowledgeDocument]:
    return _documents


@router.post("/documents", response_model=KnowledgeDocument)
def create_document(payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
    document = KnowledgeDocument(**payload.model_dump())
    _documents.append(document)
    return document


@router.post("/search", response_model=list[KnowledgeRetrievalResult])
def search_documents(payload: KnowledgeRetrievalRequest) -> list[KnowledgeRetrievalResult]:
    candidate_documents = [
        {"title": document.title, "content": document.content}
        for document in (payload.documents or list_documents())
    ]
    matches = service.retrieve(payload.question, candidate_documents)
    return [
        KnowledgeRetrievalResult(title=item.title, content=item.content, score=item.score)
        for item in matches
    ]
