from groq import Groq
from groq.types.chat import ChatCompletion
from constants import (
    CHAT_MODEL_NAME
)
from prompts import (
    DEFAULT_SYSTEM_PROMPT_RESPONSE,
    DEFAULT_SYSTEM_PROMPT_SUMMARY,
)
from schemas import SearchResult, SummaryInput


class GroqChatSession:
    def __init__(self, client: Groq) -> None:
        self.client = client
        self.model = CHAT_MODEL_NAME

    def _build_response_messages(
        self,
        query: str,
        matches: list[SearchResult],
    ) -> list[dict[str, str]]:
        formatted_docs: list[str] = []
        for doc in matches:
            metadata = doc.document.metadata or {}
            source = metadata.get("source", "Unknown")
            text = doc.document.text
            formatted_docs.append(f"[Source: {source}]\n{text}")

        context_text = "\n\n".join(formatted_docs)

        system_content = f"{DEFAULT_SYSTEM_PROMPT_RESPONSE}Knowledge base context:\n{context_text}"

        if not matches:
            return [
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT_RESPONSE},
                {"role": "user", "content": query},
            ]

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query},
        ]

    def _build_summary_messages(self, summary: str) -> list[dict[str, str]]:
        summary_input = SummaryInput(text=summary)

        return [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT_SUMMARY},
            {"role": "user", "content": summary_input.text},
        ]

    def _call_ai(self, messages: list[dict[str, str]]) -> ChatCompletion:
        return self.client.chat.completions.create(model=self.model, messages=messages)

    def get_response(self, query: str, matches: list[SearchResult]) -> str:
        messages = self._build_response_messages(query=query, matches=matches)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content or ""

    def summary(self, summary: str) -> str:
        messages = self._build_summary_messages(summary=summary)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content or ""
