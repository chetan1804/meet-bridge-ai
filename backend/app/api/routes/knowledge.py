from fastapi import APIRouter

from app.schemas.knowledge import KnowledgeDocument, KnowledgeDocumentCreate

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

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
