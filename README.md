# Aida - Osquery Schema RAG

This project implements a local, SQLite-based Retrieval-Augmented Generation (RAG) tool for querying [osquery](https://osquery.io/) schema specifications. It allows an agent (Aida) or user to semantically search for information about osquery tables, columns, and descriptions without needing external vector databases or API calls.

## Overview

The tool uses a purely local stack:
*   **Database**: SQLite (standard Python `sqlite3` with extensions).
*   **Vector Search**: `sqlite-vec` extension for storing and querying INT8 quantized vectors.
*   **Embedding Generation**: `sqlite-ai` extension running the `embeddinggemma-300m` model directly within the database.
*   **Data Source**: Official osquery specification files (`.table`).

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