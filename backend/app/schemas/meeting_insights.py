from pydantic import BaseModel, Field


class MeetingInsights(BaseModel):
    summary: str = Field(..., description="Short summary of the meeting discussion.")
    decisions: list[str] = Field(default_factory=list, description="Key decisions identified from the transcript.")
    action_items: list[str] = Field(default_factory=list, description="Follow-up tasks or action items.")
    open_questions: list[str] = Field(default_factory=list, description="Open questions still pending in the meeting.")
