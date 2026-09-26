import pytest

from app.schemas.audio import AudioChunkMessage
from app.services.speech_provider import MockSpeechToTextProvider, get_speech_provider


def test_mock_speech_provider_returns_structured_transcript_event() -> None:
    event = MockSpeechToTextProvider().transcribe_chunk(
        AudioChunkMessage(type="audio_chunk", mime_type="audio/webm", data="YXVkaW8=")
    )

    assert event.provider == "mock"
    assert event.is_final is False
    assert event.text.startswith("Mock transcript received")


def test_unknown_speech_provider_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported speech provider"):
        get_speech_provider("unknown")