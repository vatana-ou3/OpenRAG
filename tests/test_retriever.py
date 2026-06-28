from openrag.core import Chunk
from openrag.retrievers import KeywordRetriever


def test_keyword_retriever_returns_matching_chunks_by_score() -> None:
    chunks = [
        Chunk(id="1", document_id="doc", text="Vacation policy and paid leave"),
        Chunk(id="2", document_id="doc", text="Office lunch menu"),
        Chunk(id="3", document_id="doc", text="Leave requests require manager approval"),
    ]
    retriever = KeywordRetriever()
    retriever.index(chunks)

    results = retriever.retrieve("leave policy", top_k=2)

    assert [chunk.id for chunk in results] == ["1", "3"]


def test_keyword_retriever_returns_empty_list_without_matches() -> None:
    retriever = KeywordRetriever()
    retriever.index([Chunk(id="1", document_id="doc", text="Office lunch menu")])

    assert retriever.retrieve("vacation") == []


def test_keyword_retriever_respects_top_k() -> None:
    retriever = KeywordRetriever()
    retriever.index(
        [
            Chunk(id="1", document_id="doc", text="policy"),
            Chunk(id="2", document_id="doc", text="policy"),
        ]
    )

    assert len(retriever.retrieve("policy", top_k=1)) == 1
