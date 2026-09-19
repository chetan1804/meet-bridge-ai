from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass
class KnowledgeItem:
    title: str
    content: str
    score: float


class KnowledgeService:
    """Simple retrieval layer for relevant documents and evidence matching."""

    def retrieve(self, query: str, documents: list[dict[str, str]] | None = None) -> list[KnowledgeItem]:
        normalized_query = (query or "").strip()
        if not normalized_query:
            return []

        candidate_documents = documents or []
        if not candidate_documents:
            return []

        query_terms = self._expand_query_terms(self._tokenize(normalized_query))
        matches: list[KnowledgeItem] = []

        for document in candidate_documents:
            text = (document.get("content") or "").strip()
            title = (document.get("title") or "Untitled").strip()
            if not text:
                continue

            score = self._score(query_terms, f"{title} {text}")
            if score > 0:
                matches.append(KnowledgeItem(title=title, content=text, score=score))

        return sorted(matches, key=lambda item: item.score, reverse=True)

    def _tokenize(self, text: str) -> set[str]:
        return {term for term in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(term) > 2}

    def _expand_query_terms(self, terms: set[str]) -> set[str]:
        expanded = set(terms)
        synonyms = {
            "rag": {"rag", "retrieval", "retriever", "context", "embedding"},
            "accuracy": {"accuracy", "precision", "recall", "quality", "relevance", "score", "performance"},
            "improve": {"improve", "improving", "optimize", "optimize", "tune", "boost", "better"},
            "chunk": {"chunk", "chunking", "segment", "split"},
            "rank": {"rank", "ranking", "rerank", "reranking"},
        }

        for term in list(terms):
            expanded.update(synonyms.get(term, {term}))

        return expanded

    def _score(self, query_terms: set[str], text: str) -> float:
        words = self._tokenize(text)
        if not query_terms:
            return 0.0

        overlap = len(query_terms & words)
        if overlap == 0:
            return 0.0

        weighted = (overlap / len(query_terms)) * 1.2
        if any(term in text.lower() for term in ("retrieval", "chunk", "rerank", "precision", "recall", "metrics", "quality")):
            weighted += 0.25
        if any(term in text.lower() for term in ("rag", "retrieval", "chunking", "reranking")):
            weighted += 0.15
        return round(min(weighted, 1.0), 4)
