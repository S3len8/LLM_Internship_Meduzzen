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
    SUPPORTED_AUDIO_EXTENSIONS: Final[tuple[str, ...]] = (".mp3", ".wav", ".m4a")

    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, ".env"),
                                      env_file_encoding="utf-8",
                                      extra="ignore")

constants = Constants()
