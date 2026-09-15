from pydantic import BaseModel, Field


class QuestionDetectionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Transcript chunk or utterance to analyze.")


class QuestionDetectionResult(BaseModel):
    is_question: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    question: str
    question_type: str
    requires_response: bool


class IntentUnderstandingResult(BaseModel):
    question: str
    intent: str
    why_they_are_asking: str
    expected_answer_type: str
    important_topics: list[str]
    context_needed: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
