from __future__ import annotations

import re
from collections import Counter


class SimpleEmbeddingProvider:
    """Lightweight embedding-like similarity provider for in-memory retrieval.

    This intentionally avoids external vector dependencies while still modeling the
    core behavior expected from semantic retrieval: related concepts such as
    "semantic search", "vector similarity", and "reranking" should be recognized
    even when they are expressed with different but related vocabulary.
    """

    name = "simple"

    _term_aliases = {
        "semantic": {"semantic", "conceptual", "related", "meaningful"},
        "search": {"search", "lookup", "query", "retrieval", "finder"},
        "similarity": {"similarity", "similar", "matching", "related", "alignment"},
        "vector": {"vector", "embedding", "embeddings", "representation"},
        "quality": {"quality", "accuracy", "precision", "recall", "score", "relevance"},
        "improve": {"improve", "improving", "optimize", "optimization", "enhance", "better", "boost", "tune"},
        "rank": {"rank", "ranking", "rerank", "reranking", "sort"},
        "chunk": {"chunk", "chunking", "segment", "split", "partition"},
        "context": {"context", "background", "grounding", "evidence"},
    }

    def embed(self, text: str) -> dict[str, float]:
        counts = Counter()
        for token in re.findall(r"[a-zA-Z0-9]+", (text or "").lower()):
            if len(token) <= 2:
                continue
            for canonical in self._canonicalize(token):
                counts[canonical] += 1
        return dict(counts)

    def cosine_similarity(self, left: str, right: str) -> float:
        left_vector = self.embed(left)
        right_vector = self.embed(right)
        if not left_vector or not right_vector:
            return 0.0

        shared_terms = set(left_vector) & set(right_vector)
        if not shared_terms:
            return 0.0

        left_norm = sum(value * value for value in left_vector.values()) ** 0.5
        right_norm = sum(value * value for value in right_vector.values()) ** 0.5
        if left_norm == 0 or right_norm == 0:
            return 0.0

        numerator = sum(left_vector[term] * right_vector[term] for term in shared_terms)
        return round(numerator / (left_norm * right_norm), 4)

    def _canonicalize(self, token: str) -> set[str]:
        normalized = token.strip().lower()
        if not normalized:
            return set()

        matches = {normalized}
        for canonical, aliases in self._term_aliases.items():
            if normalized in aliases or normalized == canonical:
                matches.add(canonical)
        return matches
