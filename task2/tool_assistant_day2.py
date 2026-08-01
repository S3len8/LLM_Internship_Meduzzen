import datetime
import json
import os
from typing import Any
from dotenv import load_dotenv
from groq import Groq
from constants import DEFAULT_PROMPT
from functions import calculate, explain, search_wikipedia
from schemas import TOOLS

load_dotenv()


class ChatSession:
    def __init__(self, system_prompt=None) -> None:
        self.API_KEY = os.getenv("API_KEY")

        if not self.API_KEY:
            raise ValueError(
                "API_KEY is not set. Add it to the .env file."
            )

        self.client = Groq(api_key=self.API_KEY)
        self.model = "llama-3.1-8b-instant"

        if system_prompt:
            selected_prompt = (
                f"{DEFAULT_PROMPT}\n\nYour persona/style: {system_prompt}"
            )
        else:
            selected_prompt = DEFAULT_PROMPT

        self.messages = [
            {
                "role": "system",
                "content": selected_prompt,
            }
        ]

        self.tools = TOOLS

        self.tools_map = {
            "calculate": calculate,
            "explain": explain,
            "search_wikipedia": search_wikipedia,
        }

    def send_message(self) -> bool:
        user_message = input("You: ")
        clean_message = user_message.strip().lower()

        if clean_message in ["exit", "quit"]:
            print("Goodbye!")
            return False

        turn_start = len(self.messages)
        self.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message
            self.messages.append(assistant_message)

            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    if function_name in self.tools_map:
                        result = self.tools_map[function_name](**function_args)
                        self.log_tool_calls(
                            function_name=function_name,
                            function_args=function_args,
                            result=result,
                        )
                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": str(result),
                            }
                        )

                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                )
                final_message = second_response.choices[0].message
                print(f"Assistant: {final_message.content}")
                self.messages.append(final_message)
                return True

            print(f"Assistant: {assistant_message.content}")
            return True

        except (Exception, KeyboardInterrupt) as error:
            del self.messages[turn_start:]
            print(f"Error while processing your message: {error}")
            return True

    def log_tool_calls(
        self,
        function_name: str,
        function_args: dict[str, Any],
        result: Any,
    ) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        str_args = json.dumps(function_args, ensure_ascii=False)
        str_result = str(result)

        log_entry = (
            f"TimeStamp: {timestamp}, Function: {function_name}, "
            f"Args: {str_args}, Result: {str_result}\n"
        )

        current_dir = os.path.dirname(os.path.abspath(__file__))

        log_path = os.path.join(current_dir, "logs", "logs_tool_calls.md")

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def run_cli(self) -> None:
        is_running = True
        while is_running:
            is_running = self.send_message()
