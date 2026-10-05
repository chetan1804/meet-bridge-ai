from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.routes.auth import get_current_user
from app.models.user import User
from app.schemas.evaluation import EvaluationExample, EvaluationScoreRequest, EvaluationScoreResult
from app.services.evaluation_service import service


router = APIRouter(prefix="/evaluation", tags=["evaluation"])
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/dataset", response_model=list[EvaluationExample])
def get_dataset(current_user: CurrentUser) -> list[EvaluationExample]:
    return service.get_dataset()


@router.post("/score", response_model=EvaluationScoreResult)
def score_evaluation(payload: EvaluationScoreRequest, current_user: CurrentUser) -> EvaluationScoreResult:
    return service.score(payload)


@router.get("/report", response_model=dict[str, float | int])
def get_report(current_user: CurrentUser) -> dict[str, float | int]:
    return service.get_report()
