from fastapi import APIRouter, Query

from app.schemas.meeting_state import MeetingContextState, MeetingSearchResult, MeetingStateResponse
from app.services.meeting_state_service import service

router = APIRouter(prefix="/meeting", tags=["meeting"])


@router.get("/state", response_model=MeetingStateResponse)
def get_meeting_state() -> MeetingStateResponse:
    return MeetingStateResponse(**service.get_state().model_dump())


@router.get("/search", response_model=list[MeetingSearchResult])
def search_meeting_history(
    query: str | None = Query(default=None, alias="query"),
    q: str | None = Query(default=None, alias="q"),
    limit: int = 5,
) -> list[MeetingSearchResult]:
    search_term = (q or query or "").strip()
    if not search_term:
        return []
    return [
        MeetingSearchResult(**entry)
        for entry in service.search_history(search_term, limit=limit)
    ]


@router.post("/state", response_model=MeetingStateResponse)
def update_meeting_state(payload: MeetingContextState) -> MeetingStateResponse:
    state = service.get_state()

    if payload.current_question:
        state.current_question = payload.current_question
        state.why_they_are_asking = payload.why_they_are_asking or state.why_they_are_asking
        state.expected_answer_type = payload.expected_answer_type or state.expected_answer_type
        state.important_topics = payload.important_topics or state.important_topics
        state.context_needed = payload.context_needed or state.context_needed
        state.suggested_answer = payload.suggested_answer or state.suggested_answer
        state.transcript = payload.transcript or state.transcript
        state = service.update_from_question(
            state.current_question,
            why=state.why_they_are_asking,
            topics=state.important_topics,
            expected_answer_type=state.expected_answer_type,
            context_needed=state.context_needed,
        )
    else:
        state.why_they_are_asking = payload.why_they_are_asking or state.why_they_are_asking
        state.expected_answer_type = payload.expected_answer_type or state.expected_answer_type
        state.important_topics = payload.important_topics or state.important_topics
        state.context_needed = payload.context_needed or state.context_needed
        state.suggested_answer = payload.suggested_answer or state.suggested_answer
        state.transcript = payload.transcript or state.transcript

    state.listening = payload.listening
    state.connected = payload.connected
    return MeetingStateResponse(**state.model_dump())
