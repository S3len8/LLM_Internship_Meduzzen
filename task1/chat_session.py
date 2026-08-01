"""Core logic for a multi-turn Groq chat session."""
from __future__ import annotations
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator
from dotenv import load_dotenv
from groq import Groq
from constants import DEFAULT_SYSTEM_PROMPT, MODEL 


class ChatConfigurationError(RuntimeError):
    """Raised when the chat session cannot be configured."""


class ChatSession:
    """Manage message history, streaming responses, tokens, and chat logs."""
    def __init__(
        self,
        model: str = MODEL,
        system_prompt: str | None = None,
        *,
        api_key: str | None = None,
        log_dir: str | Path | None = None,
    ) -> None:
        """Create a chat session and initialize its persistent log."""
        load_dotenv()

        resolved_api_key = (
            api_key
            if api_key is not None
            else os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
        )
        if not resolved_api_key:
            raise ChatConfigurationError(
                "GROQ_API_KEY is missing. Add it to a .env file before starting the app."
            )

        self.client = Groq(api_key=resolved_api_key, timeout=30.0, max_retries=2)
        self.model = model
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self.started_at = datetime.now().astimezone()

        self.messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.log_entries: list[dict[str, Any]] = []
        self.last_usage = self._empty_usage()
        self.total_usage = self._empty_usage()

        self.log_dir = Path(log_dir) if log_dir else Path(__file__).parent / "logs"
        filename_time = self.started_at.strftime("%Y-%m-%d_%H-%M-%S-%f")
        self.log_path = self.log_dir / f"conversation_{filename_time}.md"

    @staticmethod
    def _empty_usage() -> dict[str, int]:
        """Return a new zeroed token-usage dictionary."""
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    @staticmethod
    def _timestamp() -> str:
        """Return a timezone-aware timestamp for a log entry."""
        return datetime.now().astimezone().isoformat(timespec="seconds")

    def add_message(self, role: str, content: str) -> None:
        """Add a validated user or assistant message to API history."""
        if role not in {"user", "assistant"}:
            raise ValueError("Message role must be 'user' or 'assistant'.")
        if not content.strip():
            raise ValueError("Message content cannot be empty.")
        self.messages.append({"role": role, "content": content})

    def get_response(self, user_input: str) -> Iterator[str]:
        """Yield assistant text chunks while preserving the completed turn.

        Token usage is supplied by the final streaming chunk. A completed turn
        is added to API history and saved to Markdown. If streaming fails, the
        partial text is logged but is not added to future model context.
        """
        cleaned_input = user_input.strip()
        if not cleaned_input:
            raise ValueError("Message cannot be empty.")

        self.last_usage = self._empty_usage()
        self.add_message("user", cleaned_input)
        user_log = {
            "role": "user",
            "content": cleaned_input,
            "timestamp": self._timestamp(),
            "status": "complete",
        }
        self.log_entries.append(user_log)

        response_parts: list[str] = []
        usage = self._empty_usage()

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                stream=True,
            )

            for chunk in stream:
                chunk_usage = chunk.usage
                if chunk_usage is None and chunk.x_groq is not None:
                    chunk_usage = chunk.x_groq.usage

                if chunk_usage is not None:
                    usage = {
                        "input_tokens": chunk_usage.prompt_tokens,
                        "output_tokens": chunk_usage.completion_tokens,
                        "total_tokens": chunk_usage.total_tokens,
                    }

                if not chunk.choices:
                    continue

                text = chunk.choices[0].delta.content
                if text:
                    response_parts.append(text)
                    yield text

            assistant_text = "".join(response_parts).strip()
            if not assistant_text:
                raise RuntimeError("The Groq API returned no assistant text.")
        except (Exception, KeyboardInterrupt):
            self._remove_unanswered_user_message()
            user_log["status"] = "failed"

            partial_text = "".join(response_parts).strip()
            if partial_text:
                self.log_entries.append(
                    {
                        "role": "assistant",
                        "content": partial_text,
                        "timestamp": self._timestamp(),
                        "status": "incomplete",
                    }
                )
            self.save_log()
            raise

        self.add_message("assistant", assistant_text)
        self.last_usage = usage
        for key, value in usage.items():
            self.total_usage[key] += value

        self.log_entries.append(
            {
                "role": "assistant",
                "content": assistant_text,
                "timestamp": self._timestamp(),
                "status": "complete",
                "usage": usage.copy(),
            }
        )
        self.save_log()

    def _remove_unanswered_user_message(self) -> None:
        """Remove a failed turn from the context sent on the next request."""
        if self.messages and self.messages[-1]["role"] == "user":
            self.messages.pop()

    def save_log(self) -> Path:
        """Persist the complete session as a human-readable Markdown file."""
        self.log_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            "# Conversation Log",
            "",
            f"- Started: {self.started_at.isoformat(timespec='seconds')}",
            f"- Model: `{self.model}`",
            "- Token method: Groq response metadata",
            "",
            "## System Prompt",
            "",
            self.system_prompt,
            "",
        ]

        for entry in self.log_entries:
            role_name = "User" if entry["role"] == "user" else "Assistant"
            lines.extend(
                [
                    f"## {role_name} — {entry['timestamp']}",
                    "",
                ]
            )
            if entry.get("status") != "complete":
                lines.extend([f"Status: **{entry['status']}**", ""])
            lines.extend([entry["content"], ""])

            usage = entry.get("usage")
            if usage:
                lines.extend(
                    [
                        (
                            "Tokens — input: "
                            f"{usage['input_tokens']}, output: {usage['output_tokens']}, "
                            f"total: {usage['total_tokens']}"
                        ),
                        "",
                    ]
                )

        lines.extend(
            [
                "## Session Summary",
                "",
                f"- Input tokens: {self.total_usage['input_tokens']}",
                f"- Output tokens: {self.total_usage['output_tokens']}",
                f"- Total tokens: {self.total_usage['total_tokens']}",
                "",
            ]
        )

        self.log_path.write_text("\n".join(lines), encoding="utf-8")
        return self.log_path

    def get_summary(self) -> dict[str, int]:
        """Return token totals and the number of completed assistant turns."""
        completed_turns = sum(
            entry["role"] == "assistant" and entry.get("status") == "complete"
            for entry in self.log_entries
        )
        return {"completed_turns": completed_turns, **self.total_usage}