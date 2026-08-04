from pydantic import BaseModel, Field, field_validator


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
    top_n: int = Field(default=3, ge=1)


class DocumentInput(BaseModel):
    text: str = Field(min_length=1)
    metadata: dict[str, str] | None = None

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Document text must not be blank.")
        return value


class DocumentRecord(BaseModel):
    id: int
    text: str
    metadata: dict[str, str] | None = None


class SearchResult(BaseModel):
    document: DocumentRecord
    score: float
