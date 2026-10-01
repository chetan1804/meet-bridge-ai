from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

from app.schemas.question import IntentUnderstandingResult, QuestionDetectionResult


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def detect_question(self, text: str) -> QuestionDetectionResult:
        """Classify ambiguous transcript text as a question or response-worthy request."""

    @abstractmethod
    def understand_intent(self, question: str) -> IntentUnderstandingResult:
        """Return structured intent data for a completed question."""

    @abstractmethod
    def build_suggested_response(
        self,
        question: str,
        intent: str | None = None,
        important_topics: list[str] | None = None,
    ) -> str:
        """Generate a response using structured meeting context."""


class MockLLMProvider(LLMProvider):
    name = "mock"

    def detect_question(self, text: str) -> QuestionDetectionResult:
        lowered = text.strip().lower()
        indirect_cues = (
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
        is_question = any(cue in lowered for cue in indirect_cues)
        return QuestionDetectionResult(
            is_question=is_question,
            confidence=0.72 if is_question else 0.28,
            question=text.strip() if is_question else "",
            question_type="general",
            requires_response=is_question,
        )

    def understand_intent(self, question: str) -> IntentUnderstandingResult:
        q = question.strip()
        lowered = q.lower()
        if any(marker in lowered for marker in ("how", "improve", "optimize", "best")):
            intent, why, expected = "Improve process or approach", "The speaker is seeking a practical recommendation or optimization strategy.", "actionable guidance"
            topics, context = ["process improvement", "best practices", "implementation strategy"], ["current workflow", "constraints", "success metrics"]
        elif any(marker in lowered for marker in ("what", "why", "when", "where")):
            intent, why, expected = "Clarify facts or context", "The speaker wants a clearer explanation or better understanding of the situation.", "explanation"
            topics, context = ["context", "background", "trade-offs"], ["relevant background", "known constraints"]
        elif any(marker in lowered for marker in ("can", "could", "would")):
            intent, why, expected = "Assess feasibility", "The speaker is evaluating whether an approach is realistic or achievable.", "feasibility assessment"
            topics, context = ["capability", "resource constraints", "risk"], ["technical constraints", "team capacity", "timeline"]
        else:
            intent, why, expected = "General inquiry", "The speaker is asking for guidance or an evaluation.", "brief explanation"
            topics, context = ["context", "trade-offs", "recommendation"], ["meeting context", "known facts"]
        return IntentUnderstandingResult(
            question=q,
            intent=intent,
            why_they_are_asking=why,
            expected_answer_type=expected,
            important_topics=topics,
            context_needed=context,
            confidence=0.87,
        )

    def build_suggested_response(self, question: str, intent: str | None = None, important_topics: list[str] | None = None) -> str:
        q = question.strip()
        lowered = q.lower()
        if not q:
            return "I would first clarify the goal, then recommend the simplest, most measurable next step."
        if intent and "improve" in intent.lower():
            topic_text = ", ".join(important_topics or []) or "retrieval quality"
            return f"I would start by measuring the current retrieval quality and isolating whether the issue is chunking, indexing, or ranking. Then I would test the highest-impact changes around {topic_text}, validate them on a small benchmark, and only scale up once the metrics improve."
        if any(keyword in lowered for keyword in ("what", "why", "when", "where")):
            return "I would explain the context first, separate facts from assumptions, and answer with the most relevant evidence before suggesting a next step."
        if any(keyword in lowered for keyword in ("can", "could", "would", "should")):
            return "I would assess feasibility by checking constraints, trade-offs, and the simplest path to a working solution before recommending a final approach."
        return "I would focus on the most likely root cause, validate the assumption with the clearest evidence, and recommend the smallest measurable next step."


class OllamaLLMProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def detect_question(self, text: str) -> QuestionDetectionResult:
        return self._generate_structured(
            "Decide whether this transcript utterance asks a question or requests a response. "
            "Do not classify ordinary statements as questions.",
            text,
            QuestionDetectionResult,
        )

    def understand_intent(self, question: str) -> IntentUnderstandingResult:
        return self._generate_structured(
            "Understand the intent of the question. Return concise, evidence-aware fields.",
            question,
            IntentUnderstandingResult,
        )

    def build_suggested_response(self, question: str, intent: str | None = None, important_topics: list[str] | None = None) -> str:
        result = self._generate_structured(
            "Draft a concise, natural response for a meeting participant. Do not invent facts.",
            f"Question: {question}\nIntent: {intent or 'unspecified'}\nImportant topics: {', '.join(important_topics or [])}",
            SuggestedResponse,
        )
        return result.response

    def _generate_structured(
        self, instructions: str, prompt: str, response_model: type[BaseModel]
    ) -> BaseModel:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt},
                ],
                "format": response_model.model_json_schema(),
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return response_model.model_validate_json(content)


class SuggestedResponse(BaseModel):
    response: str


def _strict_json_schema(response_model: type[BaseModel]) -> dict[str, object]:
    schema = response_model.model_json_schema()
    schema["additionalProperties"] = False
    return schema


class OpenAILLMProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when using the OpenAI provider.")
        self.api_key = api_key
        self.model = model

    def detect_question(self, text: str) -> QuestionDetectionResult:
        return self._generate_structured(
            "Decide whether this transcript utterance asks a question or requests a response. "
            "Do not classify ordinary statements as questions.",
            text,
            QuestionDetectionResult,
        )

    def understand_intent(self, question: str) -> IntentUnderstandingResult:
        return self._generate_structured(
            "Understand the intent of the question. Return concise, evidence-aware fields.",
            question,
            IntentUnderstandingResult,
        )

    def build_suggested_response(self, question: str, intent: str | None = None, important_topics: list[str] | None = None) -> str:
        result = self._generate_structured(
            "Draft a concise, natural response for a meeting participant. Do not invent facts.",
            f"Question: {question}\nIntent: {intent or 'unspecified'}\nImportant topics: {', '.join(important_topics or [])}",
            SuggestedResponse,
        )
        return result.response

    def _generate_structured(
        self, instructions: str, prompt: str, response_model: type[BaseModel]
    ) -> BaseModel:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "meeting_response",
                        "strict": True,
                        "schema": _strict_json_schema(response_model),
                    },
                },
                "temperature": 0,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return response_model.model_validate_json(content)


def get_llm_provider(
    provider_name: str,
    ollama_base_url: str,
    ollama_model: str,
    openai_api_key: str = "",
    openai_model: str = "gpt-4o-mini",
) -> LLMProvider:
    if provider_name == "mock":
        return MockLLMProvider()
    if provider_name == "ollama":
        return OllamaLLMProvider(ollama_base_url, ollama_model)
    if provider_name == "openai":
        return OpenAILLMProvider(openai_api_key, openai_model)
    raise ValueError(f"Unsupported LLM provider: {provider_name}")