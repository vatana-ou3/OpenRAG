import re
from dataclasses import dataclass

from openrag.chunkers.base import BaseChunker
from openrag.core.chunk import Chunk
from openrag.core.document import Document


@dataclass
class _TextBlock:
    text: str
    heading: str | None = None


class MabChunker(BaseChunker):
    """Structure-aware chunker for mixed document types."""

    def __init__(
        self,
        chunk_size: int = 260,
        overlap: int = 50,
        min_chunk_size: int = 25,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if overlap < 0:
            raise ValueError("overlap cannot be negative")
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        if min_chunk_size < 0:
            raise ValueError("min_chunk_size cannot be negative")

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    def chunk(self, document: Document) -> list[Chunk]:
        text = self._normalize_text(document.text)
        if not text:
            return []

        blocks = self._merge_small_blocks(self._detect_blocks(text))
        chunk_texts = self._build_chunks(blocks)

        return [
            Chunk(
                id=f"{document.id}:{chunk_number}",
                document_id=document.id,
                text=chunk_text,
                metadata={
                    **document.metadata,
                    "chunk_number": chunk_number,
                    "word_count": self._word_count(chunk_text),
                    "chunker": "mab",
                },
            )
            for chunk_number, chunk_text in enumerate(chunk_texts)
        ]

    def _normalize_text(self, text: str) -> str:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = text.replace("\t", " ")
        text = re.sub(r"([.!?])([A-Z])", r"\1 \2", text)
        text = re.sub(r"([a-z])([A-Z][a-z])", r"\1 \2", text)

        normalized_lines = []
        for line in text.split("\n"):
            line = re.sub(r" {2,}", " ", line.strip())
            normalized_lines.append(line)

        normalized = "\n".join(normalized_lines)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    def _detect_blocks(self, text: str) -> list[_TextBlock]:
        blocks: list[_TextBlock] = []
        current_heading: str | None = None
        current_lines: list[str] = []
        current_kind: str | None = None

        def flush() -> None:
            nonlocal current_lines, current_kind
            if not current_lines:
                return

            body = "\n".join(current_lines).strip()
            block_text = body
            if current_heading and not body.startswith(current_heading):
                block_text = f"{current_heading}\n{body}"

            blocks.append(_TextBlock(text=block_text, heading=current_heading))
            current_lines = []
            current_kind = None

        for line in text.split("\n"):
            if not line:
                flush()
                continue

            if self._is_heading(line):
                flush()
                current_heading = line
                continue

            line_kind = self._line_kind(line)
            if current_kind and line_kind != current_kind:
                flush()

            current_lines.append(line)
            current_kind = line_kind

        flush()

        if not blocks:
            return [_TextBlock(text=text)]

        return blocks

    def _line_kind(self, line: str) -> str:
        if self._is_bullet_or_step(line):
            return "list"
        if self._is_key_value(line):
            return "key-value"
        if self._is_table_like(line):
            return "table"
        return "paragraph"

    def _is_heading(self, line: str) -> bool:
        words = line.split()
        if not words or len(words) > 14:
            return False
        if self._is_bullet_or_step(line) or self._is_key_value(line):
            return False
        if re.match(r"^\d+(\.\d+)*\.?\s+\S+", line):
            return True
        if line.endswith(":"):
            return True
        if line.isupper() and len(words) <= 10:
            return True
        if line.istitle() and not re.search(r"[.!?]$", line):
            return True
        return False

    def _is_bullet_or_step(self, line: str) -> bool:
        return bool(re.match(r"^([-*]|\d+[.)]|[A-Za-z][.)])\s+", line))

    def _is_key_value(self, line: str) -> bool:
        return bool(re.match(r"^[A-Za-z][A-Za-z0-9 /_-]{1,50}:\s+\S+", line))

    def _is_table_like(self, line: str) -> bool:
        return "|" in line or len(re.findall(r"\s{2,}", line)) >= 2

    def _merge_small_blocks(self, blocks: list[_TextBlock]) -> list[_TextBlock]:
        merged: list[_TextBlock] = []
        pending: _TextBlock | None = None

        for block in blocks:
            if pending:
                block = _TextBlock(
                    text=f"{pending.text}\n\n{block.text}",
                    heading=pending.heading or block.heading,
                )
                pending = None

            if self._word_count(block.text) < self.min_chunk_size:
                if merged:
                    previous = merged[-1]
                    merged[-1] = _TextBlock(
                        text=f"{previous.text}\n\n{block.text}",
                        heading=previous.heading,
                    )
                else:
                    pending = block
                continue

            merged.append(block)

        if pending:
            if merged:
                previous = merged[-1]
                merged[-1] = _TextBlock(
                    text=f"{previous.text}\n\n{pending.text}",
                    heading=previous.heading,
                )
            else:
                merged.append(pending)

        return merged

    def _build_chunks(self, blocks: list[_TextBlock]) -> list[str]:
        chunks: list[str] = []
        current_parts: list[str] = []
        current_word_count = 0

        def flush_current() -> None:
            nonlocal current_parts, current_word_count
            if current_parts:
                chunks.append("\n\n".join(current_parts).strip())
                current_parts = []
                current_word_count = 0

        for block in blocks:
            block_word_count = self._word_count(block.text)

            if block_word_count > self.chunk_size:
                flush_current()
                chunks.extend(self._split_large_block(block))
                continue

            if current_parts and current_word_count + block_word_count > self.chunk_size:
                flush_current()

            current_parts.append(block.text)
            current_word_count += block_word_count

        flush_current()
        return chunks

    def _split_large_block(self, block: _TextBlock) -> list[str]:
        words = block.text.split()
        chunks: list[str] = []
        step = self.chunk_size - self.overlap
        start = 0

        while start < len(words):
            window = words[start : start + self.chunk_size]
            chunks.append(" ".join(window).strip())
            if start + self.chunk_size >= len(words):
                break
            start += step

        return chunks

    def _word_count(self, text: str) -> int:
        return len(text.split())
