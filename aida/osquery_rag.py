import sqlite3
import os
import threading

# Try to use importlib.resources for Python 3.9+
try:
    from importlib.resources import files
except ImportError:
    pass

# Hardcoded paths for now, could be configured via env vars or settings
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "osquery.db")
MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models/unsloth/embeddinggemma-300m-GGUF/embeddinggemma-300M-Q8_0.gguf",
)


def get_extensions():
    try:
        ai_ext = str(files("sqliteai") / "binaries" / "cpu" / "ai.dylib")
        vec_ext = str(files("sqlite_vector") / "binaries" / "vector.dylib")

        if not os.path.exists(ai_ext):
            raise FileNotFoundError("AI extension not found via importlib")

        return ai_ext, vec_ext
    except Exception:
        # Fallback for when running from different contexts
        site_packages = os.path.join(PROJECT_ROOT, ".venv/lib/python3.14/site-packages")
        ai_ext = os.path.join(site_packages, "sqliteai/binaries/cpu/ai.dylib")
        vec_ext = os.path.join(site_packages, "sqlite_vector/binaries/vector.dylib")
        return ai_ext, vec_ext


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
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.conn.enable_load_extension(True)
            ai_ext, vec_ext = get_extensions()
            self.conn.load_extension(ai_ext)
            self.conn.load_extension(vec_ext)

            cursor = self.conn.cursor()

            # Ensure vector_init is called for this connection for ALL vector tables.
            for table in ["chunks", "query_embeddings"]:
                try:
                    cursor.execute(
                        f"SELECT vector_init('{table}', 'embedding', 'type=INT8,dimension=768');"
                    )
                except Exception:
                    # print(f"Debug: vector_init for {table} result: {e}")
                    pass

            # Load model and context ONCE
            print(f"Loading model from {MODEL_PATH}...")
            cursor.execute("SELECT llm_model_load(?, 'n_gpu_layers=0');", (MODEL_PATH,))
            cursor.execute(
                "SELECT llm_context_create('n_ctx=2048,embedding_type=INT8,pooling_type=mean,generate_embedding=1,normalize_embedding=1');"
            )
            print("Model loaded.")

            self._initialized = True

    def query(self, query_text: str, k: int = 5) -> str:
        if not self._initialized:
            self.initialize()

        try:
            cursor = self.conn.cursor()

            # Generate query embedding
            cursor.execute("SELECT llm_embed_generate(?)", (query_text,))
            result = cursor.fetchone()
            if not result:
                return "Failed to generate embedding for query."
            query_embedding = result[0]

            # Perform vector search
            cursor.execute(
                """
                SELECT
                    documents.uri,
                    documents.content,
                    MIN(v.distance) as distance
                FROM vector_quantize_scan('chunks', 'embedding', ?, ?) AS v
                JOIN chunks ON chunks.id = v.rowid
                JOIN documents ON documents.id = chunks.document_id
                GROUP BY documents.id
                ORDER BY distance ASC
            """,
                (query_embedding, k),
            )

            results = cursor.fetchall()

            if not results:
                return "No relevant documentation found."

            formatted_results = []
            for uri, content, distance in results:
                formatted_results.append(
                    f"Source: {uri}\nContent:\n{content.strip()}\n"
                )

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
