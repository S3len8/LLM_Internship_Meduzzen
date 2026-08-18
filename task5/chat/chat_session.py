import json
from collections.abc import Callable
from pathlib import Path
from typing import Any
from groq import Groq
from config.constants import (
    CHAT_MODEL_NAME,
)
from config.prompts import (
    DEFAULT_SYSTEM_PROMPT_RESPONSE,
    DEFAULT_SYSTEM_PROMPT_SUMMARY,
)
from chat.tools_schema import TOOLS


TokenCallback = Callable[[str], None]


class GroqChatSession:
    def __init__(self, client: Groq, model: str | None = None) -> None:
        self.client = client
        self.model = model or CHAT_MODEL_NAME
        self.tools = None
        self.messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": DEFAULT_SYSTEM_PROMPT_RESPONSE,
            }
        ]

    def set_tools(self, tools: Any) -> None:
        self.tools = tools

    def change_prompt(self, prompt_source: str) -> str:
        prompt_source = prompt_source.strip()

        if not prompt_source:
            raise ValueError("System prompt cannot be empty.")

        prompt_path = Path(prompt_source)

        if prompt_path.is_file():
            prompt = prompt_path.read_text(encoding="utf-8").strip()
        else:
            prompt = prompt_source

        if not prompt:
            raise ValueError("System prompt cannot be empty.")

        self.system_prompt = prompt

        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0]["content"] = prompt
        else:
            self.messages.insert(
                0,
                {
                    "role": "system",
                    "content": prompt,
                },
            )

        return prompt

    def get_messages(self) -> list[dict[str, Any]]:
        return list(self.messages)

    def ask(
        self,
        user_query: str,
        on_token: TokenCallback | None = None,
    ) -> str:
        self.messages.append({
            "role": "user",
            "content": user_query,
        })

        while True:
            stream = self._call_ai(stream=True)
            content, tool_calls = self._consume_stream(
                stream=stream,
                on_token=on_token,
            )

            if not tool_calls:
                self.messages.append({
                    "role": "assistant",
                    "content": content,
                })
                return content

            self.messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": [
                    tool_call
                    for tool_call in tool_calls
                ],
            })

            for tool_call in tool_calls:
                if self.tools is None:
                    raise RuntimeError("Tools are not configured.")

                arguments = json.loads(
                    tool_call["function"]["arguments"]
                )
                result = self.tools.execute(
                    name=tool_call["function"]["name"],
                    arguments=arguments,
                )

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result,
                })

    def _call_ai(self, stream: bool = False) -> Any:
        return self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=stream,
        )

    def _consume_stream(
        self,
        stream: Any,
        on_token: TokenCallback | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        content_parts: list[str] = []
        tool_calls: dict[int, dict[str, Any]] = {}

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            content = getattr(delta, "content", None)

            if content:
                content_parts.append(content)
                if on_token is not None:
                    on_token(content)

            for tool_fragment in getattr(delta, "tool_calls", None) or []:
                index = tool_fragment.index
                tool_call = tool_calls.setdefault(
                    index,
                    {
                        "id": "",
                        "type": "function",
                        "function": {
                            "name": "",
                            "arguments": "",
                        },
                    },
                )

                if tool_fragment.id:
                    tool_call["id"] = tool_fragment.id

                if tool_fragment.type:
                    tool_call["type"] = tool_fragment.type

                function = tool_fragment.function
                if function is not None:
                    if function.name:
                        tool_call["function"]["name"] += function.name
                    if function.arguments:
                        tool_call["function"]["arguments"] += function.arguments

        ordered_tool_calls = [
            tool_calls[index]
            for index in sorted(tool_calls) # Restore the original order of tool calls from their streaming indexes.
        ]
        return "".join(content_parts), ordered_tool_calls

    def summarize_messages(self, messages: list[dict[str, Any]]) -> str:
        conversation = "\n".join(
            f"{message['role']}: {message.get('content') or ''}"
            for message in messages
            if message.get("role") != "system"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT_SUMMARY,
                },
                {
                    "role": "user",
                    "content": conversation,
                },
            ],
        )
        return response.choices[0].message.content 

    def save_session(self, storage) -> str:
        return storage.save(
            messages=self.messages
        )

    def load_session(self, storage) -> None:
        self.messages = storage.load()
