from pydantic import BaseModel, Field


class UsageRecordRequest(BaseModel):
    event_type: str = Field(default="llm", description="Type of operation, such as llm, stt, or retrieval.")
    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    stt_minutes: float = Field(default=0.0, ge=0.0)
    cost_usd: float | None = Field(default=None, ge=0.0)


class UsageMetrics(BaseModel):
    ai_requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    stt_minutes: float = 0.0
    avg_latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0
