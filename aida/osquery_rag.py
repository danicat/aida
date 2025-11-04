import os
import threading
import sys
from unittest.mock import MagicMock

# Hack: Mock markitdown to bypass dependency issues on Python 3.14.
sys.modules["markitdown"] = MagicMock()

from sqlite_rag import SQLiteRag

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "osquery.db")


class RAGEngine:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(RAGEngine, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            print("Initializing RAG Engine...")
            # SQLiteRag.create will load settings from the DB if they exist.
            self.rag = SQLiteRag.create(DB_PATH, require_existing=True)

            # Initialize vector table for query library if it exists.
            # This is needed for every new connection that wants to use vector_quantize_scan on this table.
            try:
                self.rag._conn.execute(
                    "SELECT vector_init('query_embeddings', 'embedding', 'type=INT8,dimension=768');"
                )
            except Exception:
                # Ignore errors if table doesn't exist yet (e.g. before ingest_packs)
                pass

            self._initialized = True
            print("RAG Engine initialized.")

    @property
    def conn(self):
        if not self._initialized:
            self.initialize()
        return self.rag._conn

    def create_context(self):
        if not self._initialized:
            self.initialize()
        self.rag._ensure_initialized()
        self.rag._engine.create_new_context()

    def query(self, query_text: str, k: int = 5) -> str:
        if not self._initialized:
            self.initialize()

        try:
            # Get more chunks to ensure we have enough unique documents
            results = self.rag.search(query_text, top_k=k * 2)

            if not results:
                return "No relevant documentation found."

            unique_docs = {}
            for res in results:
                if res.document.uri not in unique_docs:
                    unique_docs[res.document.uri] = res.document.content.strip()
                if len(unique_docs) >= k:
                    break

            formatted_results = []
            for uri, content in unique_docs.items():
                formatted_results.append(f"Source: {uri}\nContent:\n{content}\n")

            return "\n---\n".join(formatted_results)

        except Exception as e:
            return f"Error querying osquery schema: {e}"


# Global instance
rag_engine = RAGEngine()


def query_osquery_schema(query: str, k: int = 5) -> str:
    """
    Queries the osquery schema documentation using RAG.
    Uses the persistent RAGEngine instance.
    """
    return rag_engine.query(query, k)


if __name__ == "__main__":
    import sys

    query_text = sys.argv[1] if len(sys.argv) > 1 else "processes"
    # Initialize explicitly if running as script
    rag_engine.initialize()
    print(query_osquery_schema(query_text))
