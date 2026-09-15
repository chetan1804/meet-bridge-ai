from pydantic import BaseModel, Field


class ConversationBufferRequest(BaseModel):
    utterance: str = Field(..., min_length=1, description="Transcript chunk or utterance to append to the live conversation buffer.")


class ConversationBufferResponse(BaseModel):
    is_question: bool
    confidence: float
    question: str
    question_type: str
    requires_response: bool
    intent: str | None = None
    why_they_are_asking: str | None = None
    expected_answer_type: str | None = None
    important_topics: list[str] | None = None
    context_needed: list[str] | None = None


class ConversationContextResponse(BaseModel):
    context: str
