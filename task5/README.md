# Task 5 - CLI AI Assistant

A modular command-line assistant with memory, semantic search, text and audio
input, streaming responses, and optional voice output.

## Implemented

 - Groq chat session with conversation history stored in `messages`.
 - Streaming assistant responses token by token.
 - FAISS vector knowledge base with local sentence embeddings.
 - Text knowledge updates through `/update_kb_text`.
 - Audio transcription for `.mp3`, `.wav`, and `.m4a` through `/update_kb_voice`.
 - Automatic GPT tool calling:
   - `semantic_search` searches the knowledge base.
   - `summarize_session` summarizes the current conversation.
 - Session persistence with `/save_session` and `/load_session`.
 - Runtime system prompt changes with `/change_prompt`.
 - Model selection with the `--model` CLI option.
 - Optional Windows text-to-speech with the `--voice` option.
 - Logging of user queries, assistant responses, and CLI commands.

## Configuration

Create a `.env` file in the project root with the API key, chat model,
embedding model, and FAISS file names.

## Run

 Start the application from the `task5` directory:

 ```bash
 python app.py
 ```

 Use a custom chat model or enable voice output:

 ```bash
 python app.py --model <model-name> --voice
 ```

## CLI Commands

 ```text
 /update_kb_text       Add typed knowledge to the vector store
 /update_kb_voice      Transcribe and add an audio file to the vector store
 /save_session         Save the current conversation
 /load_session         Load the saved conversation
 /change_prompt ...    Change the system prompt or load it from a file
 /exit                 End the session
 ```

## Storage

Runtime files are stored in the `data` directory and the task root:

- `data/audio_files` - input audio files
- `data/logs` - interaction logs
- `data/sessions` - saved conversations
- `faiss_index.bin` and `metadata.pkl` - vector knowledge base files
