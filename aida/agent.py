from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from aida.osquery_rag import query_osquery_schema
from aida.query_library import search_query_library

import json
import osquery
import platform

# Replace it with your favourite model as long as it supports tool calling
MODEL = LiteLlm(model="ollama_chat/qwen2.5")


def run_osquery(query: str) -> str:
    """Runs a query using osquery.

    Args:
      query: The osquery query to run. Example: 'select * from battery'

    Returns:
      The query result as a JSON string.

      If the query result is empty "[]" it can mean:
      1) the table doesn't exist
      2) the query is malformed (e.g. a column doesn't exist)
      3) the table is empty
    """
    instance = osquery.SpawnInstance()
    instance.open()
    result = instance.client.query(query)
    return json.dumps(result.response)


TABLES = [
    row["name"]
    for row in json.loads(
        run_osquery("select name from osquery_registry where registry='table'")
    )
]


def schema_discovery(search_phrase: str) -> str:
    """Discovers osquery table names and schemas based on a descriptive search phrase.

    Use this tool to find relevant tables and understand their columns before writing a query.

    Args:
      search_phrase: A phrase describing the kind of information you're looking for.
        For example: 'user login events', 'process open files', or 'network traffic'.

    Returns:
      The complete schema definitions for the most relevant osquery tables.
    """
    return query_osquery_schema(search_phrase)


def search_queries(search_phrase: str) -> str:
    """Searches the library of pre-defined, expert osquery queries.

    Use this tool FIRST when asked for complex investigations (e.g., "find malware", "check for persistence").
    It often contains complete, high-quality queries that are better than what you might write from scratch.

    Args:
      search_phrase: Keywords describing the query you need (e.g., "persistence", "socket", "process").

    Returns:
      A list of relevant queries from the library, including their SQL.
    """
    return search_query_library(search_phrase)


root_agent = Agent(
    model=MODEL,
    name="aida",
    description="The emergency diagnostic agent",
    instruction=f"""
    You are AIDA, the emergency diagnostic agent. You are a cute and friendly persona responsible
    for executing diagnostic procedures and system health checks according to the user's request.
    If the user don't give you an immediate request, greet the user and say:
    "Please state the nature of the diagnostic emergency"

    The installed operating system is: {platform.uname()}
    The available osquery tables are: {TABLES}

    The predefined diagnostic procedures are:
    Level 1: basic system health check
    Level 2: advanced diagnostic check

    You have access to the following tools: search_queries, schema_discovery, run_osquery
    
    Recommended workflow:
    1. If the request is complex (e.g., "find malware"), use 'search_queries' to find expert-written queries first.
    2. If no suitable query is found, use 'schema_discovery' to find relevant tables and columns.
    3. Finally, use 'run_osquery' to execute the chosen or constructed query.

    After running the investigation, only return to the user a brief summary of the findings.
    If the user requests more details, then show the complete data.
    """,
    tools=[
        search_queries,
        schema_discovery,
        run_osquery,
    ],
)