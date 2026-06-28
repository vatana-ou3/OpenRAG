import pytest

from openrag.chunkers import MabChunker
from openrag.core import Document


def test_mab_chunker_preserves_heading_context() -> None:
    document = Document(
        id="doc-1",
        text=(
            "Leave Policy\n"
            "Employees receive annual leave after probation.\n"
            "- Requests must be submitted early.\n"
            "- Managers approve requests.\n\n"
            "Benefits\n"
            "Health insurance is available."
        ),
        metadata={"source": "sample.txt"},
    )
    chunker = MabChunker(chunk_size=40, overlap=5, min_chunk_size=5)

    chunks = chunker.chunk(document)

    assert "Leave Policy" in chunks[0].text
    assert "Employees receive annual leave" in chunks[0].text
    assert "- Requests must be submitted early." in chunks[0].text
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].metadata["source"] == "sample.txt"
    assert chunks[0].metadata["chunker"] == "mab"


def test_mab_chunker_normalizes_text_before_chunking() -> None:
    document = Document(
        id="doc-1",
        text="Leave\tPolicy\nEmployees  can apply.ThenManagers review it.",
    )

    chunks = MabChunker(chunk_size=30, overlap=5, min_chunk_size=1).chunk(document)

    assert chunks[0].text == "Leave Policy\nEmployees can apply. Then Managers review it."


def test_mab_chunker_splits_large_blocks_with_word_overlap() -> None:
    text = " ".join(f"word{i}" for i in range(12))
    document = Document(id="doc-1", text=text)
    chunker = MabChunker(chunk_size=5, overlap=2, min_chunk_size=1)

    chunks = chunker.chunk(document)

    assert [chunk.text for chunk in chunks] == [
        "word0 word1 word2 word3 word4",
        "word3 word4 word5 word6 word7",
        "word6 word7 word8 word9 word10",
        "word9 word10 word11",
    ]


def test_mab_chunker_merges_small_chunks_with_nearby_content() -> None:
    document = Document(
        id="doc-1",
        text="Short Note\nTiny bit.\n\nLong Section\nThis section has enough words to stand near the short note.",
    )

    chunks = MabChunker(chunk_size=50, overlap=5, min_chunk_size=6).chunk(document)

    assert len(chunks) == 1
    assert "Short Note" in chunks[0].text
    assert "Long Section" in chunks[0].text


def test_mab_chunker_rejects_invalid_min_chunk_size() -> None:
    with pytest.raises(ValueError):
        MabChunker(min_chunk_size=-1)
