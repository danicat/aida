import sqlite3
import os
import json
import sys

# Try to use importlib.resources for Python 3.9+
try:
    from importlib.resources import files
except ImportError:
    # Fallback or just fail if < 3.9, but we are on 3.14
    pass

DB_PATH = os.path.abspath("osquery.db")
SPECS_DIR = os.path.abspath("osquery_data/specs")
# Adjust model path if necessary, assuming it's relative to project root
MODEL_PATH = os.path.abspath("./models/unsloth/embeddinggemma-300m-GGUF/embeddinggemma-300M-Q8_0.gguf")

def get_extensions():
    # Locate the extension binaries using importlib.resources if possible,
    # otherwise fall back to assumed paths in site-packages.
    try:
        import sqliteai
        import sqlite_vector
        
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
        # This is brittle but might work if importlib fails for some reason
        site_packages = os.path.abspath(os.path.join(os.path.dirname(sqliteai.__file__), ".."))
        ai_ext = os.path.join(site_packages, "sqliteai/binaries/cpu/ai.dylib")
        vec_ext = os.path.join(site_packages, "sqlite_vector/binaries/vector.dylib")
        return ai_ext, vec_ext

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)
    
    ai_ext, vec_ext = get_extensions()
    print(f"Loading extensions:\n  AI: {ai_ext}\n  Vec: {vec_ext}")
    conn.load_extension(ai_ext)
    conn.load_extension(vec_ext)
    
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uri TEXT UNIQUE,
            content TEXT,
            metadata TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            content TEXT,
            embedding BLOB,
            FOREIGN KEY(document_id) REFERENCES documents(id)
        );
    """)
    cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(content, content='chunks', content_rowid='id');")
    
    # sqlite-vec initialization
    try:
        # Check if already initialized to avoid error on re-run if file exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chunks_vec'")
        if not cursor.fetchone():
             cursor.execute("SELECT vector_init('chunks', 'embedding', 'type=INT8,dimension=768');")
    except sqlite3.OperationalError as e:
        print(f"Warning during vector_init: {e}")

    return conn

def setup_llm(conn):
    cursor = conn.cursor()
    # n_gpu_layers=0 for CPU
    cursor.execute("SELECT llm_model_load(?, 'n_gpu_layers=0');", (MODEL_PATH,))
    # Configure context for embedding
    cursor.execute("SELECT llm_context_create('n_ctx=2048,embedding_type=INT8,pooling_type=mean,generate_embedding=1,normalize_embedding=1');")

def ingest_file(conn, file_path, rel_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO documents (uri, content, metadata) VALUES (?, ?, ?)",
                   (rel_path, content, json.dumps({"source": "osquery_specs"})))
    
    # Get the document ID
    cursor.execute("SELECT id FROM documents WHERE uri = ?", (rel_path,))
    row = cursor.fetchone()
    if not row:
        return # Should not happen if insert worked or ignored
    doc_id = row[0]

    # Check if already chunked (simple check)
    cursor.execute("SELECT count(*) FROM chunks WHERE document_id = ?", (doc_id,))
    if cursor.fetchone()[0] > 0:
        return

    # Check token count for the whole file
    cursor.execute("SELECT llm_token_count(?)", (content,))
    token_count = cursor.fetchone()[0]

    if token_count <= 2000:
        chunks = [content]
    else:
        # Fallback to paragraph splitting if too large
        print(f"  -> File too large ({token_count} tokens), splitting...")
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
    
    for chunk in chunks:
        if not chunk: continue
        # Generate embedding
        try:
            cursor.execute("SELECT llm_embed_generate(?)", (chunk,))
            embedding = cursor.fetchone()[0]
            
            cursor.execute("INSERT INTO chunks (document_id, content, embedding) VALUES (?, ?, ?)",
                           (doc_id, chunk, embedding))
        except sqlite3.OperationalError as e:
             print(f"  -> Error embedding chunk in {rel_path}: {e}")

def ingest():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    print(f"Initializing database at {DB_PATH}...")
    conn = init_db()
    
    print("Loading LLM...")
    setup_llm(conn)
    
    print(f"Scanning {SPECS_DIR} for .table files...")
    count = 0
    # SQLite3 default is autocommit off when in a transaction, but let's be explicit
    # or just let it handle it. For speed, explicit transactions are better.
    
    files_to_ingest = []
    for root, _, files in os.walk(SPECS_DIR):
        for file in files:
            if file.endswith(".table"):
                files_to_ingest.append(os.path.join(root, file))

    total_files = len(files_to_ingest)
    print(f"Found {total_files} files to ingest.")

    for i, file_path in enumerate(files_to_ingest):
        rel_path = os.path.relpath(file_path, SPECS_DIR)
        # print(f"Ingesting {rel_path} ({i+1}/{total_files})...")
        
        # Wrap each file in a transaction or batch them. 
        # Batching 10 at a time for reasonable speed/safety trade-off.
        if i % 10 == 0:
             if i > 0: conn.commit()
        
        ingest_file(conn, file_path, rel_path)
        count += 1
        if count % 50 == 0:
            print(f"Ingested {count}/{total_files}...")

    conn.commit()
    print(f"Finished ingesting {count} files.")
    
    print("Quantizing vectors...")
    # This might take a moment
    conn.execute("SELECT vector_quantize('chunks', 'embedding');")
    print("Quantization complete.")
    
    conn.close()

if __name__ == "__main__":
    ingest()