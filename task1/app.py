"""Command-line interface for the multi-turn chat application."""

from __future__ import annotations
import argparse
from groq import (
    APIError,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from chat_session import ChatConfigurationError, ChatSession
from constants import EXIT_COMMANDS
import os
from dotenv import load_dotenv

load_dotenv()



def parse_args() -> argparse.Namespace:
    """Parse optional CLI configuration."""
    parser = argparse.ArgumentParser(
        description="Start a multi-turn Groq tutor chat in the terminal."
    )
    parser.add_argument(
        "-prompt",
        "--prompt",
        dest="system_prompt",
        help="Override the default tutor system prompt.",
    )
    parser.add_argument(
        "--model",
        default="llama-3.3-70b-versatile",
        help="Groq model name (default: llama-3.3-70b-versatile).",
    )
    return parser.parse_args()


def show_usage(session: ChatSession) -> None:
    """Print token usage for the last request and the whole session."""
    usage = session.last_usage
    print(
        "[Tokens — "
        f"input: {usage['input_tokens']} | "
        f"output: {usage['output_tokens']} | "
        f"request: {usage['total_tokens']} | "
        f"session: {session.total_usage['total_tokens']}]"
    )


def save_and_report(session: ChatSession) -> None:
    """Save the session and print its final summary."""
    path = session.save_log()
    summary = session.get_summary()
    print(
        f"Session summary: {summary['completed_turns']} completed turn(s), "
        f"{summary['total_tokens']} token(s)."
    )
    print(f"Conversation saved to: {path}")


def run_chat(session: ChatSession) -> None:
    """Run the interactive input/streaming output loop."""
    print(f"System Prompt: {session.system_prompt}")
    print(f"Model: {session.model}")
    print("Type 'quit', 'exit', or 'q' to finish.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in EXIT_COMMANDS:
            break

        print("[Assistant is typing...]")
        print("Assistant: ", end="", flush=True)

        try:
            for text_chunk in session.get_response(user_input):
                print(text_chunk, end="", flush=True)
            print()
            show_usage(session)
        except AuthenticationError:
            print()
            print("Authentication failed. Check GROQ_API_KEY in your .env file.")
        except RateLimitError:
            print()
            print("Rate limit exceeded (429). Wait and try again later.")
        except APITimeoutError:
            print()
            print("The request timed out. Please try again.")
        except APIConnectionError:
            print()
            print("Could not connect to Groq. Check your internet connection.")
        except APIStatusError as error:
            print()
            print(f"Groq returned HTTP {error.status_code}. Please try again.")
        except APIError:
            print()
            print("The Groq request failed. Please try again.")
        except (RuntimeError, ValueError) as error:
            print()
            print(f"Could not complete the response: {error}")
        except OSError as error:
            print()
            print(f"The response completed, but the log could not be saved: {error}")

    save_and_report(session)


def main() -> int:
    """Create the chat session and handle application-level shutdown."""
    args = parse_args()

    api_key = os.getenv("API_KEY")

    try:
        session = ChatSession(model=args.model, system_prompt=args.system_prompt, api_key=api_key)
    except ChatConfigurationError as error:
        print(f"Configuration error: {error}")
        return 1

    try:
        run_chat(session)
    except KeyboardInterrupt:
        print("\nChat interrupted by the user.")
        save_and_report(session)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())