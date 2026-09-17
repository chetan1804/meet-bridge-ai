from __future__ import annotations

from app.schemas.meeting_state import MeetingContextState


class MeetingStateService:
    """Minimal in-memory meeting state used for live current-question and transcript tracking."""

    def __init__(self) -> None:
        self.reset()

    def _build_default_state(self) -> MeetingContextState:
        return MeetingContextState(
            meeting_id="demo-meeting",
            title="Q3 Product Review",
            transcript=[
                "Product lead: We need a lower-friction plan for meeting follow-up.",
                "Engineer: We should evaluate the retrieval quality before changing prompts.",
            ],
            current_question="How would you improve RAG accuracy?",
            why_they_are_asking="They want a practical approach for diagnosing and improving retrieval quality in a production system.",
            important_topics=["evaluation dataset", "chunking strategy", "retrieval metrics"],
            suggested_answer="First, I would determine whether the problem comes from retrieval quality, chunk design, or the downstream generation step.",
        )

    def reset(self) -> MeetingContextState:
        self.state = self._build_default_state()
        return self.state

    def get_state(self) -> MeetingContextState:
        return self.state

    def update_from_question(self, question: str, intent: str | None = None, why: str | None = None, topics: list[str] | None = None) -> MeetingContextState:
        self.state.current_question = question
        if why:
            self.state.why_they_are_asking = why
        if topics:
            self.state.important_topics = topics
        if intent:
            self.state.suggested_answer = (
                f"The likely intent is {intent.lower()}. Focus on the most relevant evidence and keep the answer concise with clear next steps."
            )
        return self.state

    def add_transcript_line(self, line: str) -> MeetingContextState:
        cleaned = line.strip()
        if cleaned and cleaned not in self.state.transcript:
            self.state.transcript.append(cleaned)
        return self.state


service = MeetingStateService()
