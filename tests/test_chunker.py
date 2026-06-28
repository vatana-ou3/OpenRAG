import pytest

from openrag.chunkers import SimpleChunker
from openrag.core import Document


def test_simple_chunker_splits_text_with_overlap() -> None:
    document = Document(id="doc-1", text="abcdefghij", metadata={"source": "sample.txt"})
    chunker = SimpleChunker(chunk_size=4, overlap=1)

    chunks = chunker.chunk(document)

    assert [chunk.text for chunk in chunks] == ["abcd", "defg", "ghij", "j"]
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].metadata["source"] == "sample.txt"
    assert chunks[1].metadata["start"] == 3


def test_simple_chunker_returns_empty_list_for_empty_document() -> None:
    document = Document(id="doc-1", text="   ")

    chunks = SimpleChunker().chunk(document)

    assert chunks == []


def test_simple_chunker_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        SimpleChunker(chunk_size=100, overlap=100)
