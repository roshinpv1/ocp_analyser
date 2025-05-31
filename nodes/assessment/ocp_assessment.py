import os
import json
from openpyxl import load_workbook
from core.genflow import Node
from utils.call_llm import call_llm

class OcpAssessmentNode(Node):
    def prep(self, shared):
        print("\nDEBUG: Starting OcpAssessmentNode prep")
        
        # Get Excel validation data and set defaults if missing
        excel_validation = shared.get("excel_validation", {})
        
        # If no excel validation data, create basic entry
        if not excel_validation:
            print("WARNING: No Excel validation data found. Creating basic component entry.")
            excel_validation = {
                "component_name": shared.get("project_name", "Unknown Component"),
                "business_criticality": "Medium",
                "current_environment": "Unknown",
                "application_type": "Unknown"
            }
        
        # Get the project name for component identification
        project_name = shared.get("project_name", "Unknown Project")
        
        # Ensure component_name is set
        if "component_name" not in excel_validation:
            excel_validation["component_name"] = project_name
        
        # Get output directory
        output_dir = shared.get("output_dir", "analysis_output")
        
        # Get component analysis data for inclusion in assessment
        code_analysis = shared.get("code_analysis", {})
        component_analysis = code_analysis.get("component_analysis", {})
        excel_components = code_analysis.get("excel_components", {})
        
        print(f"DEBUG: Found {len(component_analysis)} detected components")
        print(f"DEBUG: Found {len(excel_components)} Excel component declarations")
        
        return excel_validation, output_dir, component_analysis, excel_components

    def exec(self, prep_res):
        excel_data, output_dir, component_analysis, excel_components = prep_res
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
8. COMPONENT ANALYSIS - Include a comprehensive component analysis section that:
- Compares components declared in the intake form with components actually detected in the codebase
- Creates a detailed table with columns: Component | Declared | Detected | Status
- Shows "Match" when both Declared and Detected are the same (Yes=Yes OR No=No)
- Shows "Mismatch" when Declared and Detected are different (Yes≠No OR No≠Yes)
- CRITICAL COMPONENT MATCHING LOGIC:
  * When Declared="Yes" AND Detected="Yes" → Status="Match"
  * When Declared="No" AND Detected="No" → Status="Match"  
  * When Declared="Yes" AND Detected="No" → Status="Mismatch"
  * When Declared="No" AND Detected="Yes" → Status="Mismatch"
- Lists all predefined components from the intake form including:
  venafi, redis, channel secure/pingfed, nas/smb, smtp, autosys, mtls/mutual auth, ndm, legacy jks file, 
  soap calls, rest api, apigee, kafka, ibm mq, mq cipher suite, ldap, splunk, appd, elastic apm, 
  harness/ucd for ci cd, hardrock/mtls auth, appdynamics, rabbitmq, database, mongodb, sqlserver, 
  mysql, postgresql, oracle, cassandra, couchbase, neo4j, hadoop, spark, okta, saml, auth, jwt, 
  openid, adfs, san, malwarescanner, any other service
- Use "Yes/No" values for Declared and Detected columns
- Provide clear status indicators for matches and mismatches

The output must be formatted as a structured assessment report with clear sections, using tables where appropriate for comparative data. Do not extrapolate any data - be specific to display if the OpenShift assessment is successful or not successful with required scoring (0-100 scale with detailed rubric) and specific recommendations/reasons. Include an Summary with go/no-go recommendation, followed by detailed technical sections including the Component Analysis section.

Each finding must include evidence from the intake data and reference to relevant OpenShift constraints or requirements.

IMPORTANT: Do not return any Jinja2 template syntax like '{{% for %}}', '{{ variable }}', etc. Return final HTML content with actual values, not templates.

IMPORTANT: If both values are the same (both Yes or both No), it's always a MATCH!"""
        
        # Get component analysis data from shared state if available
        component_analysis_data = ""
        
        if excel_components and component_analysis:
            component_analysis_data = "\n\nCOMPONENT ANALYSIS DATA:\n"
            component_analysis_data += "Excel Component Declarations:\n"
            for comp_name, comp_data in excel_components.items():
                declared = "Yes" if comp_data.get("is_yes", False) else "No"
                component_analysis_data += f"- {comp_name}: Declared = {declared}\n"
            
            component_analysis_data += "\nDetected Components in Codebase:\n"
            for comp_name, comp_data in component_analysis.items():
                detected = comp_data.get("detected", "no")
                evidence = comp_data.get("evidence", "No evidence")
                component_analysis_data += f"- {comp_name}: Detected = {detected} (Evidence: {evidence[:100]}...)\n"
        
        # Instruct the LLM to return content suitable for HTML embedding, not a full HTML document
        user_content = f"""Perform the OCP intake assessment for the following data and generate the assessment report content (HTML compatible):

{json.dumps(excel_data, indent=2)}

{component_analysis_data}

IMPORTANT REQUIREMENTS:
1. DO NOT return a full HTML document with <html>, <head>, or <body> tags.
2. DO NOT use any Jinja2 template syntax like '{{% for %}}', '{{ variable }}', etc. 
3. DO NOT wrap your response in markdown code blocks like ```html or ```
4. Return only clean HTML content that would go inside a <div>, with proper HTML formatting.
5. Use <div>, <h1>, <h2>, <p>, <table>, etc. elements to structure your report.
6. Return FINAL HTML with actual values, not templates or code examples.
7. Use proper CSS classes for styling compatibility with our report system.
8. MUST include a "Component Analysis" section with the following table format:
   <h2>Component Analysis</h2>
   <p>The following table compares the components declared in the intake form with the components detected in the codebase:</p>
   <table>
   <tr><th>Component</th><th>Declared</th><th>Detected</th><th>Status</th></tr>
   <tr><td>venafi</td><td>No</td><td>No</td><td>Match</td></tr>
   <tr><td>redis</td><td>Yes</td><td>Yes</td><td>Match</td></tr>
   ... (continue for all components listed in the system prompt)
   </table>

CRITICAL COMPONENT MATCHING LOGIC:
- When Declared="Yes" AND Detected="Yes" → Status="Match"
- When Declared="No" AND Detected="No" → Status="Match"
- When Declared="Yes" AND Detected="No" → Status="Mismatch"
- When Declared="No" AND Detected="Yes" → Status="Mismatch"

IMPORTANT: If both values are the same (both Yes or both No), it's always a MATCH!

CRITICAL: Your response should start directly with HTML tags like <div> or <h1>, NOT with ```html or any markdown formatting."""
        
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
            
            # Clean up the response to remove any markdown code blocks or nested HTML
            import re
            
            # Remove markdown code blocks if present
            if '```html' in response:
                print("DEBUG: Removing markdown code blocks from LLM response")
                response = re.sub(r'```html\s*', '', response)
                response = re.sub(r'```\s*$', '', response, flags=re.MULTILINE)
            
            # Remove any nested HTML document structure if present
            if '<!DOCTYPE html>' in response:
                print("DEBUG: Removing nested HTML document structure")
                # Extract content between <body> tags if present
                body_match = re.search(r'<body[^>]*>(.*?)</body>', response, re.DOTALL | re.IGNORECASE)
                if body_match:
                    response = body_match.group(1)
                else:
                    # If no body tags, try to extract content after first <div> or <h1>
                    content_match = re.search(r'(<(?:div|h1)[^>]*>.*)', response, re.DOTALL | re.IGNORECASE)
                    if content_match:
                        response = content_match.group(1)
            
            # Clean up any remaining unwanted tags
            response = re.sub(r'</?html[^>]*>', '', response, flags=re.IGNORECASE)
            response = re.sub(r'</?head[^>]*>.*?</head>', '', response, flags=re.DOTALL | re.IGNORECASE)
            response = re.sub(r'<style[^>]*>.*?</style>', '', response, flags=re.DOTALL | re.IGNORECASE)
            
            # Ensure the response is properly formatted
            response = response.strip()
            
            print(f"DEBUG: Cleaned response length: {len(response)} characters")
            
            # Use the same styling as the main analysis report for consistency
            css_styles = """
body {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 40px 20px;
    color: #374151;
    max-width: 900px;
    margin: 0 auto;
    background: #f3f4f6;
}

h1 {
    font-size: 2em;
    font-weight: 600;
    margin: 0 0 30px 0;
    color: #1f2937;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 15px;
}

h2 {
    font-size: 1.4em;
    font-weight: 600;
    margin: 40px 0 15px 0;
    color: #1f2937;
}

h3 {
    font-size: 1.1em;
    font-weight: 600;
    margin: 25px 0 10px 0;
    color: #374151;
}

h4 {
    font-size: 1em;
    font-weight: 500;
    margin: 15px 0 8px 0;
    color: #6b7280;
}

p {
    margin: 0 0 15px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    border: 1px solid #e5e7eb;
}

th {
    background: #2563eb;
    color: #fff;
    font-weight: 600;
    padding: 16px 20px;
    text-align: left;
    font-size: 0.875em;
    border: none;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

td {
    padding: 12px 20px;
    border-bottom: 1px solid #f3f4f6;
    font-size: 0.875em;
    border: none;
    color: #374151;
}

tr:last-child td {
    border-bottom: none;
}

tbody tr:nth-child(even) {
    background: #f9fafb;
}

tbody tr:nth-child(odd) {
    background: #fff;
}

tbody tr:hover {
    background: #eff6ff !important;
    transition: background-color 0.15s ease;
}

td:first-child {
    background: #f8fafc !important;
    font-weight: 600;
    color: #1f2937;
}

tbody tr:hover td:first-child {
    background: #e0f2fe !important;
}

.critical { 
    color: #dc2626; 
    font-weight: 600;
    background: #fef2f2;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}
.high { 
    color: #d97706; 
    font-weight: 600;
    background: #fffbeb;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}
.medium { 
    color: #2563eb; 
    font-weight: 600;
    background: #eff6ff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}
.low { 
    color: #059669;
    font-weight: 600;
    background: #ecfdf5;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
}

.score-high { 
    color: #059669;
    font-weight: 600;
    background: #ecfdf5;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
}
.score-medium { 
    color: #d97706; 
    font-weight: 600;
    background: #fffbeb;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}
.score-low { 
    color: #dc2626; 
    font-weight: 600;
    background: #fef2f2;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}

.executive-summary, .section {
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    margin-bottom: 25px;
    border: 1px solid #e5e7eb;
}

.finding {
    padding: 16px 20px;
    margin: 15px 0;
    border-left: 4px solid #e5e7eb;
    background-color: #f9fafb;
    border-radius: 0 8px 8px 0;
}
.finding.critical { border-left-color: #dc2626; }
.finding.high { border-left-color: #d97706; }
.finding.medium { border-left-color: #2563eb; }
.finding.low { border-left-color: #059669; }

.action-item {
    padding: 16px 20px;
    margin: 15px 0;
    border-left: 4px solid #e5e7eb;
    background-color: #f9fafb;
    border-radius: 0 8px 8px 0;
}
.action-item.critical { border-left-color: #dc2626; }
.action-item.high { border-left-color: #d97706; }
.action-item.medium { border-left-color: #2563eb; }
.action-item.low { border-left-color: #059669; }
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