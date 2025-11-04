import json
import os
import glob
import sys
import re

# Ensure we can import from aida
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from aida.osquery_rag import rag_engine

DB_PATH = "osquery.db"
PACKS_DIR = "osquery_data/packs"


def init_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_library (
            name TEXT,
            pack TEXT,
            query TEXT,
            description TEXT,
            value TEXT,
            platform TEXT,
            PRIMARY KEY (name, pack)
        )
    """)

    cursor.execute("DROP TABLE IF EXISTS query_library_fts")
    cursor.execute("""
        CREATE VIRTUAL TABLE query_library_fts USING fts5(
            name, pack, description, value, query, platform,
            tokenize='porter'
        )
    """)

    # Initialize vector table for query library as a NORMAL table
    cursor.execute("DROP TABLE IF EXISTS query_embeddings")
    cursor.execute(
        "CREATE TABLE query_embeddings (rowid INTEGER PRIMARY KEY, embedding BLOB)"
    )

    # Initialize for quantization
    try:
        cursor.execute(
            "SELECT vector_init('query_embeddings', 'embedding', 'type=INT8,dimension=768');"
        )
    except Exception as e:
        print(f"Warning initializing vector table: {e}")

    conn.commit()


def ingest_pack(conn, pack_path):
    pack_name = os.path.basename(pack_path).replace(".conf", "").replace(".json", "")
    print(f"Ingesting pack: {pack_name}...")

    try:
        with open(pack_path, "r") as f:
            content = f.read()
            content = re.sub(r"\\s*\n", " ", content)
            data = json.loads(content)

        pack_platform = data.get("platform", "all")
        queries = data.get("queries", {})
        cursor = conn.cursor()

        count = 0
        for query_name, query_data in queries.items():
            if isinstance(query_data, str):
                sql = query_data
                desc = ""
                val = ""
                platform = pack_platform
            else:
                sql = query_data.get("query")
                desc = query_data.get("description", "")
                val = query_data.get("value", "")
                # Inherit from pack if not specified in query
                platform = query_data.get("platform", pack_platform)

            if sql:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO query_library (name, pack, query, description, value, platform)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (query_name, pack_name, sql, desc, val, platform),
                )

                cursor.execute(
                    "SELECT rowid FROM query_library WHERE name = ? AND pack = ?",
                    (query_name, pack_name),
                )
                row_result = cursor.fetchone()
                if row_result:
                    rowid = row_result[0]
                    embed_text = f"Name: {query_name}\nDescription: {desc}\nRationale: {val}\nSQL: {sql}"
                    cursor.execute(
                        "INSERT OR REPLACE INTO query_embeddings(rowid, embedding) VALUES (?, llm_embed_generate(?))",
                        (rowid, embed_text),
                    )
                    count += 1

        conn.commit()
        print(f"  - Ingested {count} queries from {pack_name}")

    except json.JSONDecodeError as e:
        print(f"  - ERROR: Failed to parse {pack_name}: {e}")
    except Exception as e:
        print(f"  - ERROR: {e}")


def populate_fts(conn):
    print("Populating FTS index...")
    conn.execute(
        "INSERT INTO query_library_fts (name, pack, query, description, value, platform) SELECT name, pack, query, description, value, platform FROM query_library"
    )
    conn.commit()
    print("FTS index populated.")


def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run setup.sh first.")
        return

    print("Initializing RAG engine...")
    rag_engine.initialize()
    rag_engine.create_context()
    conn = rag_engine.conn

    init_db(conn)

    pack_files = glob.glob(os.path.join(PACKS_DIR, "*.conf")) + glob.glob(
        os.path.join(PACKS_DIR, "*.json")
    )

    if not pack_files:
        print(f"No pack files found in {PACKS_DIR}")
        return

    for pack_file in pack_files:
        ingest_pack(conn, pack_file)

    populate_fts(conn)

    print("Quantizing query vectors...")
    try:
        conn.execute("SELECT vector_quantize('query_embeddings', 'embedding');")
    except Exception as e:
        print(f"Error quantizing: {e}")

    print("Query library ingestion complete.")


if __name__ == "__main__":
    main()