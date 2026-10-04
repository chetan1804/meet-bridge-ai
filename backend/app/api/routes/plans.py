from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.plans import PlanDefinition, PlanStatus, UpdatePlanRequest, UsageRecordRequest
from app.services.plan_service import service


router = APIRouter(prefix="/plans", tags=["plans"])
DatabaseSession = Annotated[Session, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[PlanDefinition])
def list_plans(current_user: CurrentUser) -> list[PlanDefinition]:
    return service.list_plans()


@router.get("/me", response_model=PlanStatus)
def get_current_plan(current_user: CurrentUser) -> PlanStatus:
    return service.get_status(current_user)


@router.post("/me", response_model=PlanStatus)
def update_current_plan(
    payload: UpdatePlanRequest,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> PlanStatus:
    try:
        status_response = service.set_plan(current_user, payload.plan)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    session.add(current_user)
    session.commit()
    return status_response


@router.post("/usage/record", response_model=PlanStatus)
def record_usage(
    payload: UsageRecordRequest,
    current_user: CurrentUser,
) -> PlanStatus:
    try:
        return service.record_usage(current_user, payload.feature, payload.amount)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error
