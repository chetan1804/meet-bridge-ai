from pydantic import BaseModel, Field


class PlanDefinition(BaseModel):
    key: str
    name: str
    monthly_price_usd: float
    max_ai_requests_per_day: int
    max_meetings_per_month: int
    features: list[str] = Field(default_factory=list)


class UpdatePlanRequest(BaseModel):
    plan: str = Field(..., min_length=2, description="Plan key such as FREE, PRO, or TEAM.")


class UsageRecordRequest(BaseModel):
    feature: str = Field(..., min_length=2)
    amount: int = Field(default=1, gt=0)


class PlanStatus(BaseModel):
    plan: str
    plan_name: str
    features: list[str]
    usage: dict[str, int]
    limits: dict[str, int]
    remaining: dict[str, int]
    is_over_limit: bool = False
