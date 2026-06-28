from abc import ABC, abstractmethod

from openrag.core.chunk import Chunk
from openrag.core.document import Document


class BaseChunker(ABC):
    """Interface for splitting a Document into chunks."""

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """Split a document into retrievable chunks."""
