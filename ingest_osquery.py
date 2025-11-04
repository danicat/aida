import os
import sys
from unittest.mock import MagicMock

# Hack: Mock markitdown to bypass dependency issues on Python 3.14.
# We don't use FileReader which is the only consumer of markitdown.
sys.modules["markitdown"] = MagicMock()

from sqlite_rag import SQLiteRag

DB_PATH = os.path.abspath("osquery.db")
SPECS_DIR = os.path.abspath("osquery_data/specs")


def ingest():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print(f"Initializing RAG database at {DB_PATH}...")
    # Initialize with quantize_scan=False to speed up ingestion
    rag = SQLiteRag.create(DB_PATH, settings={"quantize_scan": False})

    print(f"Scanning {SPECS_DIR} for .table files...")
    files_to_ingest = []
    for root, _, files in os.walk(SPECS_DIR):
        for file in files:
            if file.endswith(".table"):
                files_to_ingest.append(os.path.join(root, file))

    total_files = len(files_to_ingest)
    print(f"Found {total_files} files to ingest.")

    for i, file_path in enumerate(files_to_ingest):
        rel_path = os.path.relpath(file_path, SPECS_DIR)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        rag.add_text(content, uri=rel_path, metadata={"source": "osquery_specs"})

        if (i + 1) % 50 == 0:
            print(f"Ingested {i + 1}/{total_files}...")

    print(f"Finished ingesting {total_files} files.")
    rag.close()

    print("Updating settings and quantizing vectors...")
    # Re-open with quantize_scan=True to store this setting for future use
    rag = SQLiteRag.create(DB_PATH, settings={"quantize_scan": True})
    rag.quantize_vectors()
    print("Quantization complete.")
    rag.close()


if __name__ == "__main__":
    ingest()
