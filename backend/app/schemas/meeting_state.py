from pydantic import BaseModel, Field

from app.schemas.meeting_insights import MeetingInsights


class MeetingContextState(BaseModel):
    meeting_id: str = Field(default="demo-meeting")
    title: str = Field(default="Q3 Product Review")
    current_question: str | None = None
    why_they_are_asking: str | None = None
    important_topics: list[str] = Field(default_factory=list)
    suggested_answer: str | None = None
    transcript: list[str] = Field(default_factory=list)
    meeting_insights: MeetingInsights = Field(default_factory=lambda: MeetingInsights(
        summary="The meeting focused on retrieval quality and follow-up planning.",
        decisions=["We should evaluate retrieval quality before changing prompts."],
        action_items=["Follow up on retrieval quality and meeting experience improvements."],
        open_questions=["How would you improve RAG accuracy?"],
    ))
    listening: bool = True
    connected: bool = True


class MeetingStateResponse(MeetingContextState):
    pass
