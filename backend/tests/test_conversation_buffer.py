from app.services.conversation_buffer import ConversationBufferService


def test_buffer_keeps_recent_utterances() -> None:
    service = ConversationBufferService(max_turns=3)

    service.add_utterance("We should evaluate retrieval quality.")
    service.add_utterance("What is the main bottleneck?")
    service.add_utterance("The chunking strategy looks weak.")
    service.add_utterance("How would you improve RAG accuracy?")

    context = service.get_context_window()

    assert context.count("How would you improve RAG accuracy?") == 1
    assert len(service.buffer) == 3
    assert service.buffer[0].endswith("What is the main bottleneck?")
    assert service.buffer[-1].endswith("How would you improve RAG accuracy?")


def test_buffer_detects_latest_question() -> None:
    service = ConversationBufferService(max_turns=5)
    service.add_utterance("We are reviewing retrieval quality.")
    service.add_utterance("How would you improve RAG accuracy?")

    result = service.analyze_latest_turn()

    assert result is not None
    assert result["is_question"] is True
    assert result["question_type"] == "how-to"


def test_buffer_ignores_non_question_statement() -> None:
    service = ConversationBufferService(max_turns=5)
    service.add_utterance("We should evaluate retrieval quality before changing prompts.")

    result = service.analyze_latest_turn()

    assert result is None
