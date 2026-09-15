from fastapi import APIRouter

from app.schemas.question import QuestionDetectionRequest, QuestionDetectionResult, IntentUnderstandingResult
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])
service = QuestionService()


@router.post("/detect", response_model=QuestionDetectionResult)
def detect_question(payload: QuestionDetectionRequest) -> QuestionDetectionResult:
    return service.detect_question(payload)


@router.post("/intent", response_model=IntentUnderstandingResult)
def understand_intent(question: str) -> IntentUnderstandingResult:
    return service.understand_intent(question)
