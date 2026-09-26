from __future__ import annotations

import re

from app.schemas.question import QuestionDetectionRequest, QuestionDetectionResult, IntentUnderstandingResult
from app.core.config import get_settings
from app.services.llm_provider import get_llm_provider


QUESTION_MARKERS = ("?", "how", "what", "why", "when", "where", "can", "could", "would", "should", "is", "are", "do", "does", "did")


class QuestionService:
    """Deterministic question detection and intent understanding."""

    def __init__(self) -> None:
        settings = get_settings()
        self.llm_provider = get_llm_provider(
            settings.llm_provider,
            settings.ollama_base_url,
            settings.ollama_model,
        )

    def detect_question(self, payload: QuestionDetectionRequest) -> QuestionDetectionResult:
        text = payload.text.strip()
        lowered = text.lower()

        has_question_mark = "?" in text
        starts_with_question_word = bool(re.match(r"^(how|what|why|when|where|who|which|can|could|would|should|do|does|did|is|are|am|was|were|have|has|had|may|might)\b", lowered))

        is_question = bool(has_question_mark or starts_with_question_word)
        confidence = 0.92 if is_question else 0.18

        question = text if is_question else ""
        question_type = self._infer_question_type(text)

        return QuestionDetectionResult(
            is_question=is_question,
            confidence=confidence,
            question=question,
            question_type=question_type,
            requires_response=is_question,
        )

    def understand_intent(self, question: str) -> IntentUnderstandingResult:
        return self.llm_provider.understand_intent(question)

    def build_suggested_response(
        self,
        question: str,
        intent: str | None = None,
        important_topics: list[str] | None = None,
    ) -> str:
        return self.llm_provider.build_suggested_response(question, intent, important_topics)

    def _infer_question_type(self, text: str) -> str:
        lowered = text.lower()
        if re.match(r"^(how|what|why|when|where|who|which|can|could|would|should|do|does|did|is|are|am|was|were|have|has|had|may|might)\b", lowered):
            if any(marker in lowered for marker in ("how", "improve", "optimize", "best")):
                return "how-to"
            if any(marker in lowered for marker in ("what", "which")):
                return "definition"
            if any(marker in lowered for marker in ("why", "cause", "reason")):
                return "why"
            if any(marker in lowered for marker in ("when", "date", "time")):
                return "timing"
            if any(marker in lowered for marker in ("can", "could", "would", "should")):
                return "feasibility"
        if any(marker in lowered for marker in ("how", "improve", "optimize", "best")):
            return "how-to"
        if any(marker in lowered for marker in ("what", "which")):
            return "definition"
        if any(marker in lowered for marker in ("why", "cause", "reason")):
            return "why"
        if any(marker in lowered for marker in ("when", "date", "time")):
            return "timing"
        if any(marker in lowered for marker in ("can", "could", "would", "should")):
            return "feasibility"
        return "general"
