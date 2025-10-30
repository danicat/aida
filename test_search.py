import os
import sqlite3

# Try to use importlib.resources for Python 3.9+
try:
    from importlib.resources import files
except ImportError:
    pass

DB_PATH = os.path.abspath("osquery.db")
# Adjust model path if necessary, assuming it's relative to project root
MODEL_PATH = os.path.abspath(
    "./models/unsloth/embeddinggemma-300m-GGUF/embeddinggemma-300M-Q8_0.gguf"
)


def get_extensions():
    # Locate the extension binaries using importlib.resources if possible,
    # otherwise fall back to assumed paths in site-packages.
    try:
        import sqliteai

        # Based on the ls -R output:
        # sqlite_vector/binaries/vector.dylib
        # sqliteai/binaries/cpu/ai.dylib

        ai_ext = str(files("sqliteai") / "binaries" / "cpu" / "ai.dylib")
        vec_ext = str(files("sqlite_vector") / "binaries" / "vector.dylib")

        if not os.path.exists(ai_ext):
            raise FileNotFoundError(f"AI extension not found at {ai_ext}")
        if not os.path.exists(vec_ext):
            raise FileNotFoundError(f"Vector extension not found at {vec_ext}")

        return ai_ext, vec_ext
    except Exception as e:
        print(f"Error locating extensions via importlib: {e}")
        # Fallback to hardcoded relative paths if in a venv
        import sqliteai

        site_packages = os.path.abspath(
            os.path.join(os.path.dirname(sqliteai.__file__), "..")
        )
        ai_ext = os.path.join(site_packages, "sqliteai/binaries/cpu/ai.dylib")
        vec_ext = os.path.join(site_packages, "sqlite_vector/binaries/vector.dylib")
        return ai_ext, vec_ext


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    ai_ext, vec_ext = get_extensions()
    conn.load_extension(ai_ext)
    conn.load_extension(vec_ext)
    return conn


def search(query, k=5):
    conn = get_conn()
    cursor = conn.cursor()

    # Load model and context for query embedding
    cursor.execute("SELECT llm_model_load(?, 'n_gpu_layers=0');", (MODEL_PATH,))
    cursor.execute(
        "SELECT llm_context_create('n_ctx=2048,embedding_type=INT8,pooling_type=mean,generate_embedding=1,normalize_embedding=1');"
    )

    # Generate query embedding
    cursor.execute("SELECT llm_embed_generate(?)", (query,))
    query_embedding = cursor.fetchone()[0]

    # Ensure vector context is loaded (copied from osquery_rag.py)
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_vec'"
        )
        if not cursor.fetchone():
            cursor.execute(
                "SELECT vector_init('chunks', 'embedding', 'type=INT8,dimension=768');"
            )
    except sqlite3.OperationalError:
        pass

    # Perform vector search using vector_quantize_scan as in osquery_rag.py
    cursor.execute(
        """
        SELECT
            documents.uri,
            chunks.content,
            v.distance
        FROM vector_quantize_scan('chunks', 'embedding', ?, ?) AS v
        JOIN chunks ON chunks.id = v.rowid
        JOIN documents ON documents.id = chunks.document_id
        ORDER BY v.distance ASC
    """,
        (query_embedding, k),
    )
    results = cursor.fetchall()

    conn.close()
    return results


if __name__ == "__main__":
    query = "What table contains process information?"
    print(f"Searching for: '{query}'...")
    results = search(query)
    for uri, content, distance in results:
        print(f"--- {uri} (distance: {distance:.4f}) ---")
        # Show a bit more content to verify relevance
        print(content[:300].replace("\n", " ") + "...")
        print()
