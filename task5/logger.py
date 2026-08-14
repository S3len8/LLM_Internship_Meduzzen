import datetime
from config.constants import LOGS_DIR

def log_interactions(
    query: str,
    response: str,
    summary: str | None = None,
) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs_dir = LOGS_DIR
    logs_dir.mkdir(parents=True, exist_ok=True)
    file_path = logs_dir / "logs.md"

    logs_entry = (
        f"Timestamp: {timestamp}, Query: {query}, "
        f"Response: {response}, Summary: {summary}\n"
    )

    with file_path.open("a", encoding="utf-8") as file:
        file.write(logs_entry)
