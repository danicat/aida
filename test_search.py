import apsw
import importlib.resources
import os
import json

DB_PATH = os.path.abspath("osquery.db")
MODEL_PATH = os.path.abspath("./models/unsloth/embeddinggemma-300m-GGUF/embeddinggemma-300M-Q8_0.gguf")

def get_extensions():
    try:
        ai_ext = str(importlib.resources.files("sqliteai.binaries.cpu") / "ai")
        vec_ext = str(importlib.resources.files("sqlite_vector.binaries") / "vector")
    except Exception:
        site_packages = os.path.abspath(".venv/lib/python3.12/site-packages")
        ai_ext = os.path.join(site_packages, "sqliteai/binaries/cpu/ai")
        vec_ext = os.path.join(site_packages, "sqlite_vector/binaries/vector")
    return ai_ext, vec_ext

def get_conn():
    conn = apsw.Connection(DB_PATH)
    conn.enableloadextension(True)
    ai_ext, vec_ext = get_extensions()
    conn.loadextension(ai_ext)
    conn.loadextension(vec_ext)
    return conn

def search(query, k=5):
    conn = get_conn()
    cursor = conn.cursor()
    
    # Load model and context for query embedding
    # We might need to keep the model loaded in a real app, but for CLI tool it's fine to load per query
    cursor.execute("SELECT llm_model_load(?, 'n_gpu_layers=0');", (MODEL_PATH,))
    cursor.execute("SELECT llm_context_create('n_ctx=2048,embedding_type=INT8,pooling_type=mean,generate_embedding=1,normalize_embedding=1');")
    
    # Generate query embedding
    cursor.execute("SELECT llm_embed_generate(?)", (query,))
    query_embedding = cursor.fetchone()[0]
    
    # Ensure vector context is loaded
    try:
        cursor.execute("SELECT vector_init('chunks', 'embedding', 'type=INT8,dimension=768');")
    except apsw.SQLError:
        pass

    # Perform vector search
    # Try vector_top_k first, it's the modern entry point.
    # If it fails (e.g. due to quantization mismatch in how it's called), try vector_quantize_scan.
    try:
        cursor.execute("""
            SELECT
                documents.uri,
                chunks.content,
                v.distance
            FROM vector_top_k('chunks', 'embedding', ?, ?) AS v
            JOIN chunks ON chunks.id = v.rowid
            JOIN documents ON documents.id = chunks.document_id
            ORDER BY v.distance ASC
        """, (query_embedding, k))
        results = cursor.fetchall()
    except apsw.SQLError as e:
        # print(f"vector_top_k failed: {e}, trying vector_quantize_scan")
        cursor.execute("""
            SELECT
                documents.uri,
                chunks.content,
                v.distance
            FROM vector_quantize_scan('chunks', 'embedding', ?, ?) AS v
            JOIN chunks ON chunks.id = v.rowid
            JOIN documents ON documents.id = chunks.document_id
            ORDER BY v.distance ASC
        """, (query_embedding, k))
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
