from __future__ import annotations

import re

from app.schemas.question import QuestionDetectionRequest, QuestionDetectionResult, IntentUnderstandingResult


QUESTION_MARKERS = ("?", "how", "what", "why", "when", "where", "can", "could", "would", "should", "is", "are", "do", "does", "did")


class QuestionService:
    """Deterministic question detection and intent understanding."""

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
        q = question.strip()
        lowered = q.lower()

        if any(marker in lowered for marker in ("how", "improve", "optimize", "best")):
            intent = "Improve process or approach"
            why = "The speaker is seeking a practical recommendation or optimization strategy."
            expected = "actionable guidance"
            topics = ["process improvement", "best practices", "implementation strategy"]
            context = ["current workflow", "constraints", "success metrics"]
        elif any(marker in lowered for marker in ("what", "why", "when", "where")):
            intent = "Clarify facts or context"
            why = "The speaker wants a clearer explanation or better understanding of the situation."
            expected = "explanation"
            topics = ["context", "background", "trade-offs"]
            context = ["relevant background", "known constraints"]
        elif any(marker in lowered for marker in ("can", "could", "would")):
            intent = "Assess feasibility"
            why = "The speaker is evaluating whether an approach is realistic or achievable."
            expected = "feasibility assessment"
            topics = ["capability", "resource constraints", "risk"]
            context = ["technical constraints", "team capacity", "timeline"]
        else:
            intent = "General inquiry"
            why = "The speaker is asking for guidance or an evaluation."
            expected = "brief explanation"
            topics = ["context", "trade-offs", "recommendation"]
            context = ["meeting context", "known facts"]

        confidence = 0.87

        return IntentUnderstandingResult(
            question=q,
            intent=intent,
            why_they_are_asking=why,
            expected_answer_type=expected,
            important_topics=topics,
            context_needed=context,
            confidence=confidence,
        )

    def build_suggested_response(
        self,
        question: str,
        intent: str | None = None,
        important_topics: list[str] | None = None,
    ) -> str:
        q = question.strip()
        lowered = q.lower()
        topics = important_topics or []

        if not q:
            return "I would first clarify the goal, then recommend the simplest, most measurable next step."

        if intent and "improve" in intent.lower():
            topic_text = ", ".join(topics) if topics else "retrieval quality"
            return (
                "I would start by measuring the current retrieval quality and isolating whether the issue is chunking, indexing, or ranking. "
                f"Then I would test the highest-impact changes around {topic_text}, validate them on a small benchmark, and only scale up once the metrics improve."
            )

        if any(keyword in lowered for keyword in ("what", "why", "when", "where")):
            return (
                "I would explain the context first, separate facts from assumptions, and answer with the most relevant evidence before suggesting a next step."
            )

        if any(keyword in lowered for keyword in ("can", "could", "would", "should")):
            return (
                "I would assess feasibility by checking constraints, trade-offs, and the simplest path to a working solution before recommending a final approach."
            )

        return (
            "I would focus on the most likely root cause, validate the assumption with the clearest evidence, and recommend the smallest measurable next step."
        )

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
