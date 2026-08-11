import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROMPT = (
    "You are a helpful educational assistant. When the user asks to calculate "
    "math, explain a topic, or search information, you MUST use the provided "
    "tools. Respond in Ukrainian."
)
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")
