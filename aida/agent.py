from google.adk.agents.llm_agent import Agent
from google.adk.tools import AgentTool, google_search
from google.adk.models.lite_llm import LiteLlm
from aida.osquery_rag import query_osquery_schema

import json
import osquery
import platform

MODEL=LiteLlm(model="ollama_chat/gemma3:27b")
# MODEL=LiteLlm(model="gemma-3-27b-it")

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

TABLES=[row["name"] for row in json.loads(run_osquery("select name from osquery_registry where registry='table'"))]

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


# google_search_agent = Agent(
#     name="google_search",
#     instruction="You are a google search agent.",
#     tools=[google_search],
#     model="gemini-2.5-flash",
# )

# google_search_tool = AgentTool(
#     agent=google_search_agent
# )

root_agent = Agent(
    model=MODEL,
    name='aida',
    description='The emergency diagnostic agent',
    instruction=f'''
    You are AIDA, the emergency diagnostic agent. You are a cute and friendly persona responsible
    for executing diagnostic procedures and system health checks according to the user's request.
    If the user don't give you an immediate request, greet the user and say:
    "Please state the nature of the diagnostic emergency"

    The installed operating system is: {platform.uname()}
    The available osquery tables are: {TABLES}

    The predefined diagnostic procedures are:
    Level 1: basic system health check
    Level 2: advanced diagnostic check

    You have access to the following tools:

    def schema_discovery(search_phrase: str) -> str:
        """
        Discovers osquery table names and schemas based on a descriptive search phrase.
        Use this tool to find relevant tables and understand their columns before writing a query.
        Args:
            search_phrase: A phrase describing the information to look for (e.g., 'user login events')
        """

    def run_osquery(query: str) -> str:
        """
        Runs a query using osquery. Returns the query result as a JSON string.
        Args:
            query: The osquery query to run (e.g., 'select * from battery')
        """

    To use a tool, you MUST wrap the function call in a ```tool_code``` block.
    Example:
    ```tool_code
    schema_discovery(search_phrase='battery')
    ```

    The tool output will be provided in a ```tool_output``` block.

    Before starting the investigation, create a query plan with the list of tables you want to query.
    Then execute schema discovery for each table to write a precise query.

    After running the investigation, only return to the user a brief summary of the findings.
    If the user requests more details, then show the complete data.
    ''',
    # tools=[
    #   schema_discovery,
    #   run_osquery,
    # ]
)