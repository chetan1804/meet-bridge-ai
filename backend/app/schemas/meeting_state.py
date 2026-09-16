from pydantic import BaseModel, Field


class MeetingContextState(BaseModel):
    meeting_id: str = Field(default="demo-meeting")
    title: str = Field(default="Q3 Product Review")
    current_question: str | None = None
    why_they_are_asking: str | None = None
    important_topics: list[str] = Field(default_factory=list)
    suggested_answer: str | None = None
    transcript: list[str] = Field(default_factory=list)
    listening: bool = True
    connected: bool = True


class MeetingStateResponse(MeetingContextState):
    pass
