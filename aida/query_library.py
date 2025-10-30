import sqlite3
import os
from aida.osquery_rag import rag_engine


def search_query_library(search_phrase: str, platform: str = None) -> str:
    """
    Searches the pre-defined query library for relevant queries using vector search,
    optionally filtered by operating system.
    """
    try:
        rag_engine.initialize()
        conn = rag_engine.conn
        cursor = conn.cursor()

        # Generate query embedding
        cursor.execute("SELECT llm_embed_generate(?)", (search_phrase,))
        result = cursor.fetchone()
        if not result:
            return "Failed to generate embedding for query."
        query_embedding = result[0]

        sql = """
            SELECT
                ql.name, ql.pack, ql.description, ql.query, ql.platform,
                v.distance
            FROM vector_quantize_scan('query_embeddings', 'embedding', ?, 50) AS v
            JOIN query_library ql ON ql.rowid = v.rowid
        """
        params = [query_embedding]

        if platform:
            allowed_platforms = {platform.lower(), "all"}
            if platform.lower() in ["darwin", "linux"]:
                allowed_platforms.add("posix")

            placeholders = ",".join(["?"] * len(allowed_platforms))
            sql += f" WHERE ql.platform IN ({placeholders})"
            params.extend(allowed_platforms)

        sql += " ORDER BY v.distance ASC"

        cursor.execute(sql, params)
        results = cursor.fetchall()

        formatted_results = []
        for name, pack, description, query, plat, distance in results:
            # Heuristic threshold.
            if distance > 200:
                continue
            formatted_results.append(
                f"Name: {name} (Pack: {pack}, Platform: {plat})\nDescription: {description}\nSQL: {query}\n(Distance: {distance:.2f})\n"
            )

        if not formatted_results:
            plat_msg = f" for {platform}" if platform else ""
            return f"No relevant queries found{plat_msg} matching '{search_phrase}'."

        return "\n---\n".join(formatted_results[:5])

    except Exception as e:
        return f"Error searching query library: {e}"


def get_loaded_packs() -> list[str]:
    """Retrieves the names of all loaded query packs."""
    try:
        # We can use a fresh connection here as it's a simple metadata query,
        # or use rag_engine.conn if initialized, but fresh is safer if called early.
        # Actually, DB_PATH is needed.
        PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        DB_PATH_LOCAL = os.path.join(PROJECT_ROOT, "osquery.db")

        conn = sqlite3.connect(DB_PATH_LOCAL)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT pack FROM query_library ORDER BY pack")
        packs = [row[0] for row in cursor.fetchall()]
        conn.close()
        return packs
    except Exception:
        # print(f"Warning: Could not load packs: {e}")
        return []
