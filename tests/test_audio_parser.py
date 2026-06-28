from openrag.parsers import AudioParser


class FakeTranscriber:
    def __init__(self) -> None:
        self.calls = []

    def transcribe(self, path: str, **options):
        self.calls.append((path, options))
        return {
            "text": "This meeting discussed the leave policy.",
            "language": "en",
            "segments": [{"start": 0.0, "end": 2.5, "text": "This meeting"}],
        }


def test_audio_parser_transcribes_audio_to_document(tmp_path) -> None:
    audio_file = tmp_path / "meeting.mp3"
    audio_file.write_bytes(b"fake audio")
    transcriber = FakeTranscriber()
    parser = AudioParser(language="en", transcriber=transcriber)

    document = parser.parse(str(audio_file))

    assert document.text == "This meeting discussed the leave policy."
    assert document.metadata["file_type"] == "audio"
    assert document.metadata["file_name"] == "meeting.mp3"
    assert document.metadata["language"] == "en"
    assert document.metadata["segments"][0]["start"] == 0.0
    assert transcriber.calls == [(str(audio_file), {"language": "en"})]
