TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "semantic_search",
            "description": (
                "Search the user's vector knowledge base when the user asks "
                "for stored knowledge. Do not call this tool for greetings, "
                "thanks, casual conversation, or unrelated requests."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search question"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_session",
            "description": (
                "Summarize the current chat session only when the user "
                "explicitly asks for a session or conversation summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
]
