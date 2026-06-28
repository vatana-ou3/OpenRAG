from dataclasses import dataclass, field
from typing import Any

from openrag.core.chunk import Chunk


@dataclass
class RAGResult:
    """The answer returned by a RAG pipeline, plus the chunks used to build it."""

    answer: str
    sources: list[Chunk] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.answer
