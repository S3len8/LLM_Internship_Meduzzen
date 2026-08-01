import pickle
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from constants import (
    DEFAULT_INDEX_FILE,
    DEFAULT_META_FILE,
    EMBEDDING_MODEL_NAME,
    SUPPORTED_DOCUMENT_EXTENSIONS,
)
from schemas import DocumentRecord, SearchResult


class VectorStore:
    documents: list[DocumentRecord]
    model: SentenceTransformer
    dimension: int
    index: faiss.Index
    index_file: Path
    meta_file: Path

    def __init__(
        self,
        index_file: str | Path = DEFAULT_INDEX_FILE,
        meta_file: str | Path = DEFAULT_META_FILE,
    ) -> None:
        self.documents = []
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME) 
        dimension = self.model.get_sentence_embedding_dimension()
        if dimension is None:
            raise RuntimeError(
                "The embedding model did not provide a vector dimension."
            )
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index_file = Path(index_file)
        self.meta_file = Path(meta_file)

    def _get_embeddings(self, text: str) -> np.ndarray:
        embedding = self.model.encode(text, convert_to_numpy=True).astype(
            "float32"
        )  # Get a float32 vector with the correct dimensions (1, dimension)
        embedding = np.expand_dims(embedding, axis=0)

        faiss.normalize_L2(embedding)  # Normalize the vector for L2/cosine similarity
        return embedding

    def add_text(self, text: str, metadata: dict[str, str] | None = None) -> int:
        doc_id = len(self.documents)

        vector = self._get_embeddings(text)
        self.index.add(vector)

        self.documents.append(
            {
                "id": doc_id,
                "text": text,
                "metadata": metadata,
            }
        )
        return doc_id

    def search(self, query: str, top_n: int = 3) -> list[SearchResult]:
        if not self.documents:
            return []

        query_vector = self._get_embeddings(query)

        scores, indices = self.index.search(query_vector, top_n)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(
                self.documents
            ):  # Handle cases where no results are returned
                results.append({"document": self.documents[idx], "score": float(score)})

        return results

    def save(self) -> None:
        """Save the FAISS index and metadata to disk."""
        faiss.write_index(self.index, str(self.index_file))
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.documents, f)
        print("Базу знань успішно збережено на диск!")

    def load(self) -> bool:
        """Load the FAISS index and metadata from disk."""
        if self.index_file.exists() and self.meta_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.meta_file, "rb") as f:
                self.documents = pickle.load(f)
            return True
        return False

    def load_documents(self) -> None:
        if self.load():
            print(
                f" Loaded the existing FAISS index ({self.index.ntotal} documents) from disk."
            )
            return

        print(" Первинна індексація: генерація векторів та створення FAISS індексу...")
        target_dir = Path.cwd() / "quantum_corpus"

        if target_dir.is_dir():
            for file_path in target_dir.iterdir():
                if (
                    file_path.is_file()
                    and file_path.suffix in SUPPORTED_DOCUMENT_EXTENSIONS
                ):
                    self.add_text(
                        text=file_path.read_text(encoding="utf-8"),
                        metadata={"source": file_path.name},
                    )
            self.save()

    def get_by_id(self, doc_id: int) -> DocumentRecord | None:
        for document in self.documents:
            if document["id"] == doc_id:
                return document
        return None
