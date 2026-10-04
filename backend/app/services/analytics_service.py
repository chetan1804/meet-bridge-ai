from __future__ import annotations

from app.schemas.analytics import UsageMetrics, UsageRecordRequest


class UsageAnalyticsService:
    def __init__(self) -> None:
        self.ai_requests = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.stt_minutes = 0.0
        self.total_latency_ms = 0.0
        self.estimated_cost_usd = 0.0

    def record_usage(self, request: UsageRecordRequest) -> UsageMetrics:
        if request.event_type.lower() == "llm":
            self.ai_requests += 1

        self.prompt_tokens += request.prompt_tokens
        self.completion_tokens += request.completion_tokens
        self.stt_minutes += request.stt_minutes
        self.total_latency_ms += request.latency_ms

        if request.cost_usd is not None:
            self.estimated_cost_usd += request.cost_usd
        else:
            self.estimated_cost_usd += self._estimate_cost(request.prompt_tokens, request.completion_tokens)

        return self.get_summary()

    def get_summary(self) -> UsageMetrics:
        total_tokens = self.prompt_tokens + self.completion_tokens
        avg_latency = (self.total_latency_ms / self.ai_requests) if self.ai_requests else 0.0
        return UsageMetrics(
            ai_requests=self.ai_requests,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            total_tokens=total_tokens,
            stt_minutes=round(self.stt_minutes, 2),
            avg_latency_ms=round(avg_latency, 2),
            estimated_cost_usd=round(self.estimated_cost_usd, 6),
        )

    @staticmethod
    def _estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        estimated = ((prompt_tokens * 0.00001) + (completion_tokens * 0.00002))
        return float(estimated)


service = UsageAnalyticsService()
