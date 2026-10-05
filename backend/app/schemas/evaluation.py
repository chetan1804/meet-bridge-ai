import re

from pydantic import BaseModel, Field


class EvaluationExample(BaseModel):
    id: str
    question: str
    answer: str
    expected_contexts: list[str] = Field(default_factory=list)
    ground_truth: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)


class EvaluationScoreRequest(BaseModel):
    question: str = Field(..., min_length=2)
    answer: str = Field(..., min_length=1)
    retrieved_contexts: list[str] = Field(default_factory=list)
    expected_contexts: list[str] = Field(default_factory=list)
    ground_truth: str = ""
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0)


class EvaluationScoreResult(BaseModel):
    retrieval_relevance: float
    context_precision: float
    context_recall: float
    answer_relevance: float
    groundedness: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    estimated_cost_usd: float


def token_set(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]+", value.lower()) if len(token) > 2}
