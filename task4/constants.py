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
    CHAT_AUDIO_TRANSCRIPTION_MODEL: str = "whisper-large-v3"
    DEFAULT_SYSTEM_PROMPT_RESPONSE: Final[str] = (
    "You are a helpful educational assistant. Answer questions based ONLY on "
    "the provided context documents. Always mention which source file the "
    "information came from. Respond in English.\n\n"
    )
    DEFAULT_SYSTEM_PROMPT_SUMMARY: Final[str] = (
        "Summarize the following English transcript. Provide a concise summary "
        "and list the main points. Respond in English."
    )
    SUPPORTED_AUDIO_EXTENSIONS: Final[tuple[str, ...]] = (".mp3", ".wav", ".m4a")

    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, ".env"),
                                      env_file_encoding="utf-8",
                                      extra="ignore")

constants = Constants()
