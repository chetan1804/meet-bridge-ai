from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.analytics import UsageMetrics, UsageRecordRequest
from app.services.analytics_service import service


router = APIRouter(prefix="/analytics", tags=["analytics"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/usage", response_model=UsageMetrics)
def get_usage_metrics(current_user: CurrentUser) -> UsageMetrics:
    return service.get_summary()


@router.post("/usage/record", response_model=UsageMetrics)
def record_usage(payload: UsageRecordRequest, current_user: CurrentUser) -> UsageMetrics:
    return service.record_usage(payload)
