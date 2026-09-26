from abc import ABC, abstractmethod

from app.schemas.question import IntentUnderstandingResult


class LLMProvider(ABC):
    name: str

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
        self.base_url = base_url
        self.model = model

    def understand_intent(self, question: str) -> IntentUnderstandingResult:
        raise RuntimeError("Ollama structured intent generation is not enabled yet.")

    def build_suggested_response(self, question: str, intent: str | None = None, important_topics: list[str] | None = None) -> str:
        raise RuntimeError("Ollama response generation is not enabled yet.")


def get_llm_provider(provider_name: str, ollama_base_url: str, ollama_model: str) -> LLMProvider:
    if provider_name == "mock":
        return MockLLMProvider()
    if provider_name == "ollama":
        return OllamaLLMProvider(ollama_base_url, ollama_model)
    raise ValueError(f"Unsupported LLM provider: {provider_name}")