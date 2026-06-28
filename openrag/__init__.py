"""OpenRAG: a small framework for local retrieval-augmented generation."""

from openrag.core.chunk import Chunk
from openrag.core.document import Document
from openrag.rag import RAG

__all__ = ["Chunk", "Document", "RAG"]
