from fastapi import APIRouter

from app.schemas.meeting_state import MeetingContextState, MeetingStateResponse
from app.services.meeting_state_service import service

router = APIRouter(prefix="/meeting", tags=["meeting"])


@router.get("/state", response_model=MeetingStateResponse)
def get_meeting_state() -> MeetingStateResponse:
    return MeetingStateResponse(**service.get_state().model_dump())


@router.post("/state", response_model=MeetingStateResponse)
def update_meeting_state(payload: MeetingContextState) -> MeetingStateResponse:
    state = service.get_state()
    state.current_question = payload.current_question or state.current_question
    state.why_they_are_asking = payload.why_they_are_asking or state.why_they_are_asking
    state.important_topics = payload.important_topics or state.important_topics
    state.suggested_answer = payload.suggested_answer or state.suggested_answer
    state.transcript = payload.transcript or state.transcript
    state.listening = payload.listening
    state.connected = payload.connected
    return MeetingStateResponse(**state.model_dump())
