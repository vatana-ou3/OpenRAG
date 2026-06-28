# OpenRAG

OpenRAG is a small, beginner-friendly Python framework for local retrieval-augmented generation (RAG).

The first version keeps the foundation intentionally simple:

- Load TXT documents
- Load PDF documents with pdfplumber
- Load DOCX documents with python-docx
- Load audio files with Whisper
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

Audio parsing is optional because Whisper is a heavier dependency:

```bash
pip install -e ".[audio]"
```

PDF and DOCX parsing are optional document dependencies:

```bash
pip install -e ".[documents]"
```

## Quick Start

```python
from openrag import RAG

rag = RAG()
rag.add("docs/policy.txt")
rag.add("docs/handbook.pdf")
rag.add("docs/benefits.docx")
rag.add("recordings/meeting.mp3")

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
- `PdfParser`
- `DocxParser`
- `AudioParser`
- `ParserRouter`
- `MabChunker`
- `KeywordRetriever`
- `OllamaGenerator`

## Custom Components

You can swap components when creating `RAG`:

```python
from openrag import RAG
from openrag.chunkers import MabChunker, SimpleChunker
from openrag.retrievers import KeywordRetriever

# Good for plain text when you only need basic character windows.
simple_rag = RAG(
    chunker=SimpleChunker(chunk_size=800, overlap=100),
)

# Good for mixed TXT, PDF, DOCX, and audio transcripts.
rag = RAG(
    chunker=MabChunker(chunk_size=260, overlap=50),
    retriever=KeywordRetriever(),
)
```

Future components can implement the base interfaces in `openrag.parsers`, `openrag.chunkers`, `openrag.retrievers`, and `openrag.generators`.

## Chunking Strategies

OpenRAG includes two chunkers:

- `SimpleChunker`: basic fixed-size character chunks with character overlap
- `MabChunker`: advanced structure-aware word chunks for mixed document types

The default `RAG()` pipeline uses `MabChunker`. It:

- Normalizes text before chunking by cleaning line breaks, tabs, extra spaces, and merged sentences
- Detects common structures such as headings, numbered sections, bullets, steps, key-value fields, and table-like lines
- Keeps headings attached to the content that follows them
- Groups related paragraphs, lists, and structured records before applying size limits
- Limits chunks to about 260 words by default
- Uses 50 words of overlap when a large section must be split
- Merges chunks shorter than 25 words with nearby content when possible
- Falls back to word-window splitting for long or poorly formatted content

## Parser Roadmap

OpenRAG currently supports TXT, PDF, DOCX, and audio files. Planned parser support:

- Markdown
- CSV
- Video, using MoviePy to extract audio and Whisper for transcription

HTML parsing is intentionally out of scope for now.

## Running Tests

```bash
pytest
```

## Project Status

OpenRAG is experimental and intentionally small. Version `0.1.0` is a foundation for local RAG experiments, not a full production RAG platform.
