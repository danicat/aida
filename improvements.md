# AIDA - Proposed Improvements

## 1. Core Agent Capabilities
*   **Hybrid Search for Schema (Accuracy Upgrade):** Combine semantic vector search with SQLite FTS5 (Full-Text Search) for `schema_discovery`. This will improve retrieval accuracy for technical terms where exact matches (e.g., specific table names like `authorized_keys` vs `known_hosts`) are more important than semantic similarity.
*   **Long-Term Memory:** Introduce a simple mechanism for the agent to "pin" important findings. A `memories` table will store timestamped key-value pairs or short summaries, enabling the agent to recall context from previous investigations (e.g., "hostname is web-prod-01").

## 2. Functional Enhancements
*   **Debug Console (Real-time Logs & Thoughts):** Instead of cluttering the main chat, add a collapsible "Debug Console" to display raw tool calls (e.g., `SELECT * FROM processes...`) and the agent's internal reasoning stream for transparency without breaking immersion.
*   **Session Persistence:** Implement ephemeral or on-demand session saving to preserve conversation context across server restarts, without permanently logging all sensitive system data by default.

## 3. Interface Improvements (Visual & UX)
*   **Command History:** Implement Up/Down arrow navigation in the input box to cycle through previous commands.
*   **"Active Tool" Indicator:** Visual feedback in the UI when a long-running tool (like a complex `osquery` scan) is executing.
*   **Sound Effects:** Add optional, subtle retro sound effects for user feedback (must include a mute toggle).
*   **Interactive Tables (Low Priority):** Render `osquery` JSON output as sortable HTML tables. (Deprioritized in favor of raw data readability for now).
