import datetime
from config.settings import LOGS_DIR

def log_interactions(
    query: str,
    response: str,
    summary: str | None = None,
) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = LOGS_DIR / "logs.md"

    logs_entry = (
        f"Timestamp: {timestamp}, Query: {query}, "
        f"Response: {response}, Summary: {summary}\n"
    )

    with file_path.open("a", encoding="utf-8") as file:
        file.write(logs_entry)
