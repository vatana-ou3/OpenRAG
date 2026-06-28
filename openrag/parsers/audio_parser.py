from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from openrag.core.document import Document
from openrag.parsers.base import BaseParser


class WhisperTranscriber(Protocol):
    def transcribe(self, path: str, **options: Any) -> dict[str, Any]:
        """Transcribe an audio file and return Whisper-style data."""


class AudioParser(BaseParser):
    """Transcribe audio files into Document objects using Whisper."""

    supported_extensions = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

    def __init__(
        self,
        model_name: str = "base",
        language: str | None = None,
        transcriber: WhisperTranscriber | None = None,
    ) -> None:
        self.model_name = model_name
        self.language = language
        self._transcriber = transcriber

    def parse(self, path: str) -> Document:
        file_path = Path(path)
        transcriber = self._get_transcriber()

        options: dict[str, Any] = {}
        if self.language:
            options["language"] = self.language

        result = transcriber.transcribe(str(file_path), **options)
        text = str(result.get("text", "")).strip()

        return Document(
            id=str(uuid4()),
            text=text,
            metadata={
                "source": str(file_path),
                "file_name": file_path.name,
                "file_type": "audio",
                "language": result.get("language", self.language),
                "segments": result.get("segments", []),
            },
        )

    def _get_transcriber(self) -> WhisperTranscriber:
        if self._transcriber is None:
            try:
                import whisper
            except ImportError as error:
                raise ImportError(
                    "Audio parsing requires Whisper. Install it with "
                    "`pip install -e .[audio]`."
                ) from error

            self._transcriber = whisper.load_model(self.model_name)

        return self._transcriber
