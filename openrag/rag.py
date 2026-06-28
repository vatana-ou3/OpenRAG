from pathlib import Path

from openrag.chunkers.base import BaseChunker
from openrag.chunkers.simple_chunker import SimpleChunker
from openrag.core.chunk import Chunk
from openrag.core.pipeline import RAGResult
from openrag.generators.base import BaseGenerator
from openrag.generators.ollama_generator import OllamaGenerator
from openrag.parsers.base import BaseParser
from openrag.parsers.router import ParserRouter
from openrag.retrievers.base import BaseRetriever
from openrag.retrievers.keyword_retriever import KeywordRetriever


class RAG:
    """Small coordinator for local RAG workflows."""

    def __init__(
        self,
        parser: BaseParser | None = None,
        chunker: BaseChunker | None = None,
        retriever: BaseRetriever | None = None,
        generator: BaseGenerator | None = None,
    ) -> None:
        self.parser = parser or ParserRouter.with_defaults()
        self.chunker = chunker or SimpleChunker()
        self.retriever = retriever or KeywordRetriever()
        self.generator = generator or OllamaGenerator()
        self.chunks: list[Chunk] = []

    def add(self, path: str) -> list[Chunk]:
        """Load, chunk, and index one document."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        document = self.parser.parse(str(file_path))
        chunks = self.chunker.chunk(document)
        self.retriever.index(chunks)
        self.chunks.extend(chunks)
        return chunks

    def ask(self, query: str, top_k: int = 5) -> RAGResult:
        """Retrieve relevant chunks and generate an answer."""
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k)
        answer = self.generator.generate(query, retrieved_chunks)
        answer_with_sources = self._format_answer_with_sources(answer, retrieved_chunks)
        return RAGResult(answer=answer_with_sources, sources=retrieved_chunks)

    def _format_answer_with_sources(self, answer: str, chunks: list[Chunk]) -> str:
        if not chunks:
            return f"{answer}\n\nSources: none"

        source_lines = []
        for index, chunk in enumerate(chunks, start=1):
            source = chunk.metadata.get("source", chunk.document_id)
            chunk_number = chunk.metadata.get("chunk_number", "?")
            source_lines.append(f"{index}. {source} (chunk {chunk_number})")

        return f"{answer}\n\nSources:\n" + "\n".join(source_lines)
