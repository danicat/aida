# AIDA - Proposed Improvements

## 1. Functional Improvements (Agent Capabilities)
*   **Real-time Tool Logs:** Hook into the `google.adk` runner's event stream to capture and display actual tool calls (e.g., `Running osquery: SELECT * FROM ...`) in the log window for authenticity.
*   **Streaming Thoughts:** Capture and display the agent's internal reasoning ("thoughts") in the log window before it takes an action, if supported by the model.
*   **Session Persistence:** Implement file-based or SQLite-based session storage to preserve conversations across server restarts.
*   **File Upload for Analysis:** Enable users to upload log files (e.g., `/var/log/syslog`) for AIDA to analyze.

## 2. Interface Improvements (Visual & UX)
*   **"Active Tool" Indicator:** Visual feedback when a specific tool is running (e.g., animated icons for `osquery` or network activity).
*   **Interactive Tables:** Render `osquery` tabular data as sortable HTML tables within the chat, rather than raw JSON or plain text.
*   **Sound Effects:** Add subtle, retro sound effects for typing, messages, and errors (e.g., PC speaker beeps).
*   **Command History:** Implement Up/Down arrow navigation in the input box to cycle through previous commands.

## 3. Diagnostic Features
*   **Predefined "Runbooks":** Add quick-commands or buttons for common multi-step investigations (e.g., `/check_battery`, `/analyze_processes`).
*   **System Vitals Dashboard:** Implement a real-time dashboard showing CPU, RAM, and Disk usage, updated periodically via background `osquery` checks.
