from abc import ABC, abstractmethod

from openrag.core.chunk import Chunk


class BaseRetriever(ABC):
    """Interface for indexing and retrieving chunks."""

    @abstractmethod
    def index(self, chunks: list[Chunk]) -> None:
        """Add chunks to the retriever index."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        """Return the most relevant chunks for a query."""
