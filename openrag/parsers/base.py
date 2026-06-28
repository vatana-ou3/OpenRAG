from abc import ABC, abstractmethod

from openrag.core.document import Document


class BaseParser(ABC):
    """Interface for loading files into Document objects."""

    @abstractmethod
    def parse(self, path: str) -> Document:
        """Parse a file path into a Document."""
