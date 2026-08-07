TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Обчислює математичний вираз і повертає числовий результат. "
                "Використовуй для будь-яких математичних обчислень."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expr": {
                        "type": "string",
                        "description": (
                            "Математичний вираз для обчислення, наприклад: "
                            "'5 * (2 + 3)' або '100 / 4'"
                        ),
                    }
                },
                "required": ["expr"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain",
            "description": (
                "Надає коротке пояснення навчальної теми чи терміну."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "Назва теми або концепту для пояснення, "
                            "наприклад: "
                            "'photosynthesis' або 'gravity'"
                        ),
                    }
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": (
                "Пошук інформації, фактів або історичних даних у Вікіпедії."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Пошуковий запит або тема для пошуку у Вікіпедії "
                            "(наприклад, 'Albert Einstein' або 'Київ')."
                        ),
                    }
                },
                "required": ["query"],
            },
        },
    },
]
