from __future__ import annotations

from collections import deque
from typing import Any

from app.services.question_service import QuestionService


class ConversationBufferService:
    """Simple rolling transcript buffer used to accumulate recent utterances and detect questions."""

    def __init__(self, max_turns: int = 10) -> None:
        self.max_turns = max_turns
        self.buffer: deque[str] = deque(maxlen=max_turns)
        self.question_service = QuestionService()

    def add_utterance(self, utterance: str) -> None:
        cleaned = utterance.strip()
        if cleaned:
            self.buffer.append(cleaned)

    def get_context_window(self) -> str:
        return "\n".join(self.buffer)

    def analyze_latest_turn(self) -> dict[str, Any] | None:
        if not self.buffer:
            return None

        latest = self.buffer[-1]
        detection = self.question_service.detect_question(type("Payload", (), {"text": latest})())

        if not detection.is_question:
            return None

        intent = self.question_service.understand_intent(detection.question)

        return {
            "is_question": detection.is_question,
            "confidence": detection.confidence,
            "question": detection.question,
            "question_type": detection.question_type,
            "requires_response": detection.requires_response,
            "intent": intent.intent,
            "why_they_are_asking": intent.why_they_are_asking,
            "expected_answer_type": intent.expected_answer_type,
            "important_topics": intent.important_topics,
            "context_needed": intent.context_needed,
        }
