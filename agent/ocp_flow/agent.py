from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import subprocess
from google.adk.tools import FunctionTool
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Now we can import from utils
from utils.chromadb_wrapper import get_chromadb_wrapper

   
import subprocess


def query_report(query : str) :
    try:
        # Use configurable ChromaDB wrapper
        wrapper = get_chromadb_wrapper()
        
        if not wrapper.is_enabled():
            return {"code_analysis": [], "assessment": []}
        
        hard_gates = wrapper.search_analysis_reports(query, n_results=1)
        assessment = wrapper.search_ocp_assessments(query, n_results=1)

        print(hard_gates)
       
        return {"code_analysis": hard_gates, "assessment": assessment}
    except Exception as e:
        print(f"Error querying reports: {str(e)}")
        return {"code_analysis": [], "assessment": []}
 



root_agent = Agent(
    model=LiteLlm(model="gpt-3.5-turbo", base_url="http://localhost:1234/v1", api_key="sdsd", provider="openai"),
    name='ocp_flow',
    instruction = """
    You are a helpful AI assistant specialized in OCP migration assessments. You can respond to user queries based on analyzed report data stored in ChromaDB. 

    If a user requests to execute a report analysis or process migration-related findings, you are allowed to trigger the appropriate tool, such as `query_report`. When the user asks to analyze the report or initiate a migration assessment, run the tool accordingly and return structured insights.

    You are expected to:
    - Understand and explain the migration assessment report.
    - Identify gaps, findings, recommendations, and summaries.
    - Execute analysis tools on demand.
    """,

    description = """
    This AI assistant interacts with structured assessment data fetched from ChromaDB. It helps users understand critical aspects of an OCP migration report, such as:

    **Key Features of Report Content:**

    1. **Executive Summary**
    - Shows implementation status of Security & Quality best practices.
    - Indicates overall findings and areas not yet implemented.

    2. **Component Analysis**
    - Matches declared vs detected components (e.g., Redis, Kafka, LDAP).
    - Useful to verify system inventory accuracy.

    3. **Technology Stack**
    - Lists languages, frameworks, libraries, databases, and infrastructure.
    - Example: Python 3.12, Apify framework, Docker containers, JSON data store.

    4. **Security & Quality Analysis**
    - Details auditability, availability, error handling, monitoring, and testing.
    - Marks each practice as implemented or not and gives recommendations.
    - Example practices: Avoid Logging Confidential Data, Retry Logic, Automated Testing.

    5. **Findings**
    - Lists potential gaps or issues discovered in the system.
    - If no findings are present, confirms codebase compliance.

    6. **Action Items**
    - Prioritized remediation tasks such as improving logging, error handling, and resilience.

    7. **Jira Integration**
    - Displays linked Jira stories with status, descriptions, comments, and attachments.
    - Helps trace planned and ongoing fixes related to the report.

    **Agent Capabilities:**
    - Summarize insights and answer technical questions from the report.
    - Provide actionable recommendations for migration readiness.
    - Trigger report querying or analysis tools like `query_report` on request.
    """,
    tools=[query_report]
)





