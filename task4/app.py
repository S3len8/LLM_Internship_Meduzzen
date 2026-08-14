import datetime
from pathlib import Path
from chat_session import GroqChatSession
from schemas import AudioChunkMetadata
from vector import VectorStore
from transcription import FileTranscription


def log_interactions(
    query: str,
    response: str,
    summary: str = None,
) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_path = logs_dir / "logs.md"

    logs_entry = f"Timestamp: {timestamp}, Query: {query}, Response: {response}, Summary: {summary}\n"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(logs_entry)


def main() -> None:
    print("Loading the knowledge base...")
    store = VectorStore()
    store.load()

    chat = GroqChatSession()
    transcription = FileTranscription()

    print("\n" + "=" * 50)
    print(" Knowledge-base chat is ready! Enter 'exit' or 'quit' to leave.")
    print("=" * 50 + "\n")

    while True:
        try:
            user_query = input("> You: ").strip()

            if user_query.lower() in ["exit", "quit", "вихід", "q"]:
                print("\n Goodbye!")
                break

            if not user_query:
                continue

            if user_query.lower().startswith("file:"):
                file_name = user_query.split(":", 1)[1].strip()

                if not file_name:
                    raise ValueError(
                        "After command file: must be a file name"
                    )

                if store.has_source(file_name):
                    print(f"File already indexed: {file_name}")
                    continue

                full_transcription = transcription.get_transcription(file_name=file_name)

                print("\n-> Full transcription:")
                print(full_transcription)

                summary = chat.summary(summary=full_transcription)

                print(f"Summary: {summary}")
                chunks = transcription.split_into_chunks(full_transcription)

                for index, chunk in enumerate(chunks):
                    chunk_metadata = AudioChunkMetadata(
                        source=file_name,
                        type="audio",
                        chunk_id=str(index),
                    )

                    store.add_text(
                        text=chunk,
                        metadata=chunk_metadata.model_dump(),
                    )

                store.save()

                log_interactions(query=user_query, response=full_transcription, summary=summary)

                continue

            matches = store.search(query=user_query)

            ai_response = chat.get_response(query=user_query, matches=matches)

            print("\n-> Groq says:")
            print(ai_response)
            print("\n" + "-" * 50 + "\n")

            log_interactions(query=user_query, response=ai_response)

        except KeyboardInterrupt:
            print("\n\n Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n An error occurred: {e}\n")


if __name__ == "__main__":
    main()
