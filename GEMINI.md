# AIDA - AI Diagnostic Agent

## Overview
AIDA is a local, privacy-focused emergency diagnostic agent. It leverages `osquery` to inspect system state and uses a local RAG (Retrieval-Augmented Generation) system to understand osquery's extensive schema. The agent can be interacted with via a web interface or used programmatically.

## Architecture
*   **Agent Framework**: Built using `google.adk`.
*   **LLM**: Uses a local **Qwen 2.5** model hosted via **Ollama** (`ollama_chat/qwen2.5`), chosen for its reliable tool-calling capabilities.
*   **RAG System**: A purely local implementation using **SQLite** via the **`sqlite-rag`** library.
    *   **Embeddings**: Generated in-database using `sqlite-ai` and the `embeddinggemma-300m` GGUF model, managed by `sqlite-rag`.
    *   **Search**: Hybrid search (Vector + FTS5) performed using `sqlite-rag` (leveraging `sqlite-vec` and `fts5`).
    *   **Data Source**: Official `osquery` `.table` specification files.
*   **Web Interface**: A **FastAPI** application serving a simple HTML/JS chat UI.

## Key Files
*   **`setup.sh`**: Automates the entire environment setup (dependencies, data fetching, model download/pull, ingestion).
*   **`cleanup.sh`**: Removes generated data, models, and the database to reset the environment.
*   **`main.py`**: The FastAPI entry point. Sets up the web server, static assets, and the chat endpoint.
*   **`aida/agent.py`**: Defines the `root_agent`, its persona, and tools (`run_osquery`, `schema_discovery`).
*   **`aida/osquery_rag.py`**: Implements the RAG logic using `sqlite-rag`.
*   **`ingest_osquery.py`**: Script to ingest osquery `.table` files into the RAG database using `sqlite-rag`.
*   **`osquery.db`**: The SQLite database containing the ingested schema data and vectors.

## Setup & Running

### Prerequisites
*   Python 3.12+
*   **Ollama** running locally.
*   `osquery` installed on the host system.

### Automated Setup
Run the included script to prepare the environment:
```bash
./setup.sh
```
This script will:
1.  Install Python dependencies from `requirements.txt`.
2.  Clone the `osquery` repository (sparse checkout of `specs`).
3.  Download the `embeddinggemma-300m` model.
4.  Pull the `qwen2.5` model via Ollama.
5.  Run `ingest_osquery.py` to build the knowledge base.

### Running the Agent
Start the web interface:
```bash
uvicorn main:app --reload
```
Access the UI at `http://127.0.0.1:8000`.

### Cleanup
To reset the project to its initial state:
```bash
./cleanup.sh
```

## Development Conventions
*   **Tool Use**: The agent uses a manual tool invocation pattern (wrapping calls in ` ```tool_code ``` ` blocks) as defined in `aida/agent.py`.
*   **Database**: Uses **`sqlite-rag`** for RAG operations.
*   **Local-First**: All components are local. Avoid adding external API dependencies.
*   **Linting**: Use `ruff check .` and `ruff format .` to maintain code quality.
