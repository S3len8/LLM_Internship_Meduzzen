from groq import Groq
from groq.types.chat import ChatCompletion
from constants import constants
from schemas import QueryInput, SearchResult


class GroqChatSession:
    def __init__(self) -> None:
        self.api_key = constants.API_KEY

        if not self.api_key:
            raise ValueError("API_KEY is not set. Add it to the .env file.")

        self.client = Groq(api_key=self.api_key)
        self.model = constants.CHAT_MODEL_NAME
        self.default_prompt = constants.DEFAULT_SYSTEM_PROMPT

    def _build_prompt(
        self,
        query: str,
        context_documents: list[SearchResult],
    ) -> list[dict[str, str]]:
        validated_query = QueryInput(query=query).query
        formatted_docs: list[str] = []
        for doc in context_documents:
            metadata = doc.document.metadata or {}
            source = metadata.get("source", "Unknown")
            text = doc.document.text
            formatted_docs.append(f"[Source: {source}]\n{text}")

        context_text = "\n\n".join(formatted_docs)

        system_content = f"{self.default_prompt}Knowledge base context:\n{context_text}"

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": validated_query},
        ]

    def _call_ai(self, messages: list[dict[str, str]]) -> ChatCompletion:
        return self.client.chat.completions.create(model=self.model, messages=messages)

    def get_response(self, query: str, context_documents: list[SearchResult]) -> str:
        messages = self._build_prompt(query=query, context_documents=context_documents)

        ai_response = self._call_ai(messages=messages)

        return ai_response.choices[0].message.content or ""
