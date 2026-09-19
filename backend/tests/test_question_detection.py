from app.schemas.question import QuestionDetectionRequest
from app.services.question_service import QuestionService


def test_detect_question_for_obvious_question() -> None:
    result = QuestionService().detect_question(QuestionDetectionRequest(text="How would you improve RAG accuracy?"))

    assert result.is_question is True
    assert result.requires_response is True
    assert result.question_type == "how-to"
    assert result.confidence > 0.5


def test_detect_non_question_utterance() -> None:
    result = QuestionService().detect_question(QuestionDetectionRequest(text="We should evaluate retrieval quality before changing prompts."))

    assert result.is_question is False
    assert result.requires_response is False


def test_understand_intent() -> None:
    result = QuestionService().understand_intent("How would you improve RAG accuracy?")

    assert result.intent == "Improve process or approach"
    assert "best practices" in result.important_topics[0] or "process improvement" in result.important_topics[0]
    assert result.confidence > 0.8


def test_build_suggested_response_from_question_and_intent() -> None:
    service = QuestionService()
    question = "How would you improve RAG accuracy?"

    result = service.build_suggested_response(
        question=question,
        intent="Improve process or approach",
        important_topics=["retrieval metrics", "chunking strategy"],
    )

    assert "retrieval" in result.lower()
    assert "chunk" in result.lower() or "metrics" in result.lower()
    assert len(result) > 60
