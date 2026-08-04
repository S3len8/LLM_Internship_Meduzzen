from typing import Final
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Constants(BaseSettings):
    API_KEY: str
    DEFAULT_INDEX_FILE: str
    DEFAULT_META_FILE: str
    EMBEDDING_MODEL_NAME: str
    CHAT_MODEL_NAME: str
    DEFAULT_SYSTEM_PROMPT: Final[str] = (
    "You are a helpful educational assistant. Answer questions based ONLY on "
    "the provided context documents. Always mention which source file the "
    "information came from. Respond in English.\n\n"
    )
    SUPPORTED_DOCUMENT_EXTENSIONS: Final[tuple[str, ...]] = (".md", ".txt")

    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, ".env"),
                                      env_file_encoding="utf-8",
                                      extra="ignore")

constants = Constants()