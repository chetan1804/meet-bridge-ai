from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field


class KnowledgeDocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Document title")
    content: str = Field(..., min_length=1, description="Knowledge base content")
    source: str = Field(default="manual", min_length=1, description="Source label")
    metadata: dict[str, str] = Field(default_factory=dict, description="Optional metadata")


class KnowledgeDocument(KnowledgeDocumentCreate):
    id: str = Field(default_factory=lambda: uuid4().hex)


class KnowledgeRetrievalRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question or topic to retrieve supporting evidence for.")
    documents: list[KnowledgeDocument] = Field(default_factory=list, description="Candidate knowledge documents to search.")


class KnowledgeRetrievalResult(BaseModel):
    title: str
    content: str
    score: float = Field(..., ge=0.0, le=1.0)
