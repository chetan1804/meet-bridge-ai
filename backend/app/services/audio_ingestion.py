import base64
import binascii
from dataclasses import dataclass, field

from app.schemas.audio import AudioChunkMessage


MAX_AUDIO_CHUNK_BYTES = 512 * 1024


@dataclass
class AudioSession:
    chunks_received: int = 0
    bytes_received: int = 0
    mime_types: set[str] = field(default_factory=set)


class AudioIngestionService:
    """Validate transient audio frames without retaining their raw bytes."""

    def __init__(self) -> None:
        self._sessions: dict[tuple[str, str], AudioSession] = {}

    def accept(self, meeting_id: str, user_id: str, message: AudioChunkMessage) -> AudioSession:
        if not message.mime_type.lower().startswith("audio/"):
            raise ValueError("Audio chunks must use an audio MIME type.")
        try:
            decoded = base64.b64decode(message.data, validate=True)
        except (binascii.Error, ValueError) as error:
            raise ValueError("Audio chunk data must be valid base64.") from error
        if not decoded:
            raise ValueError("Audio chunk data cannot be empty.")
        if len(decoded) > MAX_AUDIO_CHUNK_BYTES:
            raise ValueError("Audio chunk exceeds the 512 KB limit.")

        key = (meeting_id, user_id)
        session = self._sessions.setdefault(key, AudioSession())
        session.chunks_received += 1
        session.bytes_received += len(decoded)
        session.mime_types.add(message.mime_type)
        return session

    def clear(self, meeting_id: str, user_id: str) -> None:
        self._sessions.pop((meeting_id, user_id), None)


audio_ingestion = AudioIngestionService()