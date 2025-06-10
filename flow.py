from core.genflow import Flow, Node
# Import all node classes from the modularized nodes package
from nodes import (
    FetchRepo,
    AnalyzeCode,
    GenerateReport,
    ProcessExcel,
    FetchJiraStories,
    OcpAssessmentNode
)
from nodes.reporting.migration_insights_generator import GenerateMigrationInsights

def create_analysis_flow():
    """Creates and returns the codebase analysis flow."""

    # Instantiate nodes
    fetch_repo = FetchRepo()
    analyze_code = AnalyzeCode(max_retries=5, wait=20)
    ocp_assessment = OcpAssessmentNode(max_retries=3, wait=10)  # Add OCP assessment to regular flow
    fetch_jira = FetchJiraStories()
    generate_report = GenerateReport()
    migration_insights = GenerateMigrationInsights()  # Add migration insights

    # Connect nodes in sequence - NOW INCLUDES OCP ASSESSMENT
    fetch_repo >> analyze_code >> ocp_assessment >> fetch_jira >> generate_report >> migration_insights

    # Create the flow starting with FetchRepo
    analysis_flow = Flow(start=fetch_repo)

    return analysis_flow

def create_excel_analysis_flow():
    """Creates and returns the codebase analysis flow that starts with Excel processing."""

    # Instantiate nodes
    process_excel = ProcessExcel(max_retries=3, wait=5)  # Add retry limit to Excel processing
    fetch_repo = FetchRepo(max_retries=2, wait=5)  # Add retry limit to repo fetching
    analyze_code = AnalyzeCode(max_retries=5, wait=20)
    ocp_assessment = OcpAssessmentNode(max_retries=3, wait=10)  # Move after code analysis
    fetch_jira = FetchJiraStories(max_retries=2, wait=5)  # Add retry limit to Jira fetching
    generate_report = GenerateReport(max_retries=2, wait=5)  # Add retry limit to report generation
    migration_insights = GenerateMigrationInsights(max_retries=2, wait=5)  # Add migration insights

    # Define additional actions for error handling
    # Remove the self-loop that could cause infinite retries
    # process_excel - "error" >> process_excel  # End the flow if Excel processing fails
    # Instead, we'll handle errors in the node itself using max_retries
    
    # Add a terminal node for unrecoverable errors
    class TerminalErrorNode(Node):
        def post(self, shared, prep_res, exec_res):
            print("\nERROR: Process terminated due to unrecoverable error.")
            return None  # No next action, end the flow
            
    terminal_error = TerminalErrorNode()
    
    # Connect the terminal error node
    process_excel - "terminal_error" >> terminal_error
    
    # NEW FLOW ORDER: ProcessExcel → FetchRepo → AnalyzeCode → OcpAssessment → Jira → Reports
    process_excel - "success" >> fetch_repo  # Run repo fetch on successful Excel processing
    
    # Connect the main analysis flow
    fetch_repo >> analyze_code >> ocp_assessment >> fetch_jira >> generate_report >> migration_insights

    # DEBUG: Print the flow connections to verify they're set up correctly
    print("=== DEBUG: Excel Analysis Flow Connections ===")
    print(f"ProcessExcel successors: {process_excel.successors}")
    print(f"FetchRepo successors: {fetch_repo.successors}")
    print(f"AnalyzeCode successors: {analyze_code.successors}")
    print(f"OcpAssessment successors: {ocp_assessment.successors}")
    print(f"FetchJira successors: {fetch_jira.successors}")
    print(f"GenerateReport successors: {generate_report.successors}")
    print(f"MigrationInsights successors: {migration_insights.successors}")
    print("=== END DEBUG ===")

    # Create the flow starting with ProcessExcel
    analysis_flow = Flow(start=process_excel)

    return analysis_flow
