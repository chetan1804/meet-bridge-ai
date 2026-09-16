"use client";

import { useEffect, useState } from "react";

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

export default function Home() {
  const [transcript, setTranscript] = useState<string[]>(fallbackTranscript);
  const [currentQuestion, setCurrentQuestion] =
    useState<string>(sampleQuestion);
  const [explanation, setExplanation] = useState<string>(
    "They want a practical approach for diagnosing and improving retrieval quality in a production system.",
  );
  const [answer, setAnswer] = useState<string>(
    "First, I would determine whether the problem comes from retrieval quality, chunk design, or the downstream generation step. Then I would measure recall, precision, and latency on a labeled eval set before making targeted changes to indexing, metadata, and reranking.",
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchContext = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/conversation/context",
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

    fetchContext();
  }, []);

  const handleAnalyzeSampleQuestion = async () => {
    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/api/conversation/buffer",
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
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
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
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1.5 text-emerald-300">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
              Listening
            </span>
            <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1.5">
              Connected
            </span>
          </div>
        </header>

        <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Meeting title</p>
                <h2 className="text-2xl font-semibold">Q3 Product Review</h2>
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

            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Key points
              </p>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-200">
                {fallbackKeyPoints.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </div>
          </aside>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
              Suggested answer
            </p>
            <p className="mt-3 text-base leading-7 text-slate-200">{answer}</p>
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
  );
}
