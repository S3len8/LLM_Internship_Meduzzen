# Audio Transcription & RAG Search

This project extends the Task 3 RAG application with audio-file processing. The application accepts an audio file through the CLI using the `file:` command. Before processing, it validates the file name, supported extension, and file location.

## Model note

The transcription is implemented with Groq's `whisper-large-v3` model. The task requirements mention OpenAI's `whisper-1` model, so using Groq Whisper is a formal deviation from the specification. Functionally, the required transcription workflow is implemented, but the transcription is performed through the Groq API.

## Implemented workflow

1. Place a supported audio file in the `audio_files` directory.
2. Enter `file: filename.mp3` in the CLI.
3. Display the complete transcript and generate a summary with a Groq chat model.
4. Split the transcript into chunks and store them in FAISS with source metadata.
5. Ask text-based questions and retrieve relevant transcript chunks through FAISS similarity search.
