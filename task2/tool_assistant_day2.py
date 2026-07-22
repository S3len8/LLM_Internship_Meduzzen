import json
import os
import wikipedia
from groq import Groq
from dotenv import load_dotenv
import datetime
import argparse


load_dotenv()


class ChatSession:
    def __init__(self, system_prompt = None):

        self.API_KEY = os.getenv("API_KEY")
        self.client = Groq(api_key=self.API_KEY)
        self.model = "llama-3.1-8b-instant"

        default_prompt = "You are a helpful educational assistant. When the user asks to calculate math, explain a topic, or search information, you MUST use the provided tools. Respond in Ukrainian."

        if system_prompt:
            selected_prompt = f"{default_prompt}\n\nYour persona/style: {system_prompt}"
        else:
            selected_prompt = default_prompt

        self.messages = [{
            "role": "system",
            "content": selected_prompt,
        }]

        self.tools = [{
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Обчислює математичний вираз і повертає числовий результат. Використовуй для будь-яких математичних обчислень.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expr": {
                            "type": "string",
                            "description": "Математичний вираз для обчислення, наприклад: '5 * (2 + 3)' або '100 / 4'"
                        }
                    },
                    "required": ["expr"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "explain",
                "description": "Надає коротке пояснення навчальної теми чи терміну.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Назва теми або концепту для пояснення, наприклад: 'photosynthesis' або 'gravity'"
                        }
                    },
                    "required": ["topic"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_wikipedia",
                "description": "Пошук інформації, фактів або історичних даних у Вікіпедії.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Пошуковий запит або тема для пошуку у Вікіпедії (наприклад, 'Albert Einstein' або 'Київ')."
                        }
                    },
                    "required": ["query"]
                }
            }
        }]

    def calculate(self, expr: str):
        return eval(expr)

    def explain(self, topic: str):
        return f"Пояснення для теми: {topic}"

    def search_wikipedia(self, query: str):
        try:
            wikipedia.set_user_agent("EducationalBot/1.0 (contact@example.com)")
            wikipedia.set_lang("en")

            search_results = wikipedia.search(query)
            result = wikipedia.summary(search_results[0], sentences=2)
            return result

        except wikipedia.exceptions.DisambiguationError:
            return f"Знайдено декілька сторінок за цим запитом. Будь ласка, уточніть запит."
        except wikipedia.exceptions.PageError:
            return f"Сторінку у Вікіпедії не знайдено."
        except Exception as e:
            return f"Помилка під час пошуку у Вікіпедії: {str(e)}"


    def send_message(self):
        user_message = input("You: ")
        clean_message = user_message.strip().lower()

        if  clean_message in ["exit", "quit"]:
            print(f"Goodbye!")
            return False

        self.messages.append({
            "role": "user",
            "content": user_message,
        })

        response = self.client.chat.completions.create(model=self.model, messages=self.messages, tools=self.tools, tool_choice="auto")
        assistant_message = response.choices[0].message
        self.messages.append(assistant_message)

        if assistant_message.tool_calls:

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "calculate":
                    result = self.calculate(expr=function_args.get("expr"))
                    self.log_tool_calls(function_name=function_name, function_args=function_args, result=result)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })

                if function_name == "explain":
                    result = self.explain(topic=function_args.get("topic"))
                    self.log_tool_calls(function_name=function_name, function_args=function_args, result=result)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })

                if function_name == "search_wikipedia":
                    result = self.search_wikipedia(query=function_args.get("query"))
                    self.log_tool_calls(function_name=function_name, function_args=function_args, result=result)
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })

            second_response = self.client.chat.completions.create(model=self.model,messages=self.messages)
            final_message = second_response.choices[0].message
            print(f"Assistant: {final_message.content}")
            self.messages.append(final_message)
            return True

        else:
            print(f"{assistant_message.content}")
            return True

    def log_tool_calls(self, function_name, function_args, result):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        str_result = str(result)

        log_entry = f"TimeStamp: {timestamp}, Function: {function_name}, Args: {function_args}, Result: {str_result}\n"

        with open("task2/logs/logs_tool_calls.md", "a", encoding="utf-8") as f:
            f.write(log_entry)

    def run_cli(self):
        is_running = True
        while is_running:
            is_running = self.send_message()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Educational Assistant with Tool Support")

    parser.add_argument(
        "-p", "--persona",
        type=str,
        help="Вкажіть системний промпт / персону для бота (наприклад: 'Ти суворий професор')"
    )

    args = parser.parse_args()

    bot = ChatSession(system_prompt=args.persona)
    bot.run_cli()