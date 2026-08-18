from typing import Final

DEFAULT_INDEX_FILE: str = "faiss_index.bin"
DEFAULT_META_FILE: str = "metadata.pkl"
EMBEDDING_MODEL_NAME: str = "paraphrase-multilingual-MiniLM-L12-v2"
CHAT_MODEL_NAME: str = "openai/gpt-oss-20b"
CHAT_AUDIO_TRANSCRIPTION_MODEL: str = "whisper-large-v3"
SUPPORTED_AUDIO_EXTENSIONS: Final[tuple[str, ...]] = (".mp3", ".wav", ".m4a")
