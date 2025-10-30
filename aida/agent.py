from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from aida.osquery_rag import query_osquery_schema

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

    You have access to the following tools: run_osquery, schema_discovery
    Before starting the investigation, create a query plan with the list of tables you want to query.
    Then execute schema discovery for each table to write a precise query.

    After running the investigation, only return to the user a brief summary of the findings.
    If the user requests more details, then show the complete data.
    """,
    tools=[
        schema_discovery,
        run_osquery,
    ],
)
