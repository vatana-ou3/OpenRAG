from typing import Any

import requests

from openrag.core.chunk import Chunk
from openrag.generators.base import BaseGenerator


class OllamaGenerator(BaseGenerator):
    """Generate answers with a local Ollama model."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, query: str, chunks: list[Chunk]) -> str:
        prompt = self._build_prompt(query, chunks)
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return str(data.get("response", "")).strip()

    def _build_prompt(self, query: str, chunks: list[Chunk]) -> str:
        context = "\n\n".join(
            f"[Source {index}] {chunk.text}"
            for index, chunk in enumerate(chunks, start=1)
        )

        return (
            "You are a helpful assistant. Answer the question using only the "
            "provided context. If the context does not contain the answer, say "
            "you do not know.\n\n"
            f"Context:\n{context or 'No context found.'}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
