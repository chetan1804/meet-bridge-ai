from __future__ import annotations

from app.schemas.meeting_state import MeetingContextState
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_store import list_knowledge_documents
from app.services.meeting_insights_service import MeetingInsightsService


class MeetingStateService:
    """Minimal in-memory meeting state used for live current-question and transcript tracking."""

    def __init__(self) -> None:
        self.insights_service = MeetingInsightsService()
        self.knowledge_service = KnowledgeService()
        self.reset()

    def _build_default_state(self) -> MeetingContextState:
        transcript = [
            "Product lead: We need a lower-friction plan for meeting follow-up.",
            "Engineer: We should evaluate the retrieval quality before changing prompts.",
            "PM: Could we improve the experience for long calls and transcripts?",
        ]
        base_question = "How would you improve RAG accuracy?"
        evidence = [
            "Measure recall and precision on a labeled dataset before changing chunking or reranking.",
            "Evaluate retrieval quality, then adjust chunking strategy and ranking heuristics if needed.",
        ]
        return MeetingContextState(
            meeting_id="demo-meeting",
            title="Q3 Product Review",
            transcript=transcript,
            current_question=base_question,
            why_they_are_asking="They want a practical approach for diagnosing and improving retrieval quality in a production system.",
            important_topics=["evaluation dataset", "chunking strategy", "retrieval metrics"],
            suggested_answer="First, I would determine whether the problem comes from retrieval quality, chunk design, or the downstream generation step.",
            retrieved_evidence=evidence,
            meeting_insights=self.insights_service.build_insights(transcript),
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

        knowledge_docs = [
            {"title": document.title, "content": document.content}
            for document in list_knowledge_documents()
        ]
        retrieved = self.knowledge_service.retrieve(question, knowledge_docs)
        self.state.retrieved_evidence = [item.content for item in retrieved[:2]]

        self.state.suggested_answer = self.state.suggested_answer
        if intent:
            self.state.suggested_answer = self.insights_service.get_suggested_response(
                question=question,
                intent=intent,
                important_topics=topics or self.state.important_topics,
            )
        elif question:
            self.state.suggested_answer = self.insights_service.get_suggested_response(
                question=question,
                important_topics=topics or self.state.important_topics,
            )

        self.state.meeting_insights = self.insights_service.build_insights(self.state.transcript)
        return self.state

    def add_transcript_line(self, line: str) -> MeetingContextState:
        cleaned = line.strip()
        if cleaned and cleaned not in self.state.transcript:
            self.state.transcript.append(cleaned)
        self.state.meeting_insights = self.insights_service.build_insights(self.state.transcript)
        return self.state


service = MeetingStateService()
