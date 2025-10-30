# Report: SQLite-RAG Implementation for Osquery Documentation

## 1. Initial Task
The objective was to create a Retrieval-Augmented Generation (RAG) tool capable of querying local osquery schema specifications (`.table` files). The specific requirement was to utilize the `sqlite-rag` library to maintain consistency with other project components relying on SQLite.

## 2. Implementation Challenges and Pivots
The primary challenge stemmed from environment limitations regarding SQLite extensions.

*   **Challenge: System SQLite Limitations**
    The `sqlite-rag` Python library depends on the standard `sqlite3` module and requires `connection.enable_load_extension(True)` to load standard extensions like `sqlite-vec` (for vector search) and `sqlite-ai` (for LLM embedding generation). On macOS, the system-provided SQLite library used by Python often has this feature disabled for security reasons, causing immediate failure upon initialization.

*   **Failed Workarounds**
    Attempts to install drop-in replacements like `pysqlite3-binary` failed due to unavailability for the platform. Compiling `pysqlite3` from source also failed due to linking issues against the restricted system SQLite.

*   **Pivot to APSW**
    To adhere to the strict requirement of using SQLite, we pivoted to using **APSW (Another Python SQLite Wrapper)**. Unlike the standard `sqlite3` module, APSW includes its own bundled, fully-featured version of SQLite with extension loading enabled.

*   **Adaptation of sqlite-rag**
    The high-level `sqlite-rag` library is hardcoded to use `sqlite3.Connection` objects and could not be easily patched to use APSW. Consequently, we bypassed the library's Python API and directly utilized its underlying engine components. We manually replicated its RAG pipeline by:
    1.  Locating the binary extensions (`ai0.so`/`dll`, `vector0.so`/`dll`) installed by `sqlite-rag`'s dependencies.
    2.  Loading these extensions into an APSW connection.
    3.  Reverse-engineering the SQL commands used by `sqlite-rag` for schema creation, embedding generation (using the `embeddinggemma-300m` model), and vector quantization.

## 3. Successes
Despite the tooling pivot, the core objectives were met:
*   **Pure SQLite RAG:** A fully functional RAG system was implemented entirely within SQLite, with no external vector database required.
*   **Data Ingestion:** Successfully ingested 283 osquery `.table` files into a local `osquery.db`.
*   **Advanced Features Replicated:** Successfully replicated advanced features of the original stack, including:
    *   In-database embedding generation using `sqlite-ai` and the Gemma-300M model.
    *   INT8 vector quantization using `sqlite-vec` for efficient storage and retrieval.
*   **Functional Tool:** Delivered `aida/osquery_rag.py`, which provides a simple Python API to query the database.

## 4. Limitations of Current Approach
*   **Cold Start Latency:** The current `query_osquery_schema` function loads the 300M parameter LLM model into memory for *every* query. This introduces significant latency (several seconds) per call.
*   **Vector-Only Search:** The current implementation only performs semantic vector search. It lacks the hybrid approach (combining vector search with FTS5 keyword search using Reciprocal Rank Fusion) that the full `sqlite-rag` library implements.

## 5. Points for Improvement
*   **Persistent Model Loading:** For a production agent, the LLM model should be loaded once and kept in memory (e.g., by keeping the APSW connection open in a persistent process) to eliminate per-query latency.
*   **Hybrid Search:** Upgrade the search query to use standard FTS5 alongside `vector_quantize_scan` and combine their scores for more robust retrieval, especially for exact table name matches.

## 6. Chunking Strategy Improvement
Initially, a naive chunking strategy (splitting by double newlines) was used. This sometimes resulted in fragmented schema definitions being returned, where a search result might only contain a subset of columns or just metadata.

To address this, a "smarter" chunking strategy was implemented:
1.  **Whole-File Ingestion:** During ingestion, the token count of each `.table` file is checked against the model's context window (2048 tokens). Since most osquery specification files are small (<4KB), they fit entirely within this limit. These files are now ingested as single, complete chunks.
2.  **Full Document Retrieval:** The search query in `aida/osquery_rag.py` was updated to return the content of the *parent document* rather than the matched chunk. This ensures that even if a file was large enough to require splitting, a match on any of its chunks will return the complete schema definition to the user.
3.  **Deduplication:** The search query now groups results by document ID to prevent returning the same full schema multiple times if multiple chunks from the same file match the query.

## 8. Refactor to Standard `sqlite3` (2025-10-29)
Following an environment update that enabled extension loading in the standard Python `sqlite3` module on macOS, the project was refactored to remove the dependency on APSW.

*   **Re-evaluation:** A check confirmed that `sqlite3.connect(':memory:').enable_load_extension(True)` now succeeds.
*   **Dependency Changes:**
    *   Installed `sqlite-rag` to acquire the necessary extension binaries (`sqlite-ai`, `sqlite-vec`).
    *   Encountered a dependency conflict with `markitdown` (requiring `onnxruntime` not available for Python 3.14 on macOS ARM64), preventing use of the high-level `sqlite-rag` Python API.
    *   Decided to use standard `sqlite3` while manually loading the extensions, similar to the APSW approach but with standard tooling.
*   **Simplification & Refactor:**
    *   **Removed APSW Dependency:** Eliminated the third-party `apsw` C-extension, reducing the project's footprint and relying solely on the Python standard library for database interaction.
    *   **Unified Project Structure:** Consolidated ingestion logic into a single `ingest_osquery.py` script, removing the need for separate standard and APSW versions (`ingest_osquery_apsw.py` was deleted).
    *   **Standard API:** Switched all database interactions to the familiar standard `sqlite3` API, improving maintainability for other Python developers.
*   **Outcome:** The RAG system now operates with the standard Python library, reducing external dependencies while maintaining full functionality and performance.

### Code Comparison: Connection Setup

While the lines of code for connecting are similar, the underlying dependency shift is significant.

**Previous (APSW Dependency):**
```python
import apsw

def get_conn():
    conn = apsw.Connection(DB_PATH)
    conn.enableloadextension(True)
    # ... load extensions ...
    return conn
```

**Current (Standard Library):**
```python
import sqlite3

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    # ... load extensions ...
    return conn
```

## 9. Migration to Gemma 3 (2025-10-29)
The agent was updated to use the `gemma-3-27b-it` model, leveraging its improved capabilities, including function calling.

*   **Model Update:** Switched from `LiteLlm` (using `ollama_chat/gpt-oss`) to `Gemma` (using `gemma-3-27b-it`) in `aida/agent.py`.
*   **Function Calling:** Verified that the `google.adk` library's `Gemma` class correctly implements function calling as per the [Gemma documentation](https://ai.google.dev/gemma/docs/capabilities/function-calling). This allows the agent to natively invoke tools like `run_osquery` and `schema_discovery`.

## 10. Performance & Capability Upgrades (2025-10-30)
Addressed critical performance bottlenecks and expanded the agent's knowledge base.

*   **Persistent RAG Engine:**
    *   **Problem:** The RAG system was re-initializing the 300M parameter embedding model on every query, causing multi-second latency.
    *   **Solution:** Refactored `aida/osquery_rag.py` to use a singleton `RAGEngine` class.
    *   **Implementation:** Integrated with FastAPI's lifespan events in `main.py` to initialize the engine once during application startup. Subsequent queries now reuse the loaded model, resulting in near-instant RAG lookups.

*   **Query Library & Pack Ingestion:**
    *   **Problem:** The agent was limited to writing queries from scratch based on schema, missing out on expert knowledge contained in standard osquery packs.
    *   **Solution:** Implemented a system to ingest standard osquery query packs (e.g., `incident-response`, `osx-attacks`) into the database.
    *   **Implementation:**
        *   Updated `setup.sh` to fetch the full `packs` directory from the osquery repository.
        *   Created `ingest_packs.py` to parse `.conf` pack files (handling non-standard JSON formatting issues common in these files) and insert them into a new `query_library` table in `osquery.db`.
        *   Created a dedicated FTS5 index (`query_library_fts`) for efficient full-text search.
        *   Generated vector embeddings for all queries and stored them in `query_embeddings` table (standard BLOB storage).
        *   Added a new tool `search_queries` to the agent, utilizing **vector search** (via `sqlite-vec`) to find semantically relevant queries, with optional platform filtering.

## 11. Resolved Challenges with Vector Search for Query Library (2025-10-30)
*   **Issue:** `vector_quantize_scan` failed with "unable to retrieve context" during runtime, despite successful ingestion.
*   **Root Cause:** The `sqlite-vec` extension appears to require `vector_init` to be called for *each* connection that intends to use quantization-aware functions on a table, likely to register in-memory metadata for that connection's context.
*   **Resolution:** Updated `RAGEngine.initialize` to explicitly call `vector_init` for both `chunks` (schema) and `query_embeddings` (library) tables on the persistent application connection. This successfully enabled robust vector search for both use cases.
