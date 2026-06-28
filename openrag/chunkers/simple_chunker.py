from openrag.chunkers.base import BaseChunker
from openrag.core.chunk import Chunk
from openrag.core.document import Document


class SimpleChunker(BaseChunker):
    """Split text into fixed-size character chunks with optional overlap."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> list[Chunk]:
        text = document.text.strip()
        if not text:
            return []

        chunks: list[Chunk] = []
        start = 0
        chunk_number = 0
        step = self.chunk_size - self.overlap

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Chunk(
                        id=f"{document.id}:{chunk_number}",
                        document_id=document.id,
                        text=chunk_text,
                        metadata={
                            **document.metadata,
                            "chunk_number": chunk_number,
                            "start": start,
                            "end": min(end, len(text)),
                        },
                    )
                )
                chunk_number += 1

            start += step

        return chunks
