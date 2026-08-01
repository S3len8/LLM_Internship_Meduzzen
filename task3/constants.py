from typing import Final


DEFAULT_INDEX_FILE: Final[str] = "faiss_index.bin"
DEFAULT_META_FILE: Final[str] = "metadata.pkl"
EMBEDDING_MODEL_NAME: Final[str] = "paraphrase-multilingual-MiniLM-L12-v2"
CHAT_MODEL_NAME: Final[str] = "llama-3.1-8b-instant"
DEFAULT_SYSTEM_PROMPT: Final[str] = (
    "You are a helpful educational assistant. Answer questions based ONLY on "
    "the provided context documents. Always mention which source file the "
    "information came from. Respond in Ukrainian.\n\n"
)
SUPPORTED_DOCUMENT_EXTENSIONS: Final[tuple[str, ...]] = (".md", ".txt")
