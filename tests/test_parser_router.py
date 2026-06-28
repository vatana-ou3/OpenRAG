import pytest

from openrag.parsers import ParserRouter, TxtParser


def test_parser_router_uses_registered_parser(tmp_path) -> None:
    text_file = tmp_path / "notes.txt"
    text_file.write_text("Local RAG notes", encoding="utf-8")
    router = ParserRouter({".txt": TxtParser()})

    document = router.parse(str(text_file))

    assert document.text == "Local RAG notes"
    assert document.metadata["file_type"] == "txt"


def test_parser_router_rejects_unsupported_extension(tmp_path) -> None:
    file_path = tmp_path / "notes.pdf"
    file_path.write_text("not supported yet", encoding="utf-8")
    router = ParserRouter({".txt": TxtParser()})

    with pytest.raises(ValueError, match="No parser registered"):
        router.parse(str(file_path))
