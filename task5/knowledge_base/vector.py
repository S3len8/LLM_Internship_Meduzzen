import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config.settings import BASE_DIR
from config.constants import (
    EMBEDDING_MODEL_NAME,
    DEFAULT_INDEX_FILE,
    DEFAULT_META_FILE,
)
from schemas import DocumentInput, DocumentRecord, SearchRequest, SearchResult


class VectorStore:
    def __init__(self) -> None:
        self.documents = []
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        dimension = self.model.get_sentence_embedding_dimension()
        if dimension is None:
            raise RuntimeError(
                "The embedding model did not provide a vector dimension."
            )
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index_file = BASE_DIR / DEFAULT_INDEX_FILE
        self.meta_file = BASE_DIR / DEFAULT_META_FILE
        self.load()

    def _get_embeddings(self, text: str) -> np.ndarray:
        embedding = self.model.encode(text, convert_to_numpy=True).astype(
            "float32"
        )  # Get a float32 vector with the correct dimensions (1, dimension)
        embedding = np.expand_dims(embedding, axis=0)

        faiss.normalize_L2(embedding)  # Normalize the vector for L2/cosine similarity
        return embedding

    def add_text(self, text: str, metadata: dict[str, str] | None = None) -> int:
        document_input = DocumentInput(text=text, metadata=metadata)
        doc_id = len(self.documents)

        vector = self._get_embeddings(document_input.text)
        self.index.add(vector)

        self.documents.append(
            DocumentRecord(
                id=doc_id,
                text=document_input.text,
                metadata=document_input.metadata,
            )
        )
        return doc_id

    def has_source(self, source: str) -> bool:
        return any(
            (document.metadata or {}).get("source") == source
            for document in self.documents
        )

    def search(self, query: str, top_n: int = 3) -> list[SearchResult]:
        search_request = SearchRequest(
            query=query,
            top_n=top_n,
        )

        if not self.documents:
            return []

        query_vector = self._get_embeddings(search_request.query)

        scores, indices = self.index.search(
            query_vector,
            search_request.top_n,
        )

        results: list[SearchResult] = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            if index >= len(self.documents):
                continue

            results.append(
                SearchResult(
                    document=self.documents[index],
                    score=float(score),
                )
            )

        return results

    def save(self) -> None:
        """Save the FAISS index and metadata to disk."""
        faiss.write_index(self.index, str(self.index_file))
        with open(self.meta_file, "wb") as f:
            pickle.dump([document.model_dump() for document in self.documents], f)
        print("Knowledge base successfully saved to disk!")

    def load(self) -> bool:
        """Load the FAISS index and metadata from disk."""
        if self.index_file.exists() and self.meta_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.meta_file, "rb") as f:
                raw_documents = pickle.load(f)
            self.documents = [
                DocumentRecord.model_validate(document)
                for document in raw_documents
            ]
            return True
        return False
