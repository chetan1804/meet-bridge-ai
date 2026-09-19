from __future__ import annotations

import re

from app.schemas.meeting_insights import MeetingInsights
from app.services.question_service import QuestionService


class MeetingInsightsService:
    """Extract lightweight meeting summaries and actionable follow-ups from transcript text."""

    def build_insights(self, transcript: list[str]) -> MeetingInsights:
        cleaned_lines = [self._clean_line(line) for line in transcript if line and line.strip()]

        if not cleaned_lines:
            return MeetingInsights(
                summary="No meeting transcript is available yet.",
                decisions=[],
                action_items=[],
                open_questions=[],
            )

        decisions = [line for line in cleaned_lines if self._looks_like_decision(line)]
        if not decisions:
            decisions = [cleaned_lines[0]]

        action_items = [line for line in cleaned_lines if self._looks_like_action_item(line)]
        if not action_items:
            action_items = [cleaned_lines[0]]

        open_questions = [line for line in cleaned_lines if "?" in line]

        summary = self._build_summary(cleaned_lines, decisions, open_questions)

        return MeetingInsights(
            summary=summary,
            decisions=decisions,
            action_items=action_items,
            open_questions=open_questions,
        )

    def get_suggested_response(
        self,
        question: str,
        intent: str | None = None,
        important_topics: list[str] | None = None,
    ) -> str:
        return QuestionService().build_suggested_response(
            question=question,
            intent=intent,
            important_topics=important_topics,
        )

    def _clean_line(self, line: str) -> str:
        cleaned = line.strip()
        cleaned = re.sub(r"^[A-Za-z][A-Za-z .'-]*:\s*", "", cleaned)
        return cleaned.strip()

    def _looks_like_decision(self, line: str) -> bool:
        lowered = line.lower()
        keywords = ("need", "should", "must", "will", "decide", "decision", "proceed", "plan")
        return any(keyword in lowered for keyword in keywords)

    def _looks_like_action_item(self, line: str) -> bool:
        lowered = line.lower()
        keywords = ("need", "should", "could", "would", "improve", "evaluate", "follow-up", "review", "plan")
        return any(keyword in lowered for keyword in keywords)

    def _build_summary(self, cleaned_lines: list[str], decisions: list[str], open_questions: list[str]) -> str:
        focus = decisions[0]
        if len(cleaned_lines) > 1:
            focus = f"{decisions[0]} and {cleaned_lines[1]}"

        question_note = ""
        if open_questions:
            question_note = f", with a question about {open_questions[0].rstrip('?')}"

        return (
            "The meeting focused on "
            f"{focus.lower()}{question_note}."
        )
