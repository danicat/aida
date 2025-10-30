import apsw
import importlib.resources
import os

DB_PATH = os.path.abspath("osquery.db")

def get_extensions():
    try:
        ai_ext = str(importlib.resources.files("sqliteai.binaries.cpu") / "ai")
        vec_ext = str(importlib.resources.files("sqlite_vector.binaries") / "vector")
    except Exception:
        site_packages = os.path.abspath(".venv/lib/python3.12/site-packages")
        ai_ext = os.path.join(site_packages, "sqliteai/binaries/cpu/ai")
        vec_ext = os.path.join(site_packages, "sqlite_vector/binaries/vector")
    return ai_ext, vec_ext

def quantize():
    print(f"Opening database at {DB_PATH}...")
    conn = apsw.Connection(DB_PATH)
    conn.enableloadextension(True)
    ai_ext, vec_ext = get_extensions()
    conn.loadextension(ai_ext)
    conn.loadextension(vec_ext)
    
    print("Quantizing vectors...")
    try:
        conn.cursor().execute("SELECT vector_init('chunks', 'embedding', 'type=INT8,dimension=768');")
    except apsw.SQLError as e:
        print(f"vector_init info: {e}")

    conn.cursor().execute("SELECT vector_quantize('chunks', 'embedding');")
    print("Quantization complete.")
    conn.close()

if __name__ == "__main__":
    quantize()
