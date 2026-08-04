from __future__ import annotations
import datetime
from pathlib import Path
from dotenv import load_dotenv
from chat_session import GroqChatSession
from schemas import SearchResult
from vector import VectorStore

load_dotenv()


def log_interactions(
    query: str,
    response: str,
    matches: list[SearchResult],
) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs_dir = Path.cwd() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    file_path = logs_dir / "logs.md"

    logs_entry = f"Timestamp: {timestamp}, Query: {query}, Response: {response}\n"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(logs_entry)


def main() -> None:
    print("Loading the knowledge base...")
    store = VectorStore()
    store.load_documents()

    if not store.documents:
        print(" Warning: The knowledge base is empty! Check the 'quantum_corpus' folder.")
        return

    chat = GroqChatSession()

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

            matches = store.search(query=user_query, top_n=3)

            print("\n-> Top 3 Matches:")
            if matches:
                for i, match in enumerate(matches, 1):
                    snippet = match.document.text.replace("\n", " ")[:80]
                    score = match.score
                    print(f'[{i}] "{snippet}..." (Score: {score:.2f})')
            else:
                print("Nothing was found.")

            ai_response = chat.get_response(query=user_query, context_documents=matches)

            print("\n-> Groq says:")
            print(ai_response)
            print("\n" + "-" * 50 + "\n")

            log_interactions(query=user_query, response=ai_response, matches=matches)

        except KeyboardInterrupt:
            print("\n\n Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n An error occurred: {e}\n")


if __name__ == "__main__":
    main()
