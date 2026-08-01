from typing import TypedDict


class DocumentRecord(TypedDict):
    id: int
    text: str
    metadata: dict[str, str] | None


class SearchResult(TypedDict):
    document: DocumentRecord
    score: float
