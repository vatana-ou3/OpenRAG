from pathlib import Path
from uuid import uuid4

from openrag.core.document import Document
from openrag.parsers.base import BaseParser


class TxtParser(BaseParser):
    """Load plain text files into Document objects."""

    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def parse(self, path: str) -> Document:
        file_path = Path(path)
        text = file_path.read_text(encoding=self.encoding)

        return Document(
            id=str(uuid4()),
            text=text,
            metadata={
                "source": str(file_path),
                "file_name": file_path.name,
                "file_type": "txt",
            },
        )
