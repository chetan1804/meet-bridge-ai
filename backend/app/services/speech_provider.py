from abc import ABC, abstractmethod

from app.schemas.audio import AudioChunkMessage
from app.schemas.transcript import TranscriptEvent


class SpeechToTextProvider(ABC):
    name: str

    @abstractmethod
    def transcribe_chunk(self, chunk: AudioChunkMessage) -> TranscriptEvent | None:
        """Transcribe one transient audio chunk without retaining its raw payload."""


class MockSpeechToTextProvider(SpeechToTextProvider):
    name = "mock"

    def transcribe_chunk(self, chunk: AudioChunkMessage) -> TranscriptEvent:
        return TranscriptEvent(
            text="Mock transcript received; connect a speech provider for live transcription.",
            is_final=False,
            provider=self.name,
        )


def get_speech_provider(provider_name: str) -> SpeechToTextProvider:
    if provider_name == "mock":
        return MockSpeechToTextProvider()
    raise ValueError(f"Unsupported speech provider: {provider_name}")