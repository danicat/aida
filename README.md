# AIDA - AI Diagnostic Agent

AIDA (pronounced "ei-da") is an AI Diagnostic Agent designed to perform operating system health checks and diagnostics. It leverages the power of [osquery](https://osquery.io/) to inspect system state in a structured, SQL-like manner.

AIDA is grounded by a local Retrieval-Augmented Generation (RAG) system. It looks up table names in its built-in copy of the official osquery schema documentation before executing any queries.

## Architecture & RAG

AIDA runs entirely locally for maximum privacy:
*   **Agent Brain**: Powered by **Gemma 3 27B** (via Ollama).
*   **Tooling**: It can execute real read-only queries on your host system using `osqueryi`.
*   **RAG Knowledge Base**: A purely local SQLite database containing all osquery table specifications.
    *   **Embeddings**: Generated in-database using `sqlite-ai` and the `embeddinggemma-300m` model.
    *   **Search**: Performed using `sqlite-vec` for fast, local vector retrieval.

When you ask AIDA a question like "check my battery health", it first queries its RAG knowledge base to find relevant tables (e.g., `battery.table`), reads the schema, and then constructs a precise `osquery` SQL statement to get the actual data.

## Prerequisites

*   Python 3.12+
*   `git`
*   **Ollama** running locally with `gemma3:27b` pulled (for the main agent).
*   `osquery` installed on the host system (for executing actual queries).

## Quick Setup

We provide a setup script to automate the entire initialization process, including installing dependencies, fetching data, downloading the embedding model, and building the RAG database.

```bash
./setup.sh
```

*Note: The ingestion step in the setup script may take several minutes depending on your hardware.*

## Usage

### Run the Agent (Web UI)

Start the FastAPI server to interact with Aida via a web interface:

```bash
uvicorn main:app --reload
```

Access the UI at `http://127.0.0.1:8000`.

### Development Mode (ADK Web)

For development, you can also run the agent using the Agent Development Kit (ADK) web runner. This requires `google-adk` to be installed (which is handled by `setup.sh`).

```bash
adk web aida.agent:root_agent
```

This will start a development server, typically at `http://localhost:5173`, providing a richer debugging interface for the agent's thought process and tool usage.

### Standalone RAG Testing

You can test the schema RAG tool directly from the command line:

```bash
python3 aida/osquery_rag.py "what table contains process open files?"
```

## Cleanup

To remove all generated data, models, and the database, run:

```bash
./cleanup.sh
```

## Architecture Notes

*   **Local-First**: All components (LLM, Embeddings, DB) run locally.
*   **Smarter Chunking**: The ingestion process checks if a whole `.table` file fits within the model's 2048-token context window. If it does, it's ingested as a single chunk to preserve context.
*   **Full Document Retrieval**: Search queries return the complete content of the matching `.table` file.
