import pytest

from app.services.llm_provider import MockLLMProvider, OllamaLLMProvider, get_llm_provider


def test_mock_provider_returns_structured_intent_and_response() -> None:
    provider = MockLLMProvider()
    result = provider.understand_intent("How would you improve RAG accuracy?")
    assert result.intent == "Improve process or approach"
    assert "retrieval metrics" in provider.build_suggested_response(result.question, result.intent, ["retrieval metrics"])


def test_provider_factory_supports_mock_and_ollama_architecture() -> None:
    assert get_llm_provider("mock", "http://localhost:11434", "llama3.2").name == "mock"
    assert isinstance(get_llm_provider("ollama", "http://localhost:11434", "llama3.2"), OllamaLLMProvider)


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider("unknown", "http://localhost:11434", "llama3.2")