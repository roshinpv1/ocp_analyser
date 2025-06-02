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
    fetch_jira = FetchJiraStories()
    generate_report = GenerateReport()
    migration_insights = GenerateMigrationInsights()  # Add migration insights

    # Connect nodes in sequence
    fetch_repo >> analyze_code >> fetch_jira >> generate_report >> migration_insights

    # Create the flow starting with FetchRepo
    analysis_flow = Flow(start=fetch_repo)

    return analysis_flow

def create_excel_analysis_flow():
    """Creates and returns the codebase analysis flow that starts with Excel processing."""

    # Instantiate nodes
    process_excel = ProcessExcel(max_retries=3, wait=5)  # Add retry limit to Excel processing
    ocp_assessment = OcpAssessmentNode(max_retries=3, wait=10)
    fetch_repo = FetchRepo(max_retries=2, wait=5)  # Add retry limit to repo fetching
    analyze_code = AnalyzeCode(max_retries=5, wait=20)
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
    
    process_excel - "success" >> ocp_assessment  # Run OCP assessment on successful Excel processing
    
    # Connect OCP assessment to continue the normal flow
    ocp_assessment - "success" >> fetch_repo  # Use the "success" action returned by OcpAssessmentNode
    
    # Connect nodes in sequence for successful flow
    fetch_repo >> analyze_code >> fetch_jira >> generate_report >> migration_insights

    # Create the flow starting with ProcessExcel
    analysis_flow = Flow(start=process_excel)

    return analysis_flow

def create_analysis_flow():
    """Create and return the complete analysis flow."""
    
    # Create all the nodes
    start_node = StartAnalysis()
    preprocess_node = PreprocessCode()
    analyze_node = AnalyzeCodebase()
    excel_processor = ProcessExcelFormData()
    assessment_node = GenerateOCPAssessment()
    report_node = GenerateReport()
    migration_insights_node = GenerateMigrationInsights()  # New node
    
    # Create the flow connections
    start_node >> preprocess_node
    preprocess_node >> analyze_node
    analyze_node >> excel_processor
    excel_processor >> assessment_node
    assessment_node >> report_node
    report_node >> migration_insights_node  # Add migration insights after the main report
    
    return Flow(start=start_node)
