import wikipedia


def calculate(expr: str) -> int | float:
    return eval(expr)


def explain(topic: str) -> str:
    return f"Explanation for the topic: {topic}"


def search_wikipedia(query: str) -> str:
    try:
        wikipedia.set_user_agent("EducationalBot/1.0 (contact@example.com)")
        wikipedia.set_lang("en")

        search_results = wikipedia.search(query)
        result = wikipedia.summary(search_results[0], sentences=2)
        return result

    except wikipedia.exceptions.DisambiguationError:
        return (
            "Multiple pages were found for this query. "
            "Please refine your query."
        )
    except wikipedia.exceptions.PageError:
        return "The Wikipedia page was not found."
    except Exception as error:
        return f"An error occurred while searching Wikipedia: {error}"
