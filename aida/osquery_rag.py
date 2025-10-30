import sqlite3
import os
import json

# Try to use importlib.resources for Python 3.9+
try:
    from importlib.resources import files
except ImportError:
    pass

# Hardcoded paths for now, could be configured via env vars or settings
# Assuming this file is in aida/osquery_rag.py, so project root is one level up
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "osquery.db")
MODEL_PATH = os.path.join(PROJECT_ROOT, "models/unsloth/embeddinggemma-300m-GGUF/embeddinggemma-300M-Q8_0.gguf")

def get_extensions():
    try:
        import sqliteai
        import sqlite_vector
        
        ai_ext = str(files("sqliteai") / "binaries" / "cpu" / "ai.dylib")
        vec_ext = str(files("sqlite_vector") / "binaries" / "vector.dylib")
        
        if not os.path.exists(ai_ext):
             # Fallback if files() doesn't return absolute path or something went wrong
             raise FileNotFoundError("AI extension not found via importlib")

        return ai_ext, vec_ext
    except Exception:
        # Fallback for when running from different contexts if needed, 
        # or if importlib fails.
        # Assuming standard venv structure relative to project root if all else fails
        site_packages = os.path.join(PROJECT_ROOT, ".venv/lib/python3.14/site-packages")
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

def query_osquery_schema(query: str, k: int = 5) -> str:
    """
    Queries the osquery schema documentation using RAG.
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # Load model and context
        cursor.execute("SELECT llm_model_load(?, 'n_gpu_layers=0');", (MODEL_PATH,))
        cursor.execute("SELECT llm_context_create('n_ctx=2048,embedding_type=INT8,pooling_type=mean,generate_embedding=1,normalize_embedding=1');")
        
        # Generate query embedding
        cursor.execute("SELECT llm_embed_generate(?)", (query,))
        result = cursor.fetchone()
        if not result:
             return "Failed to generate embedding for query."
        query_embedding = result[0]
        
        # Ensure vector context is loaded
        try:
            # Check if already initialized to avoid error on re-run if file exists
            # Actually, vector_init might throw if already initialized in this session, 
            # or if the table already exists.
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_vec'")
            if not cursor.fetchone():
                 cursor.execute("SELECT vector_init('chunks', 'embedding', 'type=INT8,dimension=768');")
        except sqlite3.OperationalError:
            pass

        # Perform vector search
        cursor.execute("""
            SELECT
                documents.uri,
                documents.content,
                MIN(v.distance) as distance
            FROM vector_quantize_scan('chunks', 'embedding', ?, ?) AS v
            JOIN chunks ON chunks.id = v.rowid
            JOIN documents ON documents.id = chunks.document_id
            GROUP BY documents.id
            ORDER BY distance ASC
        """, (query_embedding, k))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return "No relevant documentation found."
            
        formatted_results = []
        for uri, content, distance in results:
            formatted_results.append(f"Source: {uri}\nContent:\n{content.strip()}\n")
            
        return "\n---\n".join(formatted_results)
        
    except Exception as e:
        return f"Error querying osquery schema: {e}"

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "processes"
    print(query_osquery_schema(query))