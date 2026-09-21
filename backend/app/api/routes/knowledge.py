from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.schemas.knowledge import (
    KnowledgeDocument,
    KnowledgeDocumentCreate,
    KnowledgeRetrievalRequest,
    KnowledgeRetrievalResult,
)
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_store import add_knowledge_document, list_knowledge_documents

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
service = KnowledgeService()


@router.get("/documents", response_model=list[KnowledgeDocument])
def list_documents() -> list[KnowledgeDocument]:
    return list_knowledge_documents()


@router.post("/documents", response_model=KnowledgeDocument)
def create_document(payload: KnowledgeDocumentCreate) -> KnowledgeDocument:
    return add_knowledge_document(payload)


@router.post("/documents/upload", response_model=KnowledgeDocument)
async def upload_document(file: UploadFile = File(...)) -> KnowledgeDocument:
    content = await file.read()
    text = content.decode("utf-8", errors="replace").strip()
    if not text:
        raise ValueError("Uploaded file is empty.")

    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    payload = KnowledgeDocumentCreate(
        title=file.filename or "uploaded-document",
        content=cleaned,
        source="upload",
        metadata={"format": file.content_type or "text/plain"},
    )
    return add_knowledge_document(payload)


@router.post("/search", response_model=list[KnowledgeRetrievalResult])
def search_documents(payload: KnowledgeRetrievalRequest) -> list[KnowledgeRetrievalResult]:
    candidate_documents = [
        {"title": document.title, "content": document.content}
        for document in (payload.documents or list_knowledge_documents())
    ]
    matches = service.retrieve(payload.question, candidate_documents)
    return [
        KnowledgeRetrievalResult(title=item.title, content=item.content, score=item.score)
        for item in matches
    ]
