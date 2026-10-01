from __future__ import annotations

import re

from app.schemas.question import (
    IntentUnderstandingResult,
    QuestionDetectionRequest,
    QuestionDetectionResult,
)
from app.core.config import get_settings
from app.services.llm_provider import get_llm_provider


INDIRECT_QUESTION_CUES = (
    "i wonder if",
    "i'm wondering if",
    "im wondering if",
    "i'd like to know",
    "id like to know",
    "could you",
    "would you",
    "please explain",
    "tell me",
    "show me",
    "walk me through",
    "we need to decide",
)


class QuestionService:
    """Deterministic question detection and intent understanding."""

    def __init__(self) -> None:
        settings = get_settings()
        self.llm_provider = get_llm_provider(
            settings.llm_provider,
            settings.ollama_base_url,
            settings.ollama_model,
            settings.openai_api_key,
            settings.openai_model,
        )

    def detect_question(self, payload: QuestionDetectionRequest) -> QuestionDetectionResult:
        text = payload.text.strip()
        lowered = text.lower()

        if "?" in text:
            is_question, confidence = True, 0.98
        elif re.match(
            r"^(how|what|why|when|where|who|which|can|could|would|should|do|does|did|is|are|am|was|were|have|has|had|may|might)\b",
            lowered,
        ):
            is_question, confidence = True, 0.94
        elif any(cue in lowered for cue in INDIRECT_QUESTION_CUES):
            result = self.llm_provider.detect_question(text)
            question_type = result.question_type
            if result.is_question and question_type == "general":
                question_type = self._infer_question_type(text)
            return result.model_copy(
                update={
                    "question": text if result.is_question else "",
                    "question_type": question_type,
                    "requires_response": result.is_question,
                }
            )
        else:
            is_question, confidence = False, 0.15

        return QuestionDetectionResult(
            is_question=is_question,
            confidence=confidence,
            question=text if is_question else "",
            question_type=self._infer_question_type(text),
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
