from openrag.parsers import DocxParser


class FakeParagraph:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeDocxDocument:
    paragraphs = [
        FakeParagraph("Leave Policy"),
        FakeParagraph(""),
        FakeParagraph("Employees receive paid leave."),
    ]


def test_docx_parser_extracts_paragraph_text(tmp_path) -> None:
    docx_file = tmp_path / "benefits.docx"
    docx_file.write_bytes(b"fake docx")
    parser = DocxParser(document_factory=lambda path: FakeDocxDocument())

    document = parser.parse(str(docx_file))

    assert document.text == "Leave Policy\n\nEmployees receive paid leave."
    assert document.metadata["file_type"] == "docx"
    assert document.metadata["file_name"] == "benefits.docx"
    assert document.metadata["paragraph_count"] == 2
