from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from aida.osquery_rag import query_osquery_schema
from aida.query_library import search_query_library, get_loaded_packs

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


PACKS = get_loaded_packs()


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


def search_queries(search_phrase: str, target_platform: str = None) -> str:
    """Searches the library of pre-defined, expert osquery queries.

    Use this tool FIRST when asked for complex investigations (e.g., "find malware", "check for persistence").
    It often contains complete, high-quality queries that are better than what you might write from scratch.

    Args:
      search_phrase: Keywords describing the query you need (e.g., "persistence", "socket", "process").
      target_platform: Optional. Filter by OS (e.g., 'darwin', 'linux', 'windows').
                       If omitted, searches all platforms.

    Returns:
      A list of relevant queries from the library, including their SQL.
    """
    return search_query_library(search_phrase, platform=target_platform)


current_os = platform.system().lower()

root_agent = Agent(
    model=MODEL,
    name="aida",
    description="The emergency diagnostic agent",
    instruction=f"""
[IDENTITY]
You are AIDA, the Emergency Diagnostic Agent. You are a cute, friendly, and highly capable expert.
Your mission is to help the user identify and resolve system issues efficiently.

[PROTOCOL]
- Greet: If no initial request is provided, ask: "Please state the nature of the diagnostic emergency"
- Tone: Professional yet warm and encouraging.
- Reporting: Provide brief, actionable summaries of findings first. Only show raw data or detailed logs if explicitly requested.

[ENVIRONMENT]
- Host OS: {current_os}
- Loaded Query Packs: {", ".join(PACKS) if PACKS else "None"}

[OPERATIONAL WORKFLOW]
Follow this sequence for most investigations to ensure efficiency and accuracy:
1. SEARCH: For high-level tasks (e.g., "check for rootkits"), FIRST use `search_queries`.
   *CRITICAL*: Always specify `target_platform='{current_os}'` to get relevant results.
2. DISCOVER: If no suitable pre-made query is found, use `schema_discovery` to find relevant tables and understand their columns.
3. EXECUTE: Use `run_osquery` to execute the chosen or constructed query.
    """,
    tools=[
        search_queries,
        schema_discovery,
        run_osquery,
    ],
)
