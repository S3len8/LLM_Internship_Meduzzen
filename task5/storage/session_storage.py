import json
from pathlib import Path
from typing import Any
from config.settings import SESSIONS_DIR

class SessionStorage:
    def __init__(
        self,
        directory: str | Path = SESSIONS_DIR,
        filename: str = "session.json",
    ) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.file_path = self.directory / filename

    def save(self, messages: list[dict[str, Any]]) -> str:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(
                messages,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return str(self.file_path)

    def load(self) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            raise FileNotFoundError("Session storage not found")

        with self.file_path.open("r", encoding="utf-8") as file:
            messages = json.load(file)

        return messages
