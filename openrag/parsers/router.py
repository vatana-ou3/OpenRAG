from pathlib import Path

from openrag.core.document import Document
from openrag.parsers.audio_parser import AudioParser
from openrag.parsers.base import BaseParser
from openrag.parsers.docx_parser import DocxParser
from openrag.parsers.pdf_parser import PdfParser
from openrag.parsers.txt_parser import TxtParser


class ParserRouter(BaseParser):
    """Choose a parser based on the file extension."""

    def __init__(self, parsers: dict[str, BaseParser] | None = None) -> None:
        self.parsers: dict[str, BaseParser] = {}
        if parsers:
            for extension, parser in parsers.items():
                self.register(extension, parser)

    @classmethod
    def with_defaults(cls) -> "ParserRouter":
        router = cls()
        router.register(".txt", TxtParser())
        router.register(".pdf", PdfParser())
        router.register(".docx", DocxParser())

        audio_parser = AudioParser()
        for extension in AudioParser.supported_extensions:
            router.register(extension, audio_parser)

        return router

    def register(self, extension: str, parser: BaseParser) -> None:
        normalized = extension.lower()
        if not normalized.startswith("."):
            normalized = f".{normalized}"
        self.parsers[normalized] = parser

    def parse(self, path: str) -> Document:
        extension = Path(path).suffix.lower()
        parser = self.parsers.get(extension)
        if parser is None:
            supported = ", ".join(sorted(self.parsers))
            raise ValueError(
                f"No parser registered for '{extension}'. Supported extensions: {supported}"
            )

        return parser.parse(path)
