# AIDA - AI Diagnostic Agent

AIDA (pronounced "ei-da") is an AI Diagnostic Agent designed to perform operating system health checks and diagnostics. It leverages the power of [osquery](https://osquery.io/) to inspect system state in a structured, SQL-like manner.

AIDA is grounded by a local Retrieval-Augmented Generation (RAG) system. It looks up table names in its built-in copy of the official osquery schema documentation before executing any queries.

<video src="assets/demo.webm" controls="controls" style="max-width: 100%;">
</video>

## Architecture & RAG

AIDA runs entirely locally for maximum privacy:
*   **Agent Brain**: Powered by **Qwen 2.5** (via Ollama), chosen for its robust tool-calling capabilities.
*   **Tooling**: It can execute real read-only queries on your host system using `osqueryi`.
*   **RAG Knowledge Base**: A purely local SQLite database containing all osquery table specifications.
    *   **Embeddings**: Generated in-database using `sqlite-ai` and the `embeddinggemma-300m` model.
    *   **Search**: Performed using `sqlite-vec` for fast, local vector retrieval.

When you ask AIDA a question like "check my battery health", it first queries its RAG knowledge base to find relevant tables (e.g., `battery.table`), reads the schema, and then constructs a precise `osquery` SQL statement to get the actual data.

## Prerequisites

*   Python 3.12+
*   `git`
*   **Ollama** running locally.
*   `osquery` installed on the host system (for executing actual queries).

## Quick Setup

We provide a setup script to automate the entire initialization process, including installing dependencies, fetching data, downloading the embedding model, pulling the LLM, and building the RAG database.

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

### Development

#### Running with ADK Web
For a richer development experience with debugging tools:
```bash
adk web aida.agent:root_agent
```

#### Linting & Formatting
We use `ruff` for linting and formatting.

```bash
# Check for issues
ruff check .

# Fix fixable issues
ruff check --fix .

# Format code
ruff format .
```

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