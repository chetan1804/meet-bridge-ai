from __future__ import annotations

from dataclasses import dataclass
import re

from app.services.embedding_provider import SimpleEmbeddingProvider


@dataclass
class KnowledgeItem:
    title: str
    content: str
    score: float


class KnowledgeService:
    """Simple retrieval layer for relevant documents and evidence matching."""

    def __init__(self) -> None:
        self.embedding_provider = SimpleEmbeddingProvider()

    def retrieve(
        self,
        query: str,
        documents: list[dict[str, str]] | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> list[KnowledgeItem]:
        normalized_query = (query or "").strip()
        if not normalized_query:
            return []

        candidate_documents = documents or []
        if not candidate_documents:
            return []

        query_terms = self._expand_query_terms(self._tokenize(normalized_query))
        query_text = normalized_query
        metadata_filters = metadata_filters or {}
        matches: list[KnowledgeItem] = []

        for document in candidate_documents:
            text = (document.get("content") or "").strip()
            title = (document.get("title") or "Untitled").strip()
            if not text:
                continue

            metadata = document.get("metadata") or {}
            if not self._matches_metadata_filters(metadata, metadata_filters):
                continue

            combined_text = f"{title} {text}"
            score = self._score(query_terms, combined_text, query_text, metadata, metadata_filters)
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

    def _score(
        self,
        query_terms: set[str],
        text: str,
        query: str,
        metadata: dict[str, str] | None = None,
        metadata_filters: dict[str, str] | None = None,
    ) -> float:
        words = self._tokenize(text)
        if not query_terms:
            return 0.0

        overlap = len(query_terms & words)
        weighted = 0.0
        if overlap > 0:
            weighted = (overlap / len(query_terms)) * 1.2

        semantic_signal = self.embedding_provider.cosine_similarity(query, text)
        if semantic_signal > 0:
            weighted += semantic_signal * 0.7

        for key, expected_value in (metadata_filters or {}).items():
            actual_value = (metadata or {}).get(key)
            if actual_value is not None:
                normalized_expected = str(expected_value).strip().lower()
                normalized_actual = str(actual_value).strip().lower()
                if normalized_actual == normalized_expected:
                    weighted += 0.4
                elif normalized_expected in normalized_actual:
                    weighted += 0.2

        if any(term in text.lower() for term in ("retrieval", "chunk", "rerank", "precision", "recall", "metrics", "quality")):
            weighted += 0.25
        if any(term in text.lower() for term in ("rag", "retrieval", "chunking", "reranking", "embedding", "semantic", "vector")):
            weighted += 0.15

        if weighted <= 0:
            return 0.0
        return round(min(weighted, 1.0), 4)

    def _matches_metadata_filters(self, metadata: dict[str, str], metadata_filters: dict[str, str]) -> bool:
        if not metadata_filters:
            return True

        for key, expected_value in metadata_filters.items():
            actual_value = metadata.get(key)
            if actual_value is None:
                return False
            if str(actual_value).strip().lower() != str(expected_value).strip().lower():
                return False
        return True
