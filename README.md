# OpenRAG

OpenRAG is a small, beginner-friendly Python framework for local retrieval-augmented generation (RAG).

The first version keeps the foundation intentionally simple:

- Load TXT documents
- Split text into chunks
- Store chunks in memory
- Retrieve chunks with keyword search
- Generate answers with a local Ollama model
- Return answers with source references

It does not use LangChain or LlamaIndex. The goal is to provide a clean base that can grow later with PDF/DOCX parsers, embedding models, vector databases, and hybrid retrieval.

## Installation

From this repository:

```bash
pip install -e ".[dev]"
```

You also need Ollama running locally for answer generation:

```bash
ollama serve
ollama pull llama3.2
```

## Quick Start

```python
from openrag import RAG

rag = RAG()
rag.add("docs/policy.txt")

answer = rag.ask("What is the leave policy?")
print(answer)
```

## How It Works

OpenRAG is built from small interchangeable components:

- `BaseParser`: loads a file into a `Document`
- `BaseChunker`: turns a `Document` into `Chunk` objects
- `BaseRetriever`: indexes and retrieves chunks
- `BaseGenerator`: turns a query and chunks into an answer
- `RAG`: coordinates the full flow

The default pipeline uses:

- `TxtParser`
- `SimpleChunker`
- `KeywordRetriever`
- `OllamaGenerator`

## Custom Components

You can swap components when creating `RAG`:

```python
from openrag import RAG
from openrag.chunkers import SimpleChunker
from openrag.retrievers import KeywordRetriever

rag = RAG(
    chunker=SimpleChunker(chunk_size=500, overlap=50),
    retriever=KeywordRetriever(),
)
```

Future components can implement the base interfaces in `openrag.parsers`, `openrag.chunkers`, `openrag.retrievers`, and `openrag.generators`.

## Running Tests

```bash
pytest
```

## Project Status

OpenRAG is experimental and intentionally small. Version `0.1.0` is a foundation for local RAG experiments, not a full production RAG platform.
