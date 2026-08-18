from pathlib import Path
from groq import Groq
from constants import (
    CHAT_AUDIO_TRANSCRIPTION_MODEL,
)
from schemas import AudioFileInput, ChunkingRequest, TranscriptInput


class FileTranscription:
    def __init__(self, client: Groq) -> None:
        self.client = client
        self.model: str = CHAT_AUDIO_TRANSCRIPTION_MODEL
        self.audio_dir: Path = Path(__file__).resolve().parent / "audio_files"

    def get_file(self, file_name: str) -> Path:
        file_input = AudioFileInput(file_name=file_name)
        audio_dir = self.audio_dir.resolve()
        file_path = (audio_dir / file_input.file_name).resolve()

        if not file_path.is_relative_to(audio_dir):
            raise ValueError("Audio file must be located inside task4/audio_files.")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise IsADirectoryError(f"Expected a file, but got: {file_path}")

        return file_path

    def get_transcription(self, file_name: str) -> str:
        file_path = self.get_file(file_name)

        with file_path.open("rb") as file:
            response = self.client.audio.transcriptions.create(
                file=file,
                model=self.model,
                language="en",
            )

        transcript = TranscriptInput(text=response.text, source=file_name)
        return transcript.text

    def split_into_chunks(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        chunking_request = ChunkingRequest(
            chunk_size=chunk_size,
            overlap=overlap,
        )
        text = TranscriptInput(text=text, source="transcript").text
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = min(start + chunking_request.chunk_size, len(words))
            chunks.append(" ".join(words[start:end]))

            if end == len(words):
                break

            start = end - chunking_request.overlap

        return chunks
