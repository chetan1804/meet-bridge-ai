from typing import Literal

from pydantic import BaseModel, Field


class AudioChunkMessage(BaseModel):
    type: Literal["audio_chunk"]
    mime_type: str = Field(min_length=1, max_length=100)
    data: str = Field(min_length=1)