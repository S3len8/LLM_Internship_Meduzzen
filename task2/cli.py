import argparse
from tool_assistant_day2 import ChatSession


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI Educational Assistant with Tool Support"
    )

    parser.add_argument(
        "-p",
        "--persona",
        type=str,
        help=(
            "Вкажіть системний промпт / персону для бота "
            "(наприклад: 'Ти суворий професор')"
        ),
    )

    args = parser.parse_args()

    bot = ChatSession(system_prompt=args.persona)
    bot.run_cli()
