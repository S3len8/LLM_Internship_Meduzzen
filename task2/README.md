# Task 2: AI Educational Assistant with Function Calling & CLI Support
An interactive CLI-based educational chatbot built with **Python**, **Groq SDK** (`llama-3.1-8b-instant`), and native **Function Calling / Tool Use**. 

## Overview
This project implements an AI assistant capable of dynamically calling local Python functions to execute math calculations, fetch educational topic overviews, and perform real-time Wikipedia searches.

## Features & What Was Completed
### 1. Core Tool Integration (Function Calling)
Implemented an interactive CLI chat loop inside the `ChatSession` class supporting automatic function execution:
* **`calculate(expr)`**: Evaluates mathematical expressions safely using Python.
* **`explain(topic)`**: Provides structured educational explanations for scientific and general concepts.
* **`search_wikipedia(query)`**: Fetches factual summaries from Wikipedia with query normalization and robust API error handling.

### 2. Execution Logging (`logs/`)
* Automatically creates a `logs/` directory and logs every tool execution into `logs_tool_calls.md`.
* Each log entry records: **Timestamp**, **Function Name**, **Arguments**, and **Output/Errors**.

### 3. Dynamic Persona / System Prompt (`argparse`)
* Added CLI argument parsing via `argparse` to customize the assistant's persona dynamically upon launch.
* Usage example:
  ```bash
  python task2/tool_assistant_day2.py --persona "You are a friendly pirate explaining science with 'Yo-ho-ho!'" 
  
### All samples for this task are placed in the file `Sample_run.md`.
