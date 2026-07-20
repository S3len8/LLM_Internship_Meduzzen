# Multi-Turn Groq CLI Chat
A CLI tutor chatbot with streaming, multi-turn history, token tracking, custom prompts, error handling, and Markdown logs.
## Setup
Install dependencies: `python -m pip install -r task1/requirements.txt`
Create a Groq API key in the [Groq Console](https://console.groq.com/keys).
Add it to `.env`: `GROQ_API_KEY=your_groq_api_key`
Run the app: `python task1/app.py`
## Options
Custom prompt: `python task1/app.py --prompt "You are a patient math tutor."`
Custom model: `python task1/app.py --model llama-3.1-8b-instant`
The default model is `llama-3.3-70b-versatile`; use `q`, `quit`, `exit`, or `Ctrl+C` to stop.
## How It Works
`ChatSession` stores `system`, `user`, and `assistant` messages and sends the full current history to Groq.
Responses are printed chunk by chunk with `stream=True` and saved after completion.
Token counts come from Groq streaming metadata and are tracked per request and session.
Logs with timestamps and token statistics are saved in `task1/logs/`; see `example_conversation.md`.
## Examples
`Explain overfitting simply.` | `Quiz me on Python.` | `Compare supervised and unsupervised learning.` | `Summarize: ...`
## Documentation
[Quickstart](https://console.groq.com/docs/quickstart) | [Streaming](https://console.groq.com/docs/text-chat) | [API Reference](https://console.groq.com/docs/api-reference) | [Models](https://console.groq.com/docs/models)
