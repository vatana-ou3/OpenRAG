from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from openrag.core.document import Document
from openrag.parsers.base import BaseParser


class PdfPage(Protocol):
    def extract_text(self) -> str | None:
        """Extract text from one PDF page."""


class PdfReader(Protocol):
    pages: list[PdfPage]

    def __enter__(self) -> "PdfReader":
        """Open the PDF reader context."""

    def __exit__(self, *args: Any) -> None:
        """Close the PDF reader context."""


class PdfParser(BaseParser):
    """Extract text from PDF files using pdfplumber."""

    supported_extensions = {".pdf"}

    def __init__(self, reader_factory: Any | None = None) -> None:
        self._reader_factory = reader_factory

    def parse(self, path: str) -> Document:
        file_path = Path(path)
        reader_factory = self._get_reader_factory()

        page_texts: list[str] = []
        with reader_factory(str(file_path)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    page_texts.append(text.strip())

        return Document(
            id=str(uuid4()),
            text="\n\n".join(page_texts),
            metadata={
                "source": str(file_path),
                "file_name": file_path.name,
                "file_type": "pdf",
                "page_count": len(page_texts),
            },
        )

    def _get_reader_factory(self) -> Any:
        if self._reader_factory is None:
            try:
                import pdfplumber
            except ImportError as error:
                raise ImportError(
                    "PDF parsing requires pdfplumber. Install it with "
                    "`pip install -e .[pdf]` or `pip install -e .[documents]`."
                ) from error

            self._reader_factory = pdfplumber.open

        return self._reader_factory
