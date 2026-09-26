from pydantic import BaseModel, Field


class TranscriptEvent(BaseModel):
    text: str = Field(min_length=1)
    is_final: bool = False
    language: str = "en"
    provider: str