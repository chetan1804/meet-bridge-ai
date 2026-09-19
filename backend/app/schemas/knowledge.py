from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    title: str = Field(default="Untitled")
    content: str = Field(..., min_length=1)


class KnowledgeRetrievalRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question or topic to retrieve supporting evidence for.")
    documents: list[KnowledgeDocument] = Field(default_factory=list, description="Candidate knowledge documents to search.")


class KnowledgeRetrievalResult(BaseModel):
    title: str
    content: str
    score: float = Field(..., ge=0.0, le=1.0)
