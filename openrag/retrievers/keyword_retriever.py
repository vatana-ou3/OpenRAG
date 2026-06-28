import re
from collections import Counter

from openrag.core.chunk import Chunk
from openrag.retrievers.base import BaseRetriever


class KeywordRetriever(BaseRetriever):
    """A tiny in-memory retriever based on keyword overlap."""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []

    def index(self, chunks: list[Chunk]) -> None:
        self._chunks.extend(chunks)

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        if top_k <= 0:
            return []

        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        scored_chunks: list[tuple[int, int, Chunk]] = []
        for position, chunk in enumerate(self._chunks):
            chunk_terms = Counter(self._tokenize(chunk.text))
            score = sum(chunk_terms[term] for term in query_terms)
            if score > 0:
                scored_chunks.append((score, -position, chunk))

        scored_chunks.sort(reverse=True)
        return [chunk for _, _, chunk in scored_chunks[:top_k]]

    def _tokenize(self, text: str) -> list[str]:
        return re.findall(r"\b\w+\b", text.lower())
