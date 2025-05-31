import os
import re
from core.genflow import Node

class GenerateReport(Node):
    def prep(self, shared):
        print("\nDEBUG: Starting GenerateReport prep")
        
        analysis = shared.get("code_analysis", {})
        
        # Check for empty analysis
        if not analysis:
            print("WARNING: No code analysis data found. Report will be limited.")
            # Initialize with empty values to avoid errors
            analysis = {
                "findings": [],
                "technology_stack": {},
                "component_analysis": {},
                "security_quality_analysis": {},
                "excel_components": {}
            }
        
        findings = analysis.get("findings", [])
        print(f"DEBUG: Number of findings: {len(findings)}")
        
        # Support both old and new technology formats
        if "technology_stack" in analysis:
            technology_stack = analysis["technology_stack"]
        else:
            technology_stack = analysis.get("technologies", {})
        
        # Get component analysis
        component_analysis = analysis.get("component_analysis", {})
        
        # Get Excel component declarations
        excel_components = analysis.get("excel_components", {})
        
        # Get security and quality analysis
        security_quality_analysis = analysis.get("security_quality_analysis", {})
        
        # Get Jira stories if available
        jira_stories = shared.get("jira_stories", [])
        print(f"DEBUG: Number of Jira stories: {len(jira_stories)}")
        
        project_name = shared.get("project_name", "Unknown Project")
        output_dir = shared.get("output_dir", "analysis_output")
        
        # Get Excel validation data if available
        excel_validation = shared.get("excel_validation", {})
        
        # Check if we have files data
        files_data = shared.get("files_data", {})
        file_count = len(files_data)
        print(f"DEBUG: Number of files analyzed: {file_count}")
        
        # Check for Excel folders in the files
        excel_extensions = {'.xlsx', '.xls', '.xlsm', '.xlsb', '.csv'}
        excel_folders = set()
        
        for file_path in files_data.keys():
            dir_path = os.path.dirname(file_path)
            dir_parts = dir_path.split(os.sep)
            for part in dir_parts:
                if any(part.lower().endswith(ext) for ext in excel_extensions):
                    excel_folders.add(part)
        
        if excel_folders:
            print(f"DEBUG: Report will include Excel folders: {', '.join(excel_folders)}")
        
        # Include file information in the report
        file_summary = {
            "count": file_count,
            "extensions": {},
            "excel_folders": list(excel_folders)
        }
        
        # Count file extensions
        for filepath in files_data.keys():
            _, ext = os.path.splitext(filepath)
            if ext:
                file_summary["extensions"][ext] = file_summary["extensions"].get(ext, 0) + 1
        
        return findings, technology_stack, project_name, output_dir, excel_validation, component_analysis, excel_components, security_quality_analysis, jira_stories, file_summary

    def exec(self, prep_res):
        findings, technology_stack, project_name, output_dir, excel_validation, component_analysis, excel_components, security_quality_analysis, jira_stories, file_summary = prep_res
        print("\nDEBUG: Starting GenerateReport exec")
        
        # Initialize report and html_content variables at the beginning of the method
        # Generate Markdown report content
        report = f"# Application & Platform Hard Gates for {project_name}\n\n"
        
        # Add Summary with statistics
        report += "## Summary\n\n"
        
        # Include file statistics
        report += f"📁 **Files Analyzed**: {file_summary['count']}\n"
        if file_summary['extensions']:
            report += "📂 **File Types**: "
            ext_counts = [f"{ext} ({count})" for ext, count in file_summary['extensions'].items()]
            report += ", ".join(ext_counts) + "\n"
        
        # Add Excel folder information if present
        if file_summary.get('excel_folders'):
            report += f"**Excel Folders**: {len(file_summary['excel_folders'])}\n"
            report += "  - " + ", ".join(file_summary['excel_folders']) + "\n"
        
        report += "\n"  # Add spacing
        
        # Calculate statistics for Hard Gates only
        hard_gate_stats = ""
        hard_gates_total = 0
        hard_gates_met = 0
        hard_gates_not_met = 0
        hard_gates_partial = 0
        
        if security_quality_analysis:
            categories_total = 0
            categories_implemented = 0
            categories_partial = 0
            categories_not_implemented = 0
            
            for category, practices in security_quality_analysis.items():
                for practice, details in practices.items():
                    categories_total += 1
                    status = details.get("implemented", "no")
                    if status == "yes":
                        categories_implemented += 1
                    elif status == "partial":
                        categories_partial += 1
                    else:
                        categories_not_implemented += 1
            
            if categories_total > 0:
                # Store hard gate counts for later use
                hard_gates_total = categories_total
                hard_gates_met = categories_implemented
                hard_gates_not_met = categories_not_implemented
                hard_gates_partial = categories_partial
                
                implementation_percentage = ((categories_implemented + 0.5 * categories_partial) / categories_total) * 100
                
                # Hard Gate Statistics only
                hard_gate_stats = "### Hard Gates Assessment\n\n"
                hard_gate_stats += f"| Metric | Count | Status |\n"
                hard_gate_stats += f"|--------|-------|--------|\n"
                hard_gate_stats += f"| **Total Evaluated** | {categories_total} | Complete |\n"
                hard_gate_stats += f"| **Gates Met** | {categories_implemented} | Passed |\n"
                hard_gate_stats += f"| **Gates Partially Met** | {categories_partial} | In Progress |\n"
                hard_gate_stats += f"| **Gates Not Met** | {categories_not_implemented} | Failed |\n"
                hard_gate_stats += f"| **Compliance Percentage** | {implementation_percentage:.1f}% | {'Good' if implementation_percentage >= 80 else 'Fair' if implementation_percentage >= 60 else 'Needs Improvement'} |\n\n"
        
        # Enhanced findings statistics
        findings_stats = ""
        if findings:
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for finding in findings:
                severity = finding.get("severity", "low").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
                else:
                    severity_counts["low"] += 1
            
            findings_stats = "### Code Analysis Findings\n\n"
            findings_stats += f"- **Total Issues Found**: {len(findings)}\n"
            if severity_counts["critical"] > 0:
                findings_stats += f"- **Critical Issues**: {severity_counts['critical']}\n"
            if severity_counts["high"] > 0:
                findings_stats += f"- **High Severity Issues**: {severity_counts['high']}\n"
            if severity_counts["medium"] > 0:
                findings_stats += f"- **Medium Severity Issues**: {severity_counts['medium']}\n"
            if severity_counts["low"] > 0:
                findings_stats += f"- **Low Severity Issues**: {severity_counts['low']}\n"
            findings_stats += "\n"
        else:
            findings_stats = "### Code Analysis Findings\n\n"
            findings_stats += "- **Total Issues Found**: 0\n\n"
        
        # JIRA Analysis statistics
        jira_stats = ""
        if jira_stories:
            status_counts = {}
            for story in jira_stories:
                status = story.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            jira_stats = "### JIRA Analysis\n\n"
            jira_stats += f"- **Total Stories**: {len(jira_stories)}\n"
            for status, count in status_counts.items():
                jira_stats += f"- **{status}**: {count} stories\n"
            jira_stats += "\n"
        
        # Add all statistics to Summary
        report += hard_gate_stats + findings_stats + jira_stats
        
        # Add table of contents
        report += "## Table of Contents\n\n"
        report += "1. [Summary](#summary)\n"
        report += "2. [Technology Stack](#technology-stack)\n"
        
        # Add Excel Folder section to TOC if present
        if file_summary.get('excel_folders'):
            report += "3. [Excel Folder Analysis](#excel-folder-analysis)\n"
            report += "4. [Hard Gates Analysis](#hard-gates-analysis)\n"
            report += "5. [Findings](#findings)\n"
            
            if jira_stories:
                report += "6. [JIRA Stories](#jira-stories)\n"
                report += "7. [Action Items](#action-items)\n"
            else:
                report += "6. [Action Items](#action-items)\n"
        else:
            report += "3. [Hard Gates Analysis](#hard-gates-analysis)\n"
            report += "4. [Findings](#findings)\n"
            
            if jira_stories:
                report += "5. [JIRA Stories](#jira-stories)\n"
                report += "6. [Action Items](#action-items)\n"
            else:
                report += "5. [Action Items](#action-items)\n"
        
        # Technology Stack Section
        report += "## Technology Stack\n\n"
        
        if technology_stack:
            # Process all categories except Excel Folder Analysis
            for category, techs in technology_stack.items():
                if category == "Excel Folder Analysis":
                    continue  # Handle separately below
                    
                report += f"### {category.title()}\n\n"
                
                if not isinstance(techs, list):
                    report += "No items found in this category.\n\n"
                    continue
                    
                # Table header
                report += "| Name | Version | Purpose |\n"
                report += "|------|---------|--------|\n"
                
                for tech in techs:
                    if not isinstance(tech, dict):
                        continue
                        
                    name = tech.get("name", "Unknown")
                    version = tech.get("version", "Unknown")
                    purpose = tech.get("purpose", "N/A")
                    
                    report += f"| {name} | {version} | {purpose} |\n"
                report += "\n"
        else:
            report += "No technology stack information available.\n\n"
        
        # Excel Folder Analysis Section (if applicable)
        if file_summary.get('excel_folders') or "Excel Folder Analysis" in technology_stack:
            report += "## Excel Folder Analysis\n\n"
            
            excel_folder_tech = technology_stack.get("Excel Folder Analysis", [])
            if excel_folder_tech:
                report += "The following Excel folders were found in the codebase:\n\n"
                
                # Table header
                report += "| Folder | Files | Purpose |\n"
                report += "|--------|-------|--------|\n"
                
                for tech in excel_folder_tech:
                    if not isinstance(tech, dict):
                        continue
                    
                    name = tech.get("name", "Unknown")
                    files = tech.get("files", [])
                    purpose = tech.get("purpose", "N/A")
                    
                    # Format the folder name
                    folder_name = name
                    if name.startswith("Excel Folder: "):
                        folder_name = name[len("Excel Folder: "):]
                    
                    report += f"| {folder_name} | {len(files)} | {purpose} |\n"
                
                report += "\n"
                
                # Display some of the files in each folder
                report += "### Excel Folder Contents\n\n"
                
                for tech in excel_folder_tech:
                    if not isinstance(tech, dict):
                        continue
                    
                    name = tech.get("name", "Unknown")
                    files = tech.get("files", [])
                    
                    # Format the folder name
                    folder_name = name
                    if name.startswith("Excel Folder: "):
                        folder_name = name[len("Excel Folder: "):]
                    
                    report += f"#### {folder_name}\n\n"
                    
                    if files:
                        report += "Files in this folder:\n\n"
                        for file in files[:10]:  # Show up to 10 files
                            report += f"- {file}\n"
                        
                        if len(files) > 10:
                            report += f"- ... and {len(files) - 10} more files\n"
                    else:
                        report += "No files listed for this folder.\n"
                    
                    report += "\n"
            else:
                report += "Excel folders were detected but no detailed analysis is available. This could be because:\n\n"
                report += "1. The files in these folders could not be properly analyzed\n"
                report += "2. The analysis process didn't complete successfully for these folders\n\n"
                
                if file_summary.get('excel_folders'):
                    report += "Detected Excel folders:\n\n"
                    for folder in file_summary['excel_folders']:
                        report += f"- {folder}\n"
                    report += "\n"
        
        # Hard Gates Analysis Section (replacing Security & Quality Analysis)
        report += "## Hard Gates Analysis\n\n"
        
        if security_quality_analysis:
            # Categories to display
            categories = [
                ("Auditability", "auditability"),
                ("Availability", "availability"), 
                ("Error Handling", "error_handling"),
                ("Monitoring", "monitoring"),
                ("Testing", "testing"),
                ("Security", "security"),
                ("Performance", "performance"),
                ("Data Management", "data_management")
            ]
            
            for display_name, category_key in categories:
                category_data = security_quality_analysis.get(category_key, {})
                if not category_data:
                    continue
                    
                report += f"### {display_name}\n\n"
                
                # Simple table format
                report += "| Practice | Status | Evidence | Recommendation |\n"
                report += "|----------|--------|----------|----------------|\n"
                
                for practice, details in category_data.items():
                    if not isinstance(details, dict):
                        continue
                        
                    # Format practice name for display
                    practice_display = practice.replace("_", " ").title()
                    
                    implemented = details.get("implemented", "no").lower()
                    evidence = details.get("evidence", "No evidence")
                    recommendation = details.get("recommendation", "No recommendation")
                    
                    status = "❌ Not Implemented"
                    if implemented == "yes":
                        status = "✅ Implemented"
                    elif implemented == "partial":
                        status = "⚠️ Partially Implemented"
                    
                    report += f"| {practice_display} | {status} | {evidence} | {recommendation} |\n"
                
                report += "\n"
        else:
            report += "No hard gates analysis available.\n\n"
        
        # Findings Section
        report += "## Findings\n\n"
        
        if findings:
            # Group findings by category
            findings_by_category = {}
            for finding in findings:
                category = finding.get("category", "other")
                if category not in findings_by_category:
                    findings_by_category[category] = []
                findings_by_category[category].append(finding)
                
            # Add findings by category
            for category, category_findings in findings_by_category.items():
                report += f"### {category.title()}\n\n"
                
                for i, finding in enumerate(category_findings):
                    severity = finding.get("severity", "low")
                    description = finding.get("description", "No description")
                    recommendation = finding.get("recommendation", "No recommendation")
                    location = finding.get("location", {})
                    
                    # Handle both old format (dict) and new format (string)
                    if isinstance(location, dict):
                        file_path = location.get("file", "Unknown")
                        line = location.get("line", "?")
                        code = location.get("code", "")
                    else:
                        # New format - location is a string
                        file_path = str(location) if location else "Unknown"
                        line = "?"
                        code = ""
                    
                    report += f"#### {i+1}. {description} (Severity: {severity.title()})\n\n"
                    report += f"**Location**: {file_path}:{line}\n\n"
                    if code:
                        report += f"**Code**: `{code}`\n\n"
                    report += f"**Recommendation**: {recommendation}\n\n"
            
        else:
            report += "No findings were identified in the codebase.\n\n"
        
        # Create action items from findings
        action_items = []
        
        # Add action items for findings
        if findings:
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for finding in findings:
                severity = finding.get("severity", "low").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            if severity_counts["critical"] > 0:
                action_items.append({
                    "title": "Address Critical Severity Findings",
                    "priority": "Critical",
                    "description": f"There are {severity_counts['critical']} critical severity findings that should be addressed immediately. These issues may pose significant security or reliability risks."
                })
                
            if severity_counts["high"] > 0:
                action_items.append({
                    "title": "Address High Severity Findings",
                    "priority": "High",
                    "description": f"There are {severity_counts['high']} high severity findings that should be addressed soon. These issues may impact the stability or security of the application."
                })
                
            if severity_counts["medium"] > 0:
                action_items.append({
                    "title": "Address Medium Severity Findings",
                    "priority": "Medium",
                    "description": f"There are {severity_counts['medium']} medium severity findings that should be planned for remediation. These issues may lead to problems in certain circumstances."
                })
        
        # Add action items for security practices
        if security_quality_analysis:
            auditability = security_quality_analysis.get("auditability", {})
            availability = security_quality_analysis.get("availability", {})
            error_handling = security_quality_analysis.get("error_handling", {})
            
            # Check if there are missing auditability practices
            missing_audit = [practice for practice, details in auditability.items() 
                            if details.get("implemented", "no") == "no"]
            if missing_audit:
                action_items.append({
                    "title": "Improve Logging and Auditability",
                    "priority": "Medium",
                    "description": f"Implement the following logging and auditability practices: {', '.join(missing_audit)}."
                })
            
            # Check if there are missing availability practices
            missing_avail = [practice for practice, details in availability.items() 
                           if details.get("implemented", "no") == "no"]
            if missing_avail:
                action_items.append({
                    "title": "Enhance Application Resilience",
                    "priority": "High",
                    "description": f"Implement the following availability and resilience practices: {', '.join(missing_avail)}."
                })
            
            # Check if there are missing error handling practices
            missing_error = [practice for practice, details in error_handling.items() 
                           if details.get("implemented", "no") == "no"]
            if missing_error:
                action_items.append({
                    "title": "Improve Error Handling",
                    "priority": "Medium",
                    "description": f"Implement the following error handling practices: {', '.join(missing_error)}."
                })
        
        # Action Items Section
        report += "## Action Items\n\n"
        
        # Format action items in the report
        if action_items:
            for i, item in enumerate(action_items):
                report += f"### {i+1}. {item['title']} (Priority: {item['priority']})\n\n"
                report += f"{item['description']}\n\n"
        else:
            report += "No specific action items identified. The codebase appears to follow good practices.\n\n"

        # Add Jira Stories Section if available
        if jira_stories:
            report += "## JIRA Stories\n\n"
            report += "The following JIRA stories are relevant to this project:\n\n"
            
            for story in jira_stories:
                report += f"### {story['key']}: {story['summary']}\n\n"
                report += f"**Status**: {story['status']}\n\n"
                report += f"**Created**: {story['created']}\n\n"
                report += f"**Last Updated**: {story['updated']}\n\n"
                
                if story['description']:
                    report += f"**Description**:\n\n{story['description']}\n\n"
                
                if story['comments']:
                    report += "**Comments**:\n\n"
                    for comment in story['comments']:
                        report += f"- **{comment['author']}** ({comment['created']}):\n  {comment['body']}\n\n"
                
                if story['attachments']:
                    report += "**Attachments**:\n\n"
                    for attachment in story['attachments']:
                        report += f"- {attachment['filename']} ({attachment['size']} bytes)\n"
                    report += "\n"
            
            report += "\n"
        
        # Generate HTML content with ultra-minimal elegant CSS
        css = """
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
        """
        
        # Process strings for clean HTML generation
        newline_str = '\n\n'
        findings_processed = findings_stats.replace('- ', '').replace('### Code Analysis Findings', '').replace(newline_str, '').strip() if findings_stats else ""
        jira_processed = jira_stats.replace('- ', '').replace('### JIRA Analysis', '').replace(newline_str, '').strip() if jira_stats else ""
        
        # Start with the ultra-minimal clean HTML structure
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Assessment Report</title>
    <style>
    {css}
    </style>
</head>
<body>
    <h1>{project_name}</h1>
    <p style="color: #2563eb; margin-bottom: 30px; font-weight: 500;">Assessment Report</p>

    <h2>Executive Summary</h2>
    
    <h3>File Analysis</h3>
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Files Analyzed</td>
                <td><strong>{file_summary['count']}</strong></td>
            </tr>
            {f"<tr><td>Excel Folders</td><td><strong>{len(file_summary.get('excel_folders', []))}</strong></td></tr>" if file_summary.get('excel_folders') else ""}
        </tbody>
    </table>
        
    {f'''
    <h3>Hard Gates Assessment</h3>
    <table>
        <thead>
            <tr>
                <th>Status</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Evaluated</td>
                <td><strong>{hard_gates_total}</strong></td>
                <td>100%</td>
            </tr>
            <tr>
                <td><span class="status-implemented">✓ Passed</span></td>
                <td><strong>{hard_gates_met}</strong></td>
                <td>{(hard_gates_met / hard_gates_total * 100):.1f}%</td>
            </tr>
            <tr>
                <td><span class="status-partial">⚬ Partial</span></td>
                <td><strong>{hard_gates_partial}</strong></td>
                <td>{(hard_gates_partial / hard_gates_total * 100):.1f}%</td>
            </tr>
            <tr>
                <td><span class="status-not-implemented">✗ Failed</span></td>
                <td><strong>{hard_gates_not_met}</strong></td>
                <td>{(hard_gates_not_met / hard_gates_total * 100):.1f}%</td>
            </tr>
            <tr>
                <td><strong>Overall Compliance</strong></td>
                <td colspan="2"><strong>{((hard_gates_met + 0.5 * hard_gates_partial) / hard_gates_total * 100):.1f}%</strong></td>
            </tr>
        </tbody>
    </table>
    ''' if hard_gates_total > 0 else ""}
        
    {f'''
    <h3>Code Findings</h3>
    <table>
        <thead>
            <tr>
                <th>Severity</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Issues</td>
                <td><strong>{len(findings)}</strong></td>
            </tr>
        </tbody>
    </table>
    ''' if findings else '''
    <h3>Code Findings</h3>
    <table>
        <thead>
            <tr>
                <th>Status</th>
                <th>Result</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Issues Found</td>
                <td><strong>0</strong></td>
            </tr>
        </tbody>
    </table>
    '''}
        
    {f'''
    <h3>JIRA Analysis</h3>
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Count</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Total Stories</td>
                <td><strong>{len(jira_stories)}</strong></td>
            </tr>
        </tbody>
    </table>
    ''' if jira_stories else ""}

    <h2>Technology Stack</h2>
"""

        if technology_stack:
            for category, techs in technology_stack.items():
                if category == "Excel Folder Analysis":
                    continue  # Handle separately below
                    
                html_content += f"""
    <h3>{category.title()}</h3>
"""
                
                if not isinstance(techs, list) or not techs:
                    html_content += """
    <p style="color: #999;">No items found in this category.</p>
"""
                else:
                    html_content += """
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Version</th>
                <th>Purpose</th>
            </tr>
        </thead>
        <tbody>
"""
                    
                    for tech in techs:
                        if not isinstance(tech, dict):
                            continue
                            
                        name = tech.get("name", "Unknown")
                        version = tech.get("version", "Unknown")
                        purpose = tech.get("purpose", "N/A")
                        
                        html_content += f"""
            <tr>
                <td><strong>{name}</strong></td>
                <td>{version}</td>
                <td>{purpose}</td>
            </tr>
"""
                    
                    html_content += """
        </tbody>
    </table>
"""
        else:
            html_content += """
    <p style="color: #999;">No technology stack information available.</p>
"""

        # Excel Folder Analysis Section (if applicable)
        if file_summary.get('excel_folders') or "Excel Folder Analysis" in technology_stack:
            html_content += """
    <h2>Excel Folder Analysis</h2>
"""
            
            excel_folder_tech = technology_stack.get("Excel Folder Analysis", [])
            if excel_folder_tech:
                html_content += """
    <table>
        <thead>
            <tr>
                <th>Folder</th>
                <th>Files</th>
                <th>Purpose</th>
            </tr>
        </thead>
        <tbody>
"""
                
                for tech in excel_folder_tech:
                    if not isinstance(tech, dict):
                        continue
                    
                    name = tech.get("name", "Unknown")
                    files = tech.get("files", [])
                    purpose = tech.get("purpose", "N/A")
                    
                    # Format the folder name
                    folder_name = name
                    if name.startswith("Excel Folder: "):
                        folder_name = name[len("Excel Folder: "):]
                    
                    html_content += f"""
            <tr>
                <td><strong>{folder_name}</strong></td>
                <td>{len(files)}</td>
                <td>{purpose}</td>
            </tr>
"""
                
                html_content += """
        </tbody>
    </table>
"""
            else:
                html_content += """
    <p style="color: #999;">Excel folders detected but analysis unavailable.</p>
"""

        # Hard Gates Analysis Section
        html_content += """
    <h2>Hard Gates Analysis</h2>
"""
        
        if security_quality_analysis:
            # Categories to display
            categories = [
                ("Auditability", "auditability"),
                ("Availability", "availability"), 
                ("Error Handling", "error_handling"),
                ("Monitoring", "monitoring"),
                ("Testing", "testing"),
                ("Security", "security"),
                ("Performance", "performance"),
                ("Data Management", "data_management")
            ]
            
            for display_name, category_key in categories:
                category_data = security_quality_analysis.get(category_key, {})
                if not category_data:
                    continue
                    
                html_content += f"""
    <h3>{display_name}</h3>
    <table>
        <thead>
            <tr>
                <th>Practice</th>
                <th>Status</th>
                <th>Evidence</th>
                <th>Recommendation</th>
            </tr>
        </thead>
        <tbody>
"""
                
                for practice, details in category_data.items():
                    if not isinstance(details, dict):
                        continue
                        
                    # Format practice name for display
                    practice_display = practice.replace("_", " ").title()
                    
                    implemented = details.get("implemented", "no").lower()
                    evidence = details.get("evidence", "No evidence")
                    recommendation = details.get("recommendation", "No recommendation")
                    
                    if implemented == "yes":
                        status = '<span class="status-implemented">✓ Implemented</span>'
                    elif implemented == "partial":
                        status = '<span class="status-partial">⚬ Partial</span>'
                    else:
                        status = '<span class="status-not-implemented">✗ Missing</span>'
                    
                    html_content += f"""
            <tr>
                <td><strong>{practice_display}</strong></td>
                <td>{status}</td>
                <td>{evidence}</td>
                <td>{recommendation}</td>
            </tr>
"""
                
                html_content += """
        </tbody>
    </table>
"""
        else:
            html_content += """
    <p style="color: #999;">No hard gates analysis available.</p>
"""

        # Findings Section
        if findings:
            html_content += """
    <h2>Code Findings</h2>
"""
            # Group findings by category
            findings_by_category = {}
            for finding in findings:
                category = finding.get("category", "other")
                if category not in findings_by_category:
                    findings_by_category[category] = []
                findings_by_category[category].append(finding)
                
            # Add findings by category
            for category, category_findings in findings_by_category.items():
                html_content += f"""
    <h3>{category.title()}</h3>
"""
                
                for i, finding in enumerate(category_findings):
                    severity = finding.get("severity", "low")
                    description = finding.get("description", "No description")
                    recommendation = finding.get("recommendation", "No recommendation")
                    location = finding.get("location", {})
                    
                    # Handle both old format (dict) and new format (string)
                    if isinstance(location, dict):
                        file_path = location.get("file", "Unknown")
                        line = location.get("line", "?")
                        code = location.get("code", "")
                    else:
                        # New format - location is a string
                        file_path = str(location) if location else "Unknown"
                        line = "?"
                        code = ""
                    
                    severity_class = f"priority-{severity.lower()}"
                    
                    html_content += f"""
    <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
        <h4 style="margin: 0 0 10px 0;">{i+1}. {description} <span class="{severity_class}">({severity.title()})</span></h4>
        <p><strong>Location:</strong> {file_path}:{line}</p>
"""
                    
                    if code:
                        html_content += f"""
        <p><strong>Code:</strong> <code>{code}</code></p>
"""
                    
                    html_content += f"""
        <p><strong>Recommendation:</strong> {recommendation}</p>
    </div>
"""

        # JIRA Stories Section
        if jira_stories:
            html_content += """
    <h2>JIRA Stories</h2>
"""
            
            for story in jira_stories:
                html_content += f"""
    <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
        <h3 style="margin: 0 0 15px 0;">{story['key']}: {story['summary']}</h3>
        <p><strong>Status:</strong> {story['status']} | <strong>Created:</strong> {story['created']} | <strong>Updated:</strong> {story['updated']}</p>
"""
                
                if story['description']:
                    html_content += f"""
        <p><strong>Description:</strong> {story['description']}</p>
"""
                
                if story['comments']:
                    html_content += """
        <p><strong>Comments:</strong></p>
        <ul style="margin: 10px 0;">
"""
                    for comment in story['comments']:
                        html_content += f"""
            <li><strong>{comment['author']}</strong> ({comment['created']}): {comment['body']}</li>
"""
                    html_content += """
        </ul>
"""
                
                if story['attachments']:
                    html_content += """
        <p><strong>Attachments:</strong></p>
        <ul style="margin: 10px 0;">
"""
                    for attachment in story['attachments']:
                        html_content += f"""
            <li>{attachment['filename']} ({attachment['size']} bytes)</li>
"""
                    html_content += """
        </ul>
"""
                html_content += """
    </div>
"""

        # Action Items Section
        if action_items:
            html_content += """
    <h2>Action Items</h2>
"""
            for i, item in enumerate(action_items):
                priority_class = f"priority-{item['priority'].lower()}"
                html_content += f"""
    <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 6px; border: 1px solid #e2e8f0;">
        <h3 style="margin: 0 0 10px 0;">{i+1}. {item['title']} <span class="{priority_class}">({item['priority']})</span></h3>
        <p>{item['description']}</p>
    </div>
"""

        html_content += """
</body>
</html>"""

        # Generate PDF
        pdf_path = None
        try:
            from weasyprint import HTML
            pdf_path = os.path.join(output_dir, "analysis_report.pdf")
            HTML(string=html_content).write_pdf(pdf_path)
            print(f"Generated PDF report: {pdf_path}")
        except Exception as e:
            print(f"Warning: Could not generate PDF: {str(e)}")
            print("Please ensure WeasyPrint is installed correctly.")
        
        # Save both Markdown and HTML
        os.makedirs(output_dir, exist_ok=True)
        
        # Save Markdown
        md_path = os.path.join(output_dir, "analysis_report.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report)
            
        # Save HTML
        html_path = os.path.join(output_dir, "analysis_report.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return {
            "markdown": md_path,
            "html": html_path,
            "pdf": pdf_path
        }

    def post(self, shared, prep_res, exec_res):
        # Store the report paths in shared state
        shared["analysis_report"] = exec_res
        
        # Print the report paths
        print(f"\nAnalysis reports generated:")
        print(f"- Markdown: {exec_res['markdown']}")
        print(f"- HTML: {exec_res['html']}")
        if exec_res['pdf']:
            print(f"- PDF: {exec_res['pdf']}")
            
        # Print command to open the HTML report for easier viewing
        print(f"\nOpen the HTML report with: open {exec_res['html']}")
        
        # Store reports in ChromaDB
        try:
            from utils.chromadb_store import ReportStore
            
            # Get component name
            project_name = shared.get("project_name", "Unknown Project")
            
            # Use context manager to properly handle ChromaDB cleanup
            with ReportStore() as store:
                # Store the analysis report
                analysis_report_path = exec_res['markdown']
                if os.path.exists(analysis_report_path):
                    store.store_analysis_report(project_name, analysis_report_path)
                
                # Store the OCP assessment report if it exists
                output_dir = os.path.dirname(analysis_report_path)
                ocp_assessment_path = os.path.join(output_dir, "ocp_assessment.html")
                ocp_assessment_md_path = os.path.join(output_dir, "ocp_assessment.md")
                
                # Check if OCP markdown report exists, if not try to extract content from HTML
                if os.path.exists(ocp_assessment_md_path):
                    store.store_ocp_assessment(project_name, ocp_assessment_md_path)
                elif os.path.exists(ocp_assessment_path):
                    # If we only have HTML, extract text content
                    import re
                    try:
                        with open(ocp_assessment_path, 'r', encoding='utf-8') as file:
                            html_content = file.read()
                            
                        # Simple regex to extract text from HTML tags
                        text_content = re.sub(r'<[^>]*>', ' ', html_content)
                        text_content = re.sub(r'\s+', ' ', text_content).strip()
                        
                        # Create a markdown file from the extracted text
                        ocp_assessment_md_path = os.path.join(output_dir, "ocp_assessment.md")
                        with open(ocp_assessment_md_path, 'w', encoding='utf-8') as file:
                            file.write(f"# OpenShift Migration Assessment for {project_name}\n\n")
                            file.write(text_content)
                        
                        store.store_ocp_assessment(project_name, ocp_assessment_md_path)
                    except Exception as e:
                        print(f"Error extracting text from OCP HTML: {str(e)}")
            
            print("\nStored reports in ChromaDB successfully")
            
        except Exception as e:
            print(f"\nWarning: Could not store reports in ChromaDB: {str(e)}")
        
        # Return a simple string action rather than a complex object
        return "default" 