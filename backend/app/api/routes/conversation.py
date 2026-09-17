from fastapi import APIRouter

from app.schemas.conversation import ConversationBufferRequest, ConversationBufferResponse, ConversationContextResponse
from app.services.conversation_buffer import ConversationBufferService
from app.services.meeting_state_service import service as meeting_state_service

router = APIRouter(prefix="/conversation", tags=["conversation"])
service = ConversationBufferService()


@router.post("/buffer", response_model=ConversationBufferResponse)
def append_utterance(payload: ConversationBufferRequest) -> ConversationBufferResponse:
    service.add_utterance(payload.utterance)
    meeting_state_service.add_transcript_line(payload.utterance)
    analysis = service.analyze_latest_turn()

    if analysis is None:
        return ConversationBufferResponse(
            is_question=False,
            confidence=0.0,
            question="",
            question_type="general",
            requires_response=False,
        )

    meeting_state_service.update_from_question(
        analysis["question"],
        analysis.get("intent"),
        analysis.get("why_they_are_asking"),
        analysis.get("important_topics"),
    )
    return ConversationBufferResponse(**analysis)


@router.get("/context", response_model=ConversationContextResponse)
def get_context() -> ConversationContextResponse:
    return ConversationContextResponse(context=service.get_context_window())
