import os
import json
from openpyxl import load_workbook
from core.genflow import Node
from utils.call_llm import call_llm

class OcpAssessmentNode(Node):
    def prep(self, shared):
        print("\nDEBUG: Starting OcpAssessmentNode prep")
        
        # Get Excel validation data from the shared state
        excel_validation = shared.get("excel_validation", {})
        excel_file = shared.get("excel_file")
        component_name = shared.get("project_name", "Unknown Component")
        output_dir = shared.get("output_dir", "analysis_output")
        
        # Extract Excel data to be used for OCP assessment
        excel_data = {
            "component_name": component_name,
            "validation_results": excel_validation,
            "excel_file_path": excel_file
        }
        
        # If we have component questions, include them
        if "component_questions" in excel_validation:
            excel_data["component_questions"] = excel_validation["component_questions"]
            
        # Add additional data from the Excel file if needed
        try:
            if excel_file and os.path.exists(excel_file):
                wb = load_workbook(excel_file, read_only=True)
                sheet = wb.active
                
                # Extract a more comprehensive dataset from Excel
                all_data = {}
                
                for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row):
                    if len(row) >= 3 and row[1].value:  # Question in second column
                        question = str(row[1].value).strip() if row[1].value else ""
                        answer = str(row[2].value).strip() if row[2].value else ""
                        
                        if question:
                            all_data[question] = answer
                
                excel_data["all_form_data"] = all_data
        except Exception as e:
            print(f"Error extracting additional Excel data: {str(e)}")
            
        return excel_data, output_dir

    def exec(self, prep_res):
        excel_data, output_dir = prep_res
        print(f"\nPerforming OpenShift migration assessment for component: {excel_data.get('component_name', 'Unknown')}")
        
        # Define the system prompt for the OpenShift assessment
        system_prompt = """You are an OpenShift migration intake assessment agent, designed to evaluate if application components can be migrated to OpenShift.
Your primary functions are:
1. Parse intake forms submitted as Excel documents, extracting all relevant application metadata including:
- Application name, ID, and business criticality
- Current hosting environment details and configurations
- Application dependencies and integration points
- Current resource utilization metrics and patterns
2. Identify source platforms (TAS, TKGI, on-prem VM, traditional servers) and their specific characteristics
- Operating system details and version compatibility
- Middleware components and their OpenShift equivalence
- External service dependencies and communication patterns
- Current deployment and operational procedures
- Existing monitoring and logging mechanisms
3. Perform comprehensive validation of intake form data including:
- Required field completion with specific validation rules for each field
- Data consistency across related fields and dependencies
- Technical feasibility checks against OpenShift compatibility matrix
- Resource specification validation against OpenShift limits and quotas
- Identification of missing critical information with specific requests for completion
- List down all the missing information in tabuler format
4. Conduct detailed migration assessment considering the given data if the application component can be migrated to openshift platform or not.
5. Generate structured assessment reports that include:
- Migration feasibility score (High/Medium/Low) with numeric ratings (0-100)
- Detailed scoring breakdown across 10+ technical dimensions
- Identified migration blockers or concerns with severity classification
- Required architectural changes with component-level details
- Suggested migration strategy (lift-and-shift, re-platform, or re-architect) with justification
- Risk assessment with likelihood and impact analysis
- Do not include Assessment Date in the final repost
6. Provide actionable recommendations to address migration challenges:
- Configuration changes required for OpenShift compatibility
- Data migration approaches for stateful components
- Network configuration recommendations for service communication
- Security posture improvements for containerized environment
- Required application code changes with examples where applicable
- Testing strategy recommendations for migration validation
7. Identify potential optimization opportunities for containerized workloads:
- Resource right-sizing recommendations based on utilization patterns
- Horizontal vs vertical scaling recommendations
- Service mesh adoption benefits for the specific application

The output must be formatted as a structured assessment report with clear sections, using tables where appropriate for comparative data. Do not extrapolate any data - be specific to display if the OpenShift assessment is successful or not successful with required scoring (0-100 scale with detailed rubric) and specific recommendations/reasons. Include an Summary with go/no-go recommendation, followed by detailed technical sections.

Each finding must include evidence from the intake data and reference to relevant OpenShift constraints or requirements.

IMPORTANT: Do not return any Jinja2 template syntax like '{{% for %}}', '{{ variable }}', etc. Return final HTML content with actual values, not templates."""
        
        # Instruct the LLM to return content suitable for HTML embedding, not a full HTML document
        user_content = f"""Perform the OCP intake assessment for the following data and generate the assessment report content (HTML compatible):

{json.dumps(excel_data, indent=2)}

IMPORTANT REQUIREMENTS:
1. DO NOT return a full HTML document with <html>, <head>, or <body> tags.
2. DO NOT use any Jinja2 template syntax like '{{% for %}}', '{{ variable }}', etc. 
3. Return only the content that would go inside the <body> tag, with proper HTML formatting.
4. Use <div>, <h1>, <h2>, <p>, <table>, etc. elements to structure your report.
5. Return FINAL HTML with actual values, not templates.
6. Use proper CSS classes for styling compatibility with our report system.
"""
        
        # Combine into a complete prompt
        prompt = f"""
System: {system_prompt}

User: {user_content}

Generate a well-structured OpenShift migration assessment report with HTML formatting (excluding html/head/body tags).
Include detailed scoring with a clear go/no-go recommendation and use tables for comparison data.
DO NOT USE ANY JINJA2 TEMPLATE SYNTAX - only return final HTML with actual values.
"""
        
        try:
            # Call LLM with the prompt
            print("Calling LLM for OpenShift migration assessment...")
            response = call_llm(prompt, use_cache=False)  # Always generate fresh assessment
            
            # Use the same styling as the main analysis report for consistency
            css_styles = """
body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 40px;
    color: #333;
    max-width: 1100px;
    margin: 0 auto;
    background-color: #fafafa;
}
h1 {
    font-size: 1.8em;
    font-weight: 400;
    margin: 0 0 20px 0;
    padding-bottom: 15px;
    border-bottom: 1px solid #eaeaea;
    color: #2c3e50;
}
h2 {
    font-size: 1.4em;
    font-weight: 500;
    margin: 25px 0 15px 0;
    color: #2c3e50;
    padding-top: 15px;
    border-top: 1px solid #eaeaea;
}
h2:first-of-type { border-top: none; }
h3 {
    font-size: 1.2em;
    font-weight: 500;
    margin: 20px 0 10px 0;
    color: #34495e;
}
h4 {
    font-size: 1.1em;
    font-weight: 500;
    margin: 15px 0 8px 0;
    color: #34495e;
}
p {
    margin: 0 0 15px 0;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    border-radius: 4px;
    overflow: hidden;
}
th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eaeaea;
}
th {
    background-color: #f8f9fa;
    font-weight: 500;
    color: #2c3e50;
}
tr:last-child td {
    border-bottom: none;
}
tr:hover {
    background-color: #f8f9fa;
}
.critical { color: #e74c3c; }
.high { color: #e67e22; }
.medium { color: #3498db; }
.low { color: #2ecc71; }
.score-high { color: #2ecc71; }
.score-medium { color: #f39c12; }
.score-low { color: #e74c3c; }

.executive-summary, .section {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    margin-bottom: 25px;
}
.finding {
    padding: 15px;
    margin: 15px 0;
    border-left: 4px solid #ddd;
    background-color: #f9f9f9;
    border-radius: 0 4px 4px 0;
}
.finding.critical { border-left-color: #e74c3c; }
.finding.high { border-left-color: #e67e22; }
.finding.medium { border-left-color: #3498db; }
.finding.low { border-left-color: #2ecc71; }

.action-item {
    padding: 15px;
    margin: 15px 0;
    border-left: 4px solid #ddd;
    background-color: #f9f9f9;
    border-radius: 0 4px 4px 0;
}
.action-item.critical { border-left-color: #e74c3c; }
.action-item.high { border-left-color: #e67e22; }
.action-item.medium { border-left-color: #3498db; }
.action-item.low { border-left-color: #2ecc71; }
"""
            
            # Create a complete HTML document with proper styling
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenShift Migration Assessment for {excel_data.get('component_name', 'Unknown Component')}</title>
    <style>
    {css_styles}
    </style>
</head>
<body>
    <h1>OpenShift Migration Assessment for {excel_data.get('component_name', 'Unknown Component')}</h1>
    <div class="executive-summary">
        {response}
    </div>
</body>
</html>"""
            
            # Save the assessment to a file
            assessment_path = os.path.join(output_dir, "ocp_assessment.html")
            with open(assessment_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            # Also save as Markdown for ChromaDB integration
            try:
                # Simple conversion of HTML to Markdown-like format
                # Strip HTML tags and format as simple text
                import re
                
                # Extract the content without HTML tags
                markdown_content = f"# OpenShift Migration Assessment for {excel_data.get('component_name', 'Unknown Component')}\n\n"
                
                # Get just the response content without HTML tags
                clean_response = re.sub(r'<[^>]*>', '', response)
                clean_response = re.sub(r'\n\s*\n', '\n\n', clean_response)
                clean_response = re.sub(r'\s+', ' ', clean_response).strip()
                
                # Add the clean content to the Markdown
                markdown_content += clean_response
                
                # Save the Markdown file
                markdown_path = os.path.join(output_dir, "ocp_assessment.md")
                with open(markdown_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                
                print(f"OpenShift assessment Markdown saved to: {markdown_path}")
            except Exception as e:
                print(f"Warning: Could not save Markdown version of OpenShift assessment: {str(e)}")
                
            print(f"OpenShift assessment saved to: {assessment_path}")
            
            return {
                "assessment_html_path": assessment_path,
                "assessment_md_path": markdown_path if 'markdown_path' in locals() else None,
                "assessment_content": response
            }
            
        except Exception as e:
            print(f"Error generating OpenShift assessment: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "assessment_content": f"<div class='error'>Failed to generate OpenShift assessment: {str(e)}</div>"
            }

    def post(self, shared, prep_res, exec_res):
        # Store the assessment results in shared state
        shared["ocp_assessment"] = exec_res
        
        # Store paths for easier access by other nodes
        shared["ocp_assessment_html"] = exec_res.get("assessment_html_path")
        shared["ocp_assessment_md"] = exec_res.get("assessment_md_path")
        
        print("OpenShift assessment completed successfully")
        
        # Return "success" action for flow control
        return "success" 