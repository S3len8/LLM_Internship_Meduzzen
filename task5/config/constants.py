from typing import Final
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env"
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio_files"
LOGS_DIR = DATA_DIR / "logs"
SESSIONS_DIR = DATA_DIR / "sessions"

class Constants(BaseSettings):
    API_KEY: str
    DEFAULT_INDEX_FILE: str
    DEFAULT_META_FILE: str
    EMBEDDING_MODEL_NAME: str
    CHAT_MODEL_NAME: str
    CHAT_AUDIO_TRANSCRIPTION_MODEL: str = "whisper-large-v3"
    SUPPORTED_AUDIO_EXTENSIONS: Final[tuple[str, ...]] = (".mp3", ".wav", ".m4a")

    model_config = SettingsConfigDict(env_file=ENV_FILE,
                                      env_file_encoding="utf-8",
                                      extra="ignore")

constants = Constants()
