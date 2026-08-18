from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env"
DATA_DIR = BASE_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio_files"
LOGS_DIR = DATA_DIR / "logs"
SESSIONS_DIR = DATA_DIR / "sessions"

class Settings(BaseSettings):
    API_KEY: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )
