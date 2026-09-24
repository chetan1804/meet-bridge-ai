from datetime import datetime
from pydantic import BaseModel, Field
class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    scheduled_at: datetime | None = None
class MeetingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    scheduled_at: datetime | None = None
    status: str | None = None
class MeetingResponse(BaseModel):
    id: str; organization_id: str; title: str; scheduled_at: datetime | None; status: str
    model_config = {"from_attributes": True}
