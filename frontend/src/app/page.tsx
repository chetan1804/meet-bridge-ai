"use client";

import { useCallback, useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { StatusBadge } from "@/components/status-badge";
import { apiEndpoint } from "@/lib/api";

const fallbackTranscript = [
  "Product lead: We need a lower-friction plan for meeting follow-up.",
  "Engineer: We should evaluate the retrieval quality before changing prompts.",
  "PM: Could we improve the experience for long calls and transcripts?",
];

const fallbackKeyPoints = [
  "evaluation dataset",
  "chunking strategy",
  "hybrid retrieval",
  "metadata filtering",
  "reranking",
  "retrieval metrics",
];

const sampleQuestion = "How would you improve RAG accuracy?";

const defaultMeetingInsights = {
  summary: "The meeting focused on retrieval quality and follow-up planning.",
  decisions: ["We should evaluate retrieval quality before changing prompts."],
  action_items: [
    "Follow up on retrieval quality and meeting experience improvements.",
  ],
  open_questions: ["How would you improve RAG accuracy?"],
};

const defaultRetrievedEvidence = [
  "Measure recall and precision on a labeled dataset before changing chunking or reranking.",
  "Evaluate retrieval quality, then adjust chunking strategy and ranking heuristics if needed.",
];

export default function Home() {
  const [transcript, setTranscript] = useState<string[]>(fallbackTranscript);
  const [currentQuestion, setCurrentQuestion] =
    useState<string>(sampleQuestion);
  const [questionInput, setQuestionInput] = useState<string>(sampleQuestion);
  const [explanation, setExplanation] = useState<string>(
    "They want a practical approach for diagnosing and improving retrieval quality in a production system.",
  );
  const [answer, setAnswer] = useState<string>(
    "First, I would determine whether the problem comes from retrieval quality, chunk design, or the downstream generation step. Then I would measure recall, precision, and latency on a labeled eval set before making targeted changes to indexing, metadata, and reranking.",
  );
  const [importantTopics, setImportantTopics] =
    useState<string[]>(fallbackKeyPoints);
  const [retrievedEvidence, setRetrievedEvidence] = useState<string[]>(
    defaultRetrievedEvidence,
  );
  const [meetingInsights, setMeetingInsights] = useState(
    defaultMeetingInsights,
  );
  const [meetingTitle, setMeetingTitle] = useState("Q3 Product Review");
  const [listening, setListening] = useState(true);
  const [connected, setConnected] = useState(true);
  const [loading, setLoading] = useState(false);

  const refreshMeetingState = useCallback(async () => {
    try {
      const response = await fetch(apiEndpoint("/api/meeting/state"));
      if (!response.ok) {
        return;
      }

      const data = await response.json();
      if (data.transcript?.length) {
        setTranscript(data.transcript);
      }
      if (data.current_question) {
        setCurrentQuestion(data.current_question);
      }
      if (data.why_they_are_asking) {
        setExplanation(data.why_they_are_asking);
      }
      if (data.suggested_answer) {
        setAnswer(data.suggested_answer);
      }
      if (data.important_topics?.length) {
        setImportantTopics(data.important_topics);
      }
      if (data.retrieved_evidence?.length) {
        setRetrievedEvidence(data.retrieved_evidence);
      }
      if (data.meeting_insights) {
        setMeetingInsights({
          summary:
            data.meeting_insights.summary || defaultMeetingInsights.summary,
          decisions:
            data.meeting_insights.decisions || defaultMeetingInsights.decisions,
          action_items:
            data.meeting_insights.action_items ||
            defaultMeetingInsights.action_items,
          open_questions:
            data.meeting_insights.open_questions ||
            defaultMeetingInsights.open_questions,
        });
      }
      if (data.title) {
        setMeetingTitle(data.title);
      }
      if (typeof data.listening === "boolean") {
        setListening(data.listening);
      }
      if (typeof data.connected === "boolean") {
        setConnected(data.connected);
      }
    } catch {
      // Keep the fallback state until the backend is ready.
    }
  }, []);

  useEffect(() => {
    const fetchContext = async () => {
      try {
        const response = await fetch(
          apiEndpoint("/api/conversation/context"),
        );
        if (!response.ok) {
          return;
        }
        const data = await response.json();
        const lines = data.context
          .split("\n")
          .map((line: string) => line.trim())
          .filter(Boolean);

        if (lines.length > 0) {
          setTranscript(lines);
          const lastQuestion = lines
            .filter((line: string) => line.includes("?"))
            .slice(-1)[0];
          if (lastQuestion) {
            setCurrentQuestion(lastQuestion);
          }
        }
      } catch {
        // Keep the fallback transcript if the backend is not yet running.
      }
    };

    void fetchContext();
    void refreshMeetingState();

    const interval = setInterval(() => {
      void fetchContext();
      void refreshMeetingState();
    }, 2000);

    return () => clearInterval(interval);
  }, [refreshMeetingState]);

  const handleAnalyzeSampleQuestion = async () => {
    setLoading(true);

    try {
      const response = await fetch(
        apiEndpoint("/api/conversation/buffer"),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ utterance: sampleQuestion }),
        },
      );

      if (response.ok) {
        const data = await response.json();
        if (data.is_question) {
          setCurrentQuestion(data.question || sampleQuestion);
          setQuestionInput(data.question || sampleQuestion);
          setExplanation(data.why_they_are_asking || explanation);
          if (data.intent) {
            setAnswer(
              `The likely intent is ${data.intent.toLowerCase()}. The system should focus on ${data.important_topics?.join(", ") || "relevant context"}.`,
            );
          }
          setTranscript((prev) => [...prev, sampleQuestion]);
        }
      }
    } catch {
      setTranscript((prev) => [...prev, sampleQuestion]);
    } finally {
      setLoading(false);
      await refreshMeetingState();
    }
  };

  const handleKnowledgeSearch = async () => {
    const query = questionInput.trim() || currentQuestion;
    if (!query) {
      return;
    }

    try {
      const response = await fetch(
        apiEndpoint("/api/knowledge/search"),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question: query }),
        },
      );

      if (!response.ok) {
        return;
      }

      const data = await response.json();
      const nextEvidence = (
        (data as Array<{ content?: string; title?: string }>) || []
      )
        .map((item) => item.content || item.title || "")
        .filter(Boolean)
        .slice(0, 3);

      if (nextEvidence.length > 0) {
        setRetrievedEvidence(nextEvidence);
      }
    } catch {
      // Keep the existing evidence if the backend is unavailable.
    }
  };

  return (
    <AppShell>
      <main className="px-6 py-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-lg shadow-slate-950/30">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-violet-400">
              MeetBridge AI
            </p>
            <h1 className="mt-2 text-3xl font-semibold">
              Understand. Think. Respond.
            </h1>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <StatusBadge label={listening ? "Listening" : "Paused"} active={listening} />
            <StatusBadge label={connected ? "Connected" : "Disconnected"} active={connected} />
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Meeting title</p>
                <h2 className="text-2xl font-semibold">{meetingTitle}</h2>
              </div>
              <div className="rounded-xl border border-slate-700 bg-slate-800 px-3 py-2 text-right">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  Timer
                </p>
                <p className="text-lg font-medium">00:18:42</p>
              </div>
            </div>

            <div className="space-y-3">
              {transcript.map((line, index) => (
                <div
                  key={`${line}-${index}`}
                  className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm text-slate-200"
                >
                  {line}
                </div>
              ))}
            </div>
          </div>

          <aside className="space-y-6 rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Current Question
              </p>
              <h3 className="mt-2 text-xl font-semibold">{currentQuestion}</h3>
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                What they are asking
              </p>
              <p className="mt-2 text-sm text-slate-200">{explanation}</p>
            </div>

            <div className="mt-4 space-y-2">
              <label className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Search knowledge base
              </label>
              <div className="flex gap-2">
                <input
                  value={questionInput}
                  onChange={(event) => setQuestionInput(event.target.value)}
                  className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-0 placeholder:text-slate-500"
                  placeholder="Ask a follow-up question"
                />
                <button
                  onClick={handleKnowledgeSearch}
                  className="rounded-lg border border-violet-500 bg-violet-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-violet-500"
                >
                  Search
                </button>
              </div>
            </div>

            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Key points
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-200">
                {importantTopics.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </div>
          </aside>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
              Meeting summary
            </p>
            <p className="mt-3 text-base leading-7 text-slate-200">
              {meetingInsights.summary}
            </p>

            <div className="mt-5 space-y-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                  Decisions
                </p>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-200">
                  {meetingInsights.decisions.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Action items
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-200">
                {meetingInsights.action_items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="mt-5">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Open questions
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-200">
                {meetingInsights.open_questions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
              Suggested answer
            </p>
            <p className="mt-3 text-base leading-7 text-slate-200">{answer}</p>

            <div className="mt-5">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Retrieved evidence
              </p>
              <ul className="mt-2 list-disc space-y-2 pl-5 text-sm text-slate-200">
                {retrievedEvidence.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="flex flex-wrap gap-2">
              {[
                "Start",
                "Pause",
                "Stop",
                "Mute AI suggestions",
                "Short answer",
                "Detailed answer",
                "Technical answer",
                "Translate",
              ].map((action) => (
                <button
                  key={action}
                  className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 transition hover:border-violet-500 hover:text-violet-200"
                >
                  {action}
                </button>
              ))}
              <button
                onClick={handleAnalyzeSampleQuestion}
                disabled={loading}
                className="rounded-lg border border-violet-500 bg-violet-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Analyzing..." : "Analyze sample question"}
              </button>
            </div>
          </div>
        </section>
      </div>
      </main>
    </AppShell>
  );
}
