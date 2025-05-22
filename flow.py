from core.genflow import Flow
# Import all node classes from nodes.py
from nodes import (
    FetchRepo,
    AnalyzeCode,
    GenerateReport,
    ProcessExcel,
    FetchJiraStories
)

def create_analysis_flow():
    """Creates and returns the codebase analysis flow."""

    # Instantiate nodes
    fetch_repo = FetchRepo()
    analyze_code = AnalyzeCode(max_retries=5, wait=20)
    fetch_jira = FetchJiraStories()
    generate_report = GenerateReport()

    # Connect nodes in sequence
    fetch_repo >> analyze_code >> fetch_jira >> generate_report

    # Create the flow starting with FetchRepo
    analysis_flow = Flow(start=fetch_repo)

    return analysis_flow

def create_excel_analysis_flow():
    """Creates and returns the codebase analysis flow that starts with Excel processing."""

    # Instantiate nodes
    process_excel = ProcessExcel()
    fetch_repo = FetchRepo()
    analyze_code = AnalyzeCode(max_retries=5, wait=20)
    fetch_jira = FetchJiraStories()
    generate_report = GenerateReport()

    # Connect nodes in sequence
    process_excel >> fetch_repo >> analyze_code >> fetch_jira >> generate_report

    # Create the flow starting with ProcessExcel
    analysis_flow = Flow(start=process_excel)

    return analysis_flow
