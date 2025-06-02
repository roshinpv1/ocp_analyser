import os
import json
from datetime import datetime
from core.genflow import Node
from utils.call_llm import call_llm

class GenerateMigrationInsights(Node):
    def prep(self, shared):
        print("\nDEBUG: Starting GenerateMigrationInsights prep")
        
        # Get existing analysis data
        analysis = shared.get("code_analysis", {})
        
        # Get existing reports content if available
        hard_gate_assessment = shared.get("hard_gate_assessment", {})
        intake_assessment_content = None
        
        # Try to read intake assessment content if it exists
        if "intake_assessment_html" in shared and os.path.exists(shared["intake_assessment_html"]):
            try:
                with open(shared["intake_assessment_html"], 'r', encoding='utf-8') as f:
                    intake_assessment_content = f.read()
            except Exception as e:
                print(f"Warning: Could not read intake assessment file: {str(e)}")
        
        # Get project metadata
        project_name = shared.get("project_name", "Unknown Project")
        output_dir = shared.get("output_dir", "analysis_output")
        
        # Extract key information for migration analysis
        technology_stack = analysis.get("technology_stack", {})
        security_quality_analysis = analysis.get("security_quality_analysis", {})
        findings = analysis.get("findings", [])
        component_analysis = analysis.get("component_analysis", {})
        excel_components = analysis.get("excel_components", {})
        
        # Get files data for environment analysis
        files_data = shared.get("files_data", {})
        
        return {
            "project_name": project_name,
            "output_dir": output_dir,
            "technology_stack": technology_stack,
            "security_quality_analysis": security_quality_analysis,
            "findings": findings,
            "component_analysis": component_analysis,
            "excel_components": excel_components,
            "files_data": files_data,
            "hard_gate_assessment": hard_gate_assessment,
            "intake_assessment_content": intake_assessment_content
        }

    def exec(self, prep_data):
        print("\nDEBUG: Starting GenerateMigrationInsights exec")
        
        # Create comprehensive analysis summary for LLM
        analysis_summary = self._create_analysis_summary(prep_data)
        
        # System prompt for migration insights
        system_prompt = """You are an OpenShift migration readiness and insights agent, designed to provide readiness checklist and insights to migrate application components to OpenShift platform from existing TAS or TKGI environments.

Your primary functions are:
1. Parse intake forms submitted as Excel documents, extracting all relevant application metadata including
   - Current hosting environment details and configurations
   - Application dependencies and integration points
   - Current resource utilization metrics and patterns

2. Identify source platforms (TAS, TKGI, on-prem VM, traditional servers) and their specific characteristics:
   - Operating system details and version compatibility
   - Current technology used to develop the application like Java, .NET, python, ReactJS, AngularJS etc
   - Middleware components and their OpenShift equivalence dependencies
   - External service dependencies and communication patterns
   - Current deployment and operational procedures
   - Existing monitoring and logging mechanisms

3. Perform comprehensive intake form analysis to:
   - Provide the application readiness checklist to migrate application component from TAS/TKGI to OpenShift
   - Provide the insights that will help migration team to do application migration to openshift platform

4. Generate structured assessment reports that include:
   - Application readiness details to help centralized team to perform application migration
   - Provide the insights that will help migration team to do application migration to openshift platform

CRITICAL OUTPUT REQUIREMENTS:
- Generate a COMPLETE HTML document with proper DOCTYPE, head, and body sections
- Include the full CSS styling for professional presentation
- Use the exact same blue theme (#2563eb) as the intake assessment reports
- Return final HTML content ready for saving to file, not content fragments"""

        # Create user prompt with analysis data
        user_prompt = f"""Based on the comprehensive code analysis and assessment data provided below, generate a complete OpenShift migration insights HTML report for the application component.

ANALYSIS DATA:
{analysis_summary}

CRITICAL HTML DOCUMENT REQUIREMENTS:
1. Generate a COMPLETE HTML document starting with <!DOCTYPE html>
2. Include <html>, <head>, and <body> tags with proper structure
3. Add complete CSS styling in <style> tags within <head>
4. Use the professional blue theme (#2563eb) throughout
5. Set title as "OpenShift Migration Insights - {prep_data['project_name']}"

EXACT CSS CLASSES TO USE:
- For status indicators: <span class="status-implemented">, <span class="status-partial">, <span class="status-not-implemented">
- For priority levels: <span class="priority-critical">, <span class="priority-high">, <span class="priority-medium">
- For Go/No-Go status: <div class="go-status go"> or <div class="go-status no-go">
- For checklists: <ul class="checklist">

REQUIRED HTML STRUCTURE WITH COMPLETE CSS:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenShift Migration Insights - {prep_data['project_name']}</title>
    <style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
        margin: 0;
        padding: 40px 20px;
        color: #374151;
        max-width: 900px;
        margin: 0 auto;
        background: #f3f4f6;
    }}
    h1 {{
        font-size: 2em;
        font-weight: 600;
        margin: 0 0 30px 0;
        color: #1f2937;
        border-bottom: 3px solid #2563eb;
        padding-bottom: 15px;
    }}
    h2 {{
        font-size: 1.4em;
        font-weight: 600;
        margin: 40px 0 15px 0;
        color: #1f2937;
    }}
    h3 {{
        font-size: 1.1em;
        font-weight: 600;
        margin: 25px 0 10px 0;
        color: #374151;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: #fff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
    }}
    th {{
        background: #2563eb;
        color: #fff;
        font-weight: 600;
        padding: 16px 20px;
        text-align: left;
        font-size: 0.875em;
        border: none;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    td {{
        padding: 12px 20px;
        border-bottom: 1px solid #f3f4f6;
        font-size: 0.875em;
        border: none;
        color: #374151;
    }}
    tbody tr:nth-child(even) {{ background: #f9fafb; }}
    tbody tr:nth-child(odd) {{ background: #fff; }}
    tbody tr:hover {{ background: #eff6ff !important; }}
    td:first-child {{
        background: #f8fafc !important;
        font-weight: 600;
        color: #1f2937;
    }}
    .status-implemented {{ 
        color: #059669;
        font-weight: 600;
        background: #ecfdf5;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75em;
    }}
    .status-partial {{ 
        color: #d97706;
        font-weight: 600;
        background: #fffbeb;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75em;
    }}
    .status-not-implemented {{ 
        color: #dc2626;
        font-weight: 600;
        background: #fef2f2;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75em;
    }}
    .priority-critical {{ 
        color: #dc2626; 
        font-weight: 600;
        background: #fef2f2;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75em;
    }}
    .priority-high {{ 
        color: #d97706; 
        font-weight: 600;
        background: #fffbeb;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75em;
    }}
    .priority-medium {{ 
        color: #2563eb; 
        font-weight: 600;
        background: #eff6ff;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.75em;
    }}
    .go-status {{
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        text-align: center;
        display: inline-block;
        margin: 10px 0;
    }}
    .go {{
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }}
    .no-go {{
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fca5a5;
    }}
    .checklist {{
        list-style-type: none;
        padding: 0;
    }}
    .checklist li {{
        padding: 8px 0;
        border-bottom: 1px solid #f3f4f6;
    }}
    .checklist li:before {{
        content: "✓ ";
        color: #059669;
        font-weight: bold;
        margin-right: 10px;
    }}
    .executive-summary {{
        background-color: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 25px;
        border: 1px solid #e5e7eb;
    }}
    p {{ margin: 0 0 15px 0; }}
    ul, ol {{ margin: 0 0 15px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>OpenShift Migration Insights for {prep_data['project_name']}</h1>
    <div class="executive-summary">
        [REPORT CONTENT HERE]
    </div>
</body>
</html>
```

REPORT CONTENT SECTIONS (Required in this order):
1. <h2>Intake Overview</h2>
   - Application component name with <h3><strong>Name</strong></h3>
   - Basic application details in <p> tags
   - Migration status: <div class="go-status [go|no-go]">Go/No Go</div>

2. <h2>General Information</h2>
   - Component metadata in proper table format

3. <h2>Application Component Details</h2>
   - Technology stack table with status indicators

4. <h2>Service Bindings and Dependencies</h2>
   - Dependencies analysis table

5. <h2>OpenShift Migration Readiness Checklist</h2>
   - Use: <ul class="checklist"> for checklist items

6. <h2>Migration Insights and Recommendations</h2>
   - Key recommendations with priority indicators
   - Next steps as ordered list

CRITICAL: Generate a COMPLETE, SELF-CONTAINED HTML document that can be saved directly to a file and opened in a browser with all styling intact. DO NOT generate content fragments."""

        try:
            # Generate complete migration insights HTML document
            combined_prompt = f"{system_prompt}\n\n=== USER REQUEST ===\n{user_prompt}"
            
            migration_report = call_llm(combined_prompt)
            
            # Clean up any markdown artifacts
            if "```html" in migration_report:
                migration_report = migration_report.split("```html")[1].split("```")[0].strip()
            
            # Ensure we have a complete HTML document
            if not migration_report.strip().startswith("<!DOCTYPE"):
                print("DEBUG: LLM didn't generate complete HTML, wrapping content...")
                migration_report = self._wrap_in_html_structure(migration_report, prep_data["project_name"])
            
            return migration_report
            
        except Exception as e:
            print(f"Error generating migration insights: {str(e)}")
            # Generate fallback report with complete HTML structure
            return self._generate_fallback_report(prep_data)

    def _create_analysis_summary(self, data):
        """Create a comprehensive summary of analysis data for LLM processing."""
        summary = f"""
APPLICATION: {data['project_name']}

TECHNOLOGY STACK:
"""
        
        # Add technology stack information
        tech_stack = data.get('technology_stack', {})
        for category, technologies in tech_stack.items():
            summary += f"\n{category.upper()}:\n"
            if isinstance(technologies, list):
                for tech in technologies:
                    if isinstance(tech, dict):
                        name = tech.get('name', 'Unknown')
                        version = tech.get('version', 'Unknown')
                        purpose = tech.get('purpose', 'N/A')
                        summary += f"  - {name} (Version: {version}) - {purpose}\n"
                    else:
                        summary += f"  - {tech}\n"
            else:
                summary += f"  - {technologies}\n"
        
        # Add security and quality analysis
        security_analysis = data.get('security_quality_analysis', {})
        if security_analysis:
            summary += "\nSECURITY & QUALITY ANALYSIS:\n"
            for category, practices in security_analysis.items():
                summary += f"\n{category.upper()}:\n"
                for practice, details in practices.items():
                    if isinstance(details, dict):
                        implemented = details.get('implemented', 'no')
                        evidence = details.get('evidence', 'No evidence')
                        recommendation = details.get('recommendation', 'No recommendation')
                        summary += f"  - {practice}: {implemented} - {evidence} - {recommendation}\n"
        
        # Add findings
        findings = data.get('findings', [])
        if findings:
            summary += f"\nCODE ANALYSIS FINDINGS ({len(findings)} issues):\n"
            for finding in findings[:10]:  # Limit to first 10 findings
                severity = finding.get('severity', 'low')
                description = finding.get('description', 'No description')
                summary += f"  - {severity.upper()}: {description}\n"
        
        # Add component analysis
        component_analysis = data.get('component_analysis', {})
        if component_analysis:
            summary += "\nCOMPONENT ANALYSIS:\n"
            for component, details in component_analysis.items():
                summary += f"  - {component}: {details}\n"
        
        # Add file analysis summary
        files_data = data.get('files_data', {})
        if files_data:
            file_count = len(files_data)
            extensions = {}
            for filepath in files_data.keys():
                _, ext = os.path.splitext(filepath)
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
            
            summary += f"\nFILE ANALYSIS:\n"
            summary += f"  - Total files analyzed: {file_count}\n"
            summary += f"  - File types: {', '.join([f'{ext} ({count})' for ext, count in extensions.items()])}\n"
        
        return summary

    def _wrap_in_html_structure(self, content, project_name):
        """Wrap content in proper HTML structure if needed."""
        # Use the exact same CSS styles as the Hard Gate Assessment report for consistency
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

.status-implemented { 
    color: #059669;
    font-weight: 600;
    background: #ecfdf5;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
}
.status-partial { 
    color: #d97706;
    font-weight: 600;
    background: #fffbeb;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
}
.status-not-implemented { 
    color: #dc2626;
    font-weight: 600;
    background: #fef2f2;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75em;
}

p {
    margin: 0 0 15px 0;
}

ul, ol {
    margin: 0 0 15px 0;
    padding-left: 20px;
}

code {
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.8em;
    color: #2563eb;
    font-family: Monaco, Consolas, monospace;
    border: 1px solid #e2e8f0;
}

.priority-critical { 
    color: #dc2626; 
    font-weight: 600;
    background: #fef2f2;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}
.priority-high { 
    color: #d97706; 
    font-weight: 600;
    background: #fffbeb;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
}
.priority-medium { 
    color: #2563eb; 
    font-weight: 600;
    background: #eff6ff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.75em;
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

/* Migration-specific styling */
.go-status {
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: 600;
    text-align: center;
    display: inline-block;
    margin: 10px 0;
}

.go {
    background: #ecfdf5;
    color: #059669;
    border: 1px solid #a7f3d0;
}

.no-go {
    background: #fef2f2;
    color: #dc2626;
    border: 1px solid #fca5a5;
}

.checklist {
    list-style-type: none;
    padding: 0;
}

.checklist li {
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
}

.checklist li:before {
    content: "✓ ";
    color: #059669;
    font-weight: bold;
    margin-right: 10px;
}
"""
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenShift Migration Insights - {project_name}</title>
    <style>
    {css_styles}
    </style>
</head>
<body>
    <h1>OpenShift Migration Insights for {project_name}</h1>
    <div class="executive-summary">
        {content}
    </div>
</body>
</html>"""

    def _generate_fallback_report(self, data):
        """Generate a fallback report when LLM fails."""
        project_name = data['project_name']
        
        # Determine Go/No-Go status based on findings
        findings = data.get('findings', [])
        critical_issues = [f for f in findings if f.get('severity', '').lower() == 'critical']
        go_status = "No Go" if len(critical_issues) > 0 else "Go"
        go_class = "no-go" if go_status == "No Go" else "go"
        
        # Extract key technologies
        tech_stack = data.get('technology_stack', {})
        languages = tech_stack.get('languages', [])
        frameworks = tech_stack.get('frameworks', [])
        
        content = f"""
        <h2>Intake Overview</h2>
        <h3><strong>{project_name}</strong></h3>
        <p>This report provides OpenShift migration readiness assessment and insights for the application component.</p>
        
        <h3>Intake Status</h3>
        <div class="go-status {go_class}">{go_status}</div>
        {f'<p><strong>Reason:</strong> {len(critical_issues)} critical issues found that must be addressed before migration.</p>' if go_status == "No Go" else '<p><strong>Reason:</strong> No critical blockers identified for OpenShift migration.</p>'}
        
        <h2>General Information</h2>
        <table>
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Component Name</td>
                    <td><strong>{project_name}</strong></td>
                </tr>
                <tr>
                    <td>Assessment Date</td>
                    <td>{datetime.now().strftime('%B %d, %Y')}</td>
                </tr>
                <tr>
                    <td>Total Files Analyzed</td>
                    <td>{len(data.get('files_data', {}))}</td>
                </tr>
                <tr>
                    <td>Issues Found</td>
                    <td>{len(findings)}</td>
                </tr>
            </tbody>
        </table>
        
        <h2>Application Component Details</h2>
        
        <h3>Technology Stack</h3>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Technology</th>
                    <th>Version</th>
                    <th>OpenShift Compatibility</th>
                </tr>
            </thead>
            <tbody>
        """
        
        # Add technology details with proper HTML structure
        for lang in languages[:5]:  # Limit to 5 entries
            if isinstance(lang, dict):
                name = lang.get('name', 'Unknown')
                version = lang.get('version', 'Unknown')
                content += f"""
                <tr>
                    <td>Language</td>
                    <td>{name}</td>
                    <td>{version}</td>
                    <td><span class="status-implemented">Compatible</span></td>
                </tr>
                """
        
        for framework in frameworks[:5]:  # Limit to 5 entries
            if isinstance(framework, dict):
                name = framework.get('name', 'Unknown')
                version = framework.get('version', 'Unknown')
                content += f"""
                <tr>
                    <td>Framework</td>
                    <td>{name}</td>
                    <td>{version}</td>
                    <td><span class="status-partial">Review Required</span></td>
                </tr>
                """
        
        content += """
            </tbody>
        </table>
        
        <h2>Service Bindings and Dependencies</h2>
        <table>
            <thead>
                <tr>
                    <th>Dependency Type</th>
                    <th>Details</th>
                    <th>Migration Impact</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Database Dependencies</td>
                    <td>Analysis in progress</td>
                    <td><span class="status-partial">Review Required</span></td>
                </tr>
                <tr>
                    <td>External APIs</td>
                    <td>Evaluation needed</td>
                    <td><span class="status-partial">Review Required</span></td>
                </tr>
                <tr>
                    <td>File System Dependencies</td>
                    <td>Assessment pending</td>
                    <td><span class="status-partial">Review Required</span></td>
                </tr>
            </tbody>
        </table>
        
        <h2>OpenShift Migration Readiness Checklist</h2>
        <ul class="checklist">
            <li>Application technology stack assessment completed</li>
            <li>Dependencies identified and catalogued</li>
            <li>Security and quality analysis performed</li>
            <li>Code findings documented and prioritized</li>
            <li>Migration strategy recommendations provided</li>
        </ul>
        
        <h2>Migration Insights and Recommendations</h2>
        
        <h3>Key Recommendations</h3>
        <ul>
        """
        
        if critical_issues:
            content += f'<li><span class="priority-critical">Critical Priority:</span> Address {len(critical_issues)} critical issues before migration</li>'
        
        content += """
            <li><span class="priority-medium">Medium Priority:</span> Containerize application components using Docker/Podman</li>
            <li><span class="priority-medium">Medium Priority:</span> Review and update configuration management for OpenShift environment</li>
            <li><span class="priority-high">High Priority:</span> Implement health checks and readiness probes</li>
            <li><span class="priority-medium">Medium Priority:</span> Plan for persistent storage requirements</li>
            <li><span class="priority-high">High Priority:</span> Update CI/CD pipelines for OpenShift deployment</li>
        </ul>
        
        <h3>Next Steps</h3>
        <ol>
            <li>Review detailed findings and address critical issues</li>
            <li>Create containerization strategy</li>
            <li>Design OpenShift deployment architecture</li>
            <li>Plan migration timeline and resource allocation</li>
            <li>Execute pilot migration with small subset</li>
        </ol>
        """
        
        return self._wrap_in_html_structure(content, project_name)

    def post(self, shared, prep_res, exec_res):
        """Save the migration insights report."""
        output_dir = prep_res["output_dir"]
        project_name = prep_res["project_name"]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the migration insights report
        migration_insights_path = os.path.join(output_dir, "migration_insights.html")
        
        try:
            with open(migration_insights_path, "w", encoding="utf-8") as f:
                f.write(exec_res)
            
            print(f"Migration insights report generated: {migration_insights_path}")
            
            # Store the path in shared state
            shared["migration_insights_html"] = migration_insights_path
            
            # Always create markdown version for consistency with other reports
            try:
                # Extract text content for storage
                import re
                text_content = re.sub(r'<[^>]*>', ' ', exec_res)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                # Create markdown content for better storage
                markdown_content = f"# OpenShift Migration Insights for {project_name}\n\n{text_content}"
                
                # Save markdown version
                markdown_path = os.path.join(output_dir, "migration_insights.md")
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                print(f"Migration insights markdown saved: {markdown_path}")
                shared["migration_insights_md"] = markdown_path
                
            except Exception as e:
                print(f"Warning: Could not create markdown version: {str(e)}")
            
            # Also try to store in ChromaDB if available
            try:
                from utils.chromadb_wrapper import get_chromadb_wrapper
                
                wrapper = get_chromadb_wrapper()
                if wrapper.is_enabled() and 'markdown_path' in locals():
                    # Store in ChromaDB with custom collection or use existing one
                    success = wrapper.store_analysis_report(f"{project_name}_migration_insights", markdown_path)
                    if success:
                        print("Stored migration insights in ChromaDB successfully")
                
            except Exception as e:
                print(f"Warning: Could not store migration insights in ChromaDB: {str(e)}")
            
            return "default"
            
        except Exception as e:
            print(f"Error saving migration insights report: {str(e)}")
            return "error" 