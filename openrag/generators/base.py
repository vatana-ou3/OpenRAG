from abc import ABC, abstractmethod

from openrag.core.chunk import Chunk


class BaseGenerator(ABC):
    """Interface for answer generation."""

    @abstractmethod
    def generate(self, query: str, chunks: list[Chunk]) -> str:
        """Generate an answer from a query and supporting chunks."""
