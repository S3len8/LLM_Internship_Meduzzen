import os
from groq import Groq
from groq.types.chat import ChatCompletion
from dotenv import load_dotenv
from constants import CHAT_MODEL_NAME, DEFAULT_SYSTEM_PROMPT
from schemas import SearchResult

load_dotenv()


class GroqChatSession:
    api_key: str
    client: Groq
    model: str
    default_prompt: str

    def __init__(self) -> None:
        api_key = os.getenv("API_KEY")

        if not api_key:
            raise ValueError("API_KEY is not set. Add it to the .env file.")

        self.api_key = api_key
        self.client = Groq(api_key=self.api_key)
        self.model = CHAT_MODEL_NAME
        self.default_prompt = DEFAULT_SYSTEM_PROMPT

    def _build_prompt(
        self,
        query: str,
        context_documents: list[SearchResult],
    ) -> list[dict[str, str]]:
        formatted_docs: list[str] = []
        for doc in context_documents:
            metadata = doc["document"]["metadata"] or {}
            source = metadata.get("source", "Невідомо")
            text = doc["document"]["text"]
            formatted_docs.append(f"[Source: {source}]\n{text}")

        context_text = "\n\n".join(formatted_docs)

        system_content = f"{self.default_prompt}Knowledge base context:\n{context_text}"

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query},
        ]

    def _call_ai(self, messages: list[dict[str, str]]) -> ChatCompletion:
        return self.client.chat.completions.create(model=self.model, messages=messages)

    def get_response(self, query: str, context_documents: list[SearchResult]) -> str:
        messages = self._build_prompt(query=query, context_documents=context_documents)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content or ""
