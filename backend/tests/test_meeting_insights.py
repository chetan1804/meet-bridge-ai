from app.services.meeting_insights_service import MeetingInsightsService


def test_extract_structured_meeting_insights() -> None:
    transcript = [
        "Product lead: We need a lower-friction plan for meeting follow-up.",
        "Engineer: We should evaluate retrieval quality before changing prompts.",
        "PM: Could we improve the experience for long calls and transcripts?",
    ]

    result = MeetingInsightsService().build_insights(transcript)

    assert result.summary.lower().startswith("the meeting")
    assert any("retrieval quality" in item.lower() for item in result.decisions)
    assert any("follow-up" in item.lower() for item in result.action_items)
    assert "Could we improve the experience for long calls and transcripts?" in result.open_questions
