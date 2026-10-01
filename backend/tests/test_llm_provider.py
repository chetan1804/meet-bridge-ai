import hmac

import pytest

from app.core.config import get_settings
from app.services.llm_provider import (
    MockLLMProvider,
    OllamaLLMProvider,
    OpenAILLMProvider,
    get_llm_provider,
)


def test_mock_provider_returns_structured_intent_and_response() -> None:
    provider = MockLLMProvider()
    result = provider.understand_intent("How would you improve RAG accuracy?")
    assert result.intent == "Improve process or approach"
    assert "retrieval metrics" in provider.build_suggested_response(result.question, result.intent, ["retrieval metrics"])


def test_provider_factory_supports_mock_and_ollama_architecture() -> None:
    assert get_llm_provider("mock", "http://localhost:11434", "llama3.2").name == "mock"
    assert isinstance(get_llm_provider("ollama", "http://localhost:11434", "llama3.2"), OllamaLLMProvider)
    settings = get_settings()
    if not settings.openai_api_key:
        pytest.skip("OPENAI_API_KEY is not configured")
    assert isinstance(
        get_llm_provider(
            "openai",
            settings.ollama_base_url,
            settings.ollama_model,
            settings.openai_api_key,
            settings.openai_model,
        ),
        OpenAILLMProvider,
    )


def test_ollama_provider_parses_structured_intent(monkeypatch: pytest.MonkeyPatch) -> None:
    import json

    from app.schemas.question import IntentUnderstandingResult

    expected = IntentUnderstandingResult(
        question="How can we improve retrieval?",
        intent="Improve retrieval quality",
        why_they_are_asking="They need a practical plan.",
        expected_answer_type="actionable guidance",
        important_topics=["evaluation"],
        context_needed=["current metrics"],
        confidence=0.9,
    )
    request: dict[str, object] = {}

    class Response:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"message": {"content": expected.model_dump_json()}}

    def fake_post(url: str, **kwargs: object) -> Response:
        request["url"] = url
        request.update(kwargs)
        return Response()

    monkeypatch.setattr("app.services.llm_provider.httpx.post", fake_post)
    result = OllamaLLMProvider("http://localhost:11434/", "llama3.2").understand_intent(
        expected.question
    )

    assert result == expected
    assert request["url"] == "http://localhost:11434/api/chat"
    assert request["json"]["format"] == IntentUnderstandingResult.model_json_schema()
    assert json.loads(expected.model_dump_json())["question"] == expected.question


def test_openai_provider_uses_strict_structured_output(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = get_settings()
    if not settings.openai_api_key:
        pytest.skip("OPENAI_API_KEY is not configured")
    response_text = '{"response":"Measure retrieval quality against a labeled benchmark."}'
    request: dict[str, object] = {}

    class Response:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {"choices": [{"message": {"content": response_text}}]}

    def fake_post(url: str, **kwargs: object) -> Response:
        request["url"] = url
        request.update(kwargs)
        return Response()

    monkeypatch.setattr("app.services.llm_provider.httpx.post", fake_post)
    result = OpenAILLMProvider(settings.openai_api_key, settings.openai_model).build_suggested_response(
        "How do we improve retrieval?", important_topics=["evaluation"]
    )

    assert result == "Measure retrieval quality against a labeled benchmark."
    authorization = request["headers"]["Authorization"]
    assert hmac.compare_digest(authorization, f"Bearer {settings.openai_api_key}")
    assert request["json"]["response_format"]["type"] == "json_schema"
    assert request["json"]["model"] == settings.openai_model
    assert (
        request["json"]["response_format"]["json_schema"]["schema"]["additionalProperties"]
        is False
    )


def test_openai_provider_requires_api_key() -> None:
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        get_llm_provider("openai", "http://localhost:11434", "llama3.2")


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        get_llm_provider("unknown", "http://localhost:11434", "llama3.2")