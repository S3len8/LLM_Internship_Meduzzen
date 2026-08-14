from collections.abc import Callable
from typing import Any

from knowledge_base.vector import VectorStore


class Tools:
    """Local Python implementations of the tools exposed to GPT."""

    def __init__(
        self,
        store: VectorStore,
        get_messages: Callable[[], list[dict[str, Any]]],
        summarize: Callable[[list[dict[str, Any]]], str],
    ) -> None:
        self.store = store
        self.get_messages = get_messages
        self.summarize = summarize

        self.functions = {
            "semantic_search": self.semantic_search,
            "summarize_session": self.summarize_session,
        }

    def execute(self, name: str, arguments: dict[str, Any]) -> str:
        function = self.functions.get(name)
        if function is None:
            raise ValueError(f"Unknown tool: {name}")

        result = function(**arguments)
        return str(result)

    def semantic_search(self, query: str) -> str:
        results = self.store.search(query=query)

        if not results:
            return "No relevant information was found in the knowledge base."

        return "\n\n".join(
            f"[Source: {(result.document.metadata or {}).get('source', 'Unknown')}]\n"
            f"{result.document.text}"
            for result in results
        )

    def summarize_session(self) -> str:
        return self.summarize(self.get_messages())
