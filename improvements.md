# AIDA - Proposed Improvements

## 1. Critical Performance & Accuracy Optimizations
*   **Persistent Model Loading (Immediate Priority):** Refactor the RAG system to initialize the embedding model and database connection only once at startup as a global singleton. Currently, it reloads on every query, causing unacceptable latency.
*   **Hybrid Search (Accuracy Upgrade):** Combine semantic vector search with SQLite FTS5 (Full-Text Search). This will improve retrieval accuracy for technical terms where exact matches (e.g., specific table names like `authorized_keys` vs `known_hosts`) are more important than semantic similarity.

## 2. Core Agent Capabilities
*   **Query Library & Pack Ingestion:**
    *   Implement a `query_library` table in `osquery.db` to store pre-defined, high-value queries.
    *   **Strategy:** Develop a mechanism (likely in `setup.sh` or a new `upgrade.sh`) to fetch standard "Query Packs" from reputable sources (e.g., official osquery GitHub repository, Palantir's open-source packs) during installation. These packs will be parsed and indexed into the library, tagged by their source pack (e.g., `incident-response`, `vulnerability-management`), allowing the agent to leverage expert knowledge immediately.
*   **Long-Term Memory:** Introduce a simple mechanism for the agent to "pin" important findings. A `memories` table will store timestamped key-value pairs or short summaries, enabling the agent to recall context from previous investigations (e.g., "hostname is web-prod-01").

## 3. Functional Enhancements
*   **Debug Console (Real-time Logs & Thoughts):** Instead of cluttering the main chat, add a collapsible "Debug Console" to display raw tool calls (e.g., `SELECT * FROM processes...`) and the agent's internal reasoning stream for transparency without breaking immersion.
*   **Session Persistence:** Implement ephemeral or on-demand session saving to preserve conversation context across server restarts, without permanently logging all sensitive system data by default.

## 4. Interface Improvements (Visual & UX)
*   **Command History:** Implement Up/Down arrow navigation in the input box to cycle through previous commands.
*   **"Active Tool" Indicator:** Visual feedback in the UI when a long-running tool (like a complex `osquery` scan) is executing.
*   **Sound Effects:** Add optional, subtle retro sound effects for user feedback (must include a mute toggle).
*   **Interactive Tables (Low Priority):** Render `osquery` JSON output as sortable HTML tables. (Deprioritized in favor of raw data readability for now).