from __future__ import annotations

import re

from app.schemas.evaluation import (
    EvaluationExample,
    EvaluationScoreRequest,
    EvaluationScoreResult,
    token_set,
)


class EvaluationService:
    def __init__(self) -> None:
        self.dataset = [
            EvaluationExample(
                id="rag-001",
                question="How do we improve retrieval quality for RAG?",
                answer="Improve retrieval quality by tuning chunking, metadata filtering, and reranking.",
                expected_contexts=[
                    "Chunking and reranking improve retrieval quality in RAG systems.",
                    "Metadata filtering helps retrieve the right evidence for RAG workflows.",
                ],
                ground_truth="Chunking and reranking are core ways to improve retrieval quality in RAG.",
                metadata={"category": "retrieval"},
            ),
            EvaluationExample(
                id="rag-002",
                question="What should we measure before changing the retriever?",
                answer="Measure retrieval relevance, context recall, and groundedness before changing the retriever.",
                expected_contexts=[
                    "Retrieval relevance and context recall are essential evaluation metrics.",
                ],
                ground_truth="Measure retrieval relevance and context recall before changing the retriever.",
                metadata={"category": "evaluation"},
            ),
        ]
        self.last_result: EvaluationScoreResult | None = None

    def get_dataset(self) -> list[EvaluationExample]:
        return self.dataset

    def score(self, request: EvaluationScoreRequest) -> EvaluationScoreResult:
        question_terms = token_set(request.question)
        answer_terms = token_set(request.answer)
        context_text = " ".join(request.retrieved_contexts)
        context_terms = token_set(context_text)

        retrieval_relevance = 0.0
        if question_terms:
            retrieval_relevance = len(question_terms & context_terms) / len(question_terms)

        relevant_count = 0
        for context in request.retrieved_contexts:
            if any(term in token_set(context) for term in question_terms) or (
                request.expected_contexts and context in request.expected_contexts
            ):
                relevant_count += 1

        context_precision = 0.0
        if request.retrieved_contexts:
            context_precision = relevant_count / len(request.retrieved_contexts)

        if request.expected_contexts:
            context_recall = min(relevant_count / len(request.expected_contexts), 1.0)
        else:
            context_recall = 1.0

        answer_relevance = 0.0
        if question_terms:
            answer_relevance = min(len(question_terms & answer_terms) / len(question_terms), 1.0)

        anchors = answer_terms | context_terms
        groundedness = 0.0
        if anchors:
            groundedness = len(answer_terms & context_terms) / len(anchors)

        total_tokens = request.prompt_tokens + request.completion_tokens
        estimated_cost_usd = ((request.prompt_tokens * 0.00001) + (request.completion_tokens * 0.00002))

        result = EvaluationScoreResult(
            retrieval_relevance=round(min(max(retrieval_relevance, 0.0), 1.0), 4),
            context_precision=round(min(max(context_precision, 0.0), 1.0), 4),
            context_recall=round(min(max(context_recall, 0.0), 1.0), 4),
            answer_relevance=round(min(max(answer_relevance, 0.0), 1.0), 4),
            groundedness=round(min(max(groundedness, 0.0), 1.0), 4),
            prompt_tokens=request.prompt_tokens,
            completion_tokens=request.completion_tokens,
            total_tokens=total_tokens,
            latency_ms=float(request.latency_ms),
            estimated_cost_usd=round(estimated_cost_usd, 6),
        )
        self.last_result = result
        return result

    def get_report(self) -> dict[str, float | int]:
        if self.last_result is None:
            return {"retrieval_relevance": 0.0, "context_precision": 0.0, "context_recall": 0.0, "answer_relevance": 0.0, "groundedness": 0.0, "total_tokens": 0, "latency_ms": 0.0, "estimated_cost_usd": 0.0}
        return {
            "retrieval_relevance": self.last_result.retrieval_relevance,
            "context_precision": self.last_result.context_precision,
            "context_recall": self.last_result.context_recall,
            "answer_relevance": self.last_result.answer_relevance,
            "groundedness": self.last_result.groundedness,
            "total_tokens": self.last_result.total_tokens,
            "latency_ms": self.last_result.latency_ms,
            "estimated_cost_usd": self.last_result.estimated_cost_usd,
        }


service = EvaluationService()
