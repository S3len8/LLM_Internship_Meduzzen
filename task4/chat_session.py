from groq import Groq
from groq.types.chat import ChatCompletion
from constants import constants
from schemas import SearchResult, SummaryInput


class GroqChatSession:
    def __init__(self) -> None:
        self.api_key = constants.API_KEY

        if not self.api_key:
            raise ValueError("API_KEY is not set. Add it to the .env file.")

        self.client = Groq(api_key=self.api_key)
        self.model = constants.CHAT_MODEL_NAME
        self.default_prompt_get_response = constants.DEFAULT_SYSTEM_PROMPT_RESPONSE
        self.default_prompt_summary = constants.DEFAULT_SYSTEM_PROMPT_SUMMARY

    def _build_prompt_get_response(
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

        system_content = f"{self.default_prompt_get_response}Knowledge base context:\n{context_text}"

        if not matches:
            return [
                {"role": "system", "content": self.default_prompt_get_response},
                {"role": "user", "content": query},
            ]

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query},
        ]

    def _build_prompt_summary(self, summary: str) -> list[dict[str, str]]:
        summary_input = SummaryInput(text=summary)

        return [
            {"role": "system", "content": self.default_prompt_summary},
            {"role": "user", "content": summary_input.text},
        ]

    def _call_ai(self, messages: list[dict[str, str]]) -> ChatCompletion:
        return self.client.chat.completions.create(model=self.model, messages=messages)

    def get_response(self, query: str, matches: list[SearchResult]) -> str:
        messages = self._build_prompt_get_response(query=query, matches=matches)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content or ""

    def summary(self, summary: str) -> str:
        messages = self._build_prompt_summary(summary=summary)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content or ""
