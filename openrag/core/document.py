from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """A source document loaded by a parser."""

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
