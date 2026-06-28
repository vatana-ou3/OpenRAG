from openrag.parsers import PdfParser


class FakePage:
    def __init__(self, text: str | None) -> None:
        self._text = text

    def extract_text(self) -> str | None:
        return self._text


class FakePdf:
    def __init__(self) -> None:
        self.pages = [
            FakePage("First page text"),
            FakePage(None),
            FakePage("Second page text"),
        ]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None


def test_pdf_parser_extracts_page_text(tmp_path) -> None:
    pdf_file = tmp_path / "handbook.pdf"
    pdf_file.write_bytes(b"fake pdf")
    parser = PdfParser(reader_factory=lambda path: FakePdf())

    document = parser.parse(str(pdf_file))

    assert document.text == "First page text\n\nSecond page text"
    assert document.metadata["file_type"] == "pdf"
    assert document.metadata["file_name"] == "handbook.pdf"
    assert document.metadata["page_count"] == 2
