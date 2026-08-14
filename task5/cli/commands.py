from schemas import AudioChunkMetadata
from knowledge_base.transcription import FileTranscription
from knowledge_base.vector import VectorStore


class Commands:
    """CLI commands that are called directly by the user."""

    def __init__(
        self,
        store: VectorStore,
        transcription: FileTranscription,
    ) -> None:
        self.store = store
        self.transcription = transcription

    def update_text(self, text: str | None = None) -> str:
        if text is None:
            print("Assistant: Please enter your fact:")
            text = input("> User: ")

        text = text.strip()
        if not text:
            raise ValueError("Knowledge text cannot be empty.")

        document_id = self.store.add_text(
            text=text,
            metadata={
                "source": "manual_text",
                "type": "text",
            },
        )
        self.store.save()

        return f"Knowledge added successfully. Document ID: {document_id}"

    def update_voice(self, file_name: str | None = None) -> str:
        if file_name is None:
            print("Assistant: Enter audio file path:")
            file_name = input("> User: ")

        file_name = file_name.strip()
        if not file_name:
            raise ValueError("Audio file name cannot be empty.")

        if self.store.has_source(file_name):
            return f"File already indexed: {file_name}"

        transcript = self.transcription.get_transcription(file_name=file_name)
        chunks = self.transcription.split_into_chunks(transcript)

        for index, chunk in enumerate(chunks):
            metadata = AudioChunkMetadata(
                source=file_name,
                type="audio",
                chunk_id=str(index),
            )
            self.store.add_text(
                text=chunk,
                metadata=metadata.model_dump(),
            )

        self.store.save()

        return (
            f'[Transcribed: "{transcript}"]\n'
            f"Audio added to the knowledge base in {len(chunks)} chunk(s)."
        )
