import argparse
from rich.console import Console
from rich.panel import Panel
from chat.chat_session import GroqChatSession
from cli.commands import Commands
from config.commands_name import CommandsName
from chat.tools import Tools
from knowledge_base.transcription import FileTranscription
from knowledge_base.vector import VectorStore
from logger import log_interactions
from storage.session_storage import SessionStorage
from tts import TextToSpeech


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the CLI knowledge-base assistant."
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Chat model name. Defaults to CHAT_MODEL_NAME from .env.",
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Speak the assistant's responses aloud.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    console = Console()

    console.print("Loading the knowledge base...", style="bold cyan")
    store = VectorStore()
    store.load()

    chat = GroqChatSession(model=args.model)
    transcription = FileTranscription()
    session_storage = SessionStorage()
    text_to_speech = TextToSpeech() if args.voice else None
    command_names = CommandsName()

    tools = Tools(
        store=store,
        get_messages=chat.get_messages,
        summarize=chat.summarize_messages,
    )
    chat.set_tools(tools)

    commands = Commands(
        store=store,
        transcription=transcription,
    )

    console.print(
        Panel(
            f"Enter '{command_names.COMMAND_EXIT[0]}' to leave.",
            title="Knowledge-base chat is ready",
            border_style="cyan",
        )
    )

    while True:
        try:
            user_query = console.input("[bold blue]> You: [/bold blue]").strip()

            if not user_query:
                continue

            normalized_query = user_query.lower()
            command, _, argument = user_query.partition(" ")
            normalized_command = command.lower()

            if normalized_query in command_names.COMMAND_EXIT:
                response = "Goodbye!"
                console.print("Assistant:", style="bold green", end=" ")
                console.print(response, markup=False)
                log_interactions(query=user_query, response=response)
                break

            if normalized_query == command_names.COMMAND_UPDATE_TEXT:
                result = commands.update_text()
                console.print("Assistant:", style="bold green", end=" ")
                console.print(result, markup=False)
                log_interactions(query=user_query, response=result)
                continue

            if normalized_query == command_names.COMMAND_UPDATE_VOICE:
                result = commands.update_voice()
                console.print("Assistant:", style="bold green", end=" ")
                console.print(result, markup=False)
                log_interactions(query=user_query, response=result)
                continue

            if normalized_query == command_names.COMMAND_LOAD_SESSION:
                chat.load_session(session_storage)
                response = "Session loaded successfully."
                console.print("Assistant:", style="bold green", end=" ")
                console.print(response, markup=False)
                log_interactions(query=user_query, response=response)
                continue

            if normalized_query == command_names.COMMAND_SAVE_SESSION:
                path = chat.save_session(session_storage)
                response = f"Session saved to {path}"
                console.print("Assistant:", style="bold green", end=" ")
                console.print(response, markup=False)
                log_interactions(query=user_query, response=response)
                continue

            if normalized_command == command_names.COMMAND_CHANGE_PROMPT:
                prompt_source = argument.strip()
                if not prompt_source:
                    console.print(
                        "Enter the new system prompt:",
                        style="bold green",
                    )
                    prompt_source = console.input(
                        "[bold blue]> User: [/bold blue]"
                    ).strip()

                chat.change_prompt(prompt_source)
                response = "System prompt updated successfully."
                console.print("Assistant:", style="bold green", end=" ")
                console.print(response, markup=False)
                log_interactions(query=user_query, response=response)
                continue

            console.print("Assistant:", style="bold green", end=" ")
            response = chat.ask(
                user_query,
                on_token=lambda token: console.print(
                    token,
                    end="",
                    markup=False,
                    highlight=False,
                ),
            )
            console.print()
            log_interactions(query=user_query, response=response)

            if text_to_speech is not None:
                text_to_speech.speak(response)

        except KeyboardInterrupt:
            console.print(
                "Assistant: Session interrupted. Goodbye!",
                style="bold yellow",
            )
            break
        except Exception as error:
            console.print(
                f"Assistant: An error occurred: {error}",
                style="bold red",
            )


if __name__ == "__main__":
    main()
