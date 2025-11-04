from aida.osquery_rag import query_osquery_schema

if __name__ == "__main__":
    query = "What table contains process information?"
    print(f"Searching for: '{query}'...")
    results = query_osquery_schema(query)
    print(results)
