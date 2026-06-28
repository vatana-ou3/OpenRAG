from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """A smaller piece of a document used for retrieval."""

    id: str
    document_id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
