import sqlite3
import os
from aida.osquery_rag import rag_engine

def search_query_library(search_phrase: str) -> str:
    """
    Searches the pre-defined query library for relevant queries using vector search.
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
        
        # Perform vector search using vector_quantize_scan
        cursor.execute("""
            SELECT
                ql.name, ql.pack, ql.description, ql.query,
                v.distance
            FROM vector_quantize_scan('query_embeddings', 'embedding', ?, 10) AS v
            JOIN query_library ql ON ql.rowid = v.rowid
            ORDER BY v.distance ASC
        """, (query_embedding,))
        
        results = cursor.fetchall()
        
        formatted_results = []
        for name, pack, description, query, distance in results:
            # Heuristic threshold based on observation. Lower distance is better.
            # "launchd" -> ~165
            # "nonsense" -> ~207
            if distance > 200:
                 continue
            formatted_results.append(f"Name: {name} (Pack: {pack})\nDescription: {description}\nSQL: {query}\n(Distance: {distance:.2f})\n")
            
        if not formatted_results:
             return f"No queries found in library matching '{search_phrase}'."

        return "\n---\n".join(formatted_results[:5]) # Limit to top 5 after filtering
        
    except Exception as e:
        return f"Error searching query library: {e}"