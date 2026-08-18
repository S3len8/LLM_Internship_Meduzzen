from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field, field_validator
from config.constants import (
    SUPPORTED_AUDIO_EXTENSIONS,
)


class QueryInput(BaseModel):
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query must not be blank.")
        return value


class SearchRequest(QueryInput):
    top_n: int = Field(default=3, ge=1, le=10)


class AudioFileInput(BaseModel):
    file_name: str = Field(min_length=1)

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Audio file name must not be blank.")

        path = Path(value)
        if path.is_absolute() or path.name != value:
            raise ValueError("Only a file name inside audio_files is allowed.")

        if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
            raise ValueError(f"File extension not supported: {path.suffix}")

        return value


class TranscriptInput(BaseModel):
    text: str = Field(min_length=1)
    source: str = Field(min_length=1)

    @field_validator("text", "source")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Transcript fields must not be blank.")
        return value


class AudioChunkMetadata(BaseModel):
    source: str = Field(min_length=1)
    type: Literal["audio"]
    chunk_id: str = Field(min_length=1)

    @field_validator("source", "chunk_id")
    @classmethod
    def metadata_fields_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Metadata fields must not be blank.")
        return value


class ChunkingRequest(BaseModel):
    chunk_size: int = Field(default=500, ge=1)
    overlap: int = Field(default=50, ge=0)

    @field_validator("overlap")
    @classmethod
    def overlap_must_be_smaller_than_chunk_size(
        cls,
        value: int,
        info,
    ) -> int:
        chunk_size = info.data.get("chunk_size")
        if chunk_size is not None and value >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk_size.")
        return value


class DocumentInput(BaseModel):
    text: str = Field(min_length=1)
    metadata: dict[str, str] | None = None

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value.strip():
            raise ValueError("Document text must not be blank.")
        return value


class DocumentRecord(BaseModel):
    id: int = Field(ge=0)
    text: str = Field(min_length=1)
    metadata: dict[str, str] | None = None


class SearchResult(BaseModel):
    document: DocumentRecord
    score: float = Field(ge=-1.0, le=1.0)
