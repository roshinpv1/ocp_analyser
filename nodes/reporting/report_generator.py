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
        
        # Include file information in the report
        file_summary = {
            "count": file_count,
            "extensions": {}
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
        report += f"- **Files Analyzed**: {file_summary['count']}\n"
        if file_summary['extensions']:
            report += "- **File Types**: "
            ext_counts = [f"{ext} ({count})" for ext, count in file_summary['extensions'].items()]
            report += ", ".join(ext_counts) + "\n"
        
        # Calculate statistics for Summary
        security_stats = ""
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
                implementation_percentage = ((categories_implemented + 0.5 * categories_partial) / categories_total) * 100
                security_stats = f"- **Security & Quality Implementation**: {implementation_percentage:.1f}%\n"
                security_stats += f"- **Practices Implemented**: {categories_implemented} fully, {categories_partial} partially, {categories_not_implemented} not implemented\n"
        
        # Calculate findings statistics
        findings_stats = ""
        if findings:
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for finding in findings:
                severity = finding.get("severity", "low").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
                else:
                    severity_counts["low"] += 1
            
            findings_stats = f"- **Total Findings**: {len(findings)}\n"
            if severity_counts["critical"] > 0:
                findings_stats += f"- **Critical Severity Issues**: {severity_counts['critical']}\n"
            if severity_counts["high"] > 0:
                findings_stats += f"- **High Severity Issues**: {severity_counts['high']}\n"
            if severity_counts["medium"] > 0:
                findings_stats += f"- **Medium Severity Issues**: {severity_counts['medium']}\n"
            if severity_counts["low"] > 0:
                findings_stats += f"- **Low Severity Issues**: {severity_counts['low']}\n"
        else:
            findings_stats = "- **Total Findings**: 0\n"
        
        # Calculate component mismatches
        component_stats = ""
        mismatches_count = 0
        if excel_components and component_analysis:
            for excel_comp, excel_data in excel_components.items():
                excel_comp_lower = excel_comp.lower()
                excel_declared = excel_data.get("is_yes", False)
                
                for comp_name, comp_data in component_analysis.items():
                    if excel_comp_lower in comp_name.lower() or comp_name.lower() in excel_comp_lower:
                        detected = comp_data["detected"].lower() == "yes"
                        if excel_declared != detected:
                            mismatches_count += 1
                        break
                        
            if mismatches_count > 0:
                component_stats = f"- **Component Declaration Mismatches**: {mismatches_count}\n"
        
        # Add all statistics to Summary
        report += security_stats + findings_stats + component_stats + "\n"
        
        # Add table of contents
        report += "## Table of Contents\n\n"
        report += "1. [Summary](#executive-summary)\n"
        report += "2. [Component Analysis](#component-analysis)\n"
        report += "3. [Technology Stack](#technology-stack)\n"
        report += "4. [Security & Quality Analysis](#security-quality-analysis)\n"
        report += "5. [Findings](#findings)\n"
        
        if jira_stories:
            report += "6. [Jira Stories](#jira-stories)\n"
            report += "7. [Action Items](#action-items)\n"
        else:
            report += "6. [Action Items](#action-items)\n"
        
        # Component Analysis Section
        report += "## Component Analysis\n\n"
        
        if excel_components and component_analysis:
            report += "The following table compares the components declared in the intake form with the components detected in the codebase:\n\n"
            
            # Table header
            report += "| Component | Declared | Detected | Status |\n"
            report += "|-----------|----------|----------|--------|\n"
            
            for excel_comp, excel_data in excel_components.items():
                excel_comp_lower = excel_comp.lower()
                excel_declared = excel_data.get("is_yes", False)
                
                # Find if component is in the analysis
                matched = False
                detected = False
                
                for comp_name, comp_data in component_analysis.items():
                    if excel_comp_lower in comp_name.lower() or comp_name.lower() in excel_comp_lower:
                        matched = True
                        detected = comp_data["detected"].lower() == "yes"
                        break
                
                status = "Match" if excel_declared == detected else "Mismatch"
                
                report += f"| {excel_comp} | {'Yes' if excel_declared else 'No'} | {'Yes' if detected else 'No'} | {status} |\n"
                
            report += "\n"
        else:
            # Just list detected components
            report += "### Components Detected in Codebase\n\n"
            
            if component_analysis:
                # Table header
                report += "| Component | Detected | Evidence |\n"
                report += "|-----------|----------|----------|\n"
                
                for comp_name, comp_data in component_analysis.items():
                    detected = comp_data["detected"].lower() == "yes"
                    evidence = comp_data.get("evidence", "No evidence")
                    evidence_short = (evidence[:75] + '...') if len(evidence) > 75 else evidence
                    
                    report += f"| {comp_name} | {'Yes' if detected else 'No'} | {evidence_short} |\n"
                report += "\n"
            else:
                report += "No components were detected in the codebase.\n\n"
        
        # Technology Stack Section
        report += "## Technology Stack\n\n"
        
        if technology_stack:
            for category, techs in technology_stack.items():
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
        
        # Security & Quality Analysis Section
        report += "## Security & Quality Analysis\n\n"
        
        if security_quality_analysis:
            # Categories to display
            categories = [
                ("Auditability", "auditability"),
                ("Availability", "availability"),
                ("Error Handling", "error_handling"),
                ("Monitoring", "monitoring"),
                ("Testing", "testing")
            ]
            
            for display_name, category_key in categories:
                category_data = security_quality_analysis.get(category_key, {})
                if not category_data:
                    continue
                    
                report += f"### {display_name}\n\n"
                
                # Table header - modified to match Technology Stack format
                report += "| Practice | Status | Evidence |\n"
                report += "|----------|--------|----------|\n"
                
                for practice, details in category_data.items():
                    if not isinstance(details, dict):
                        continue
                        
                    # Format practice name for display
                    practice_display = practice.replace("_", " ").title()
                    
                    implemented = details.get("implemented", "no").lower()
                    evidence = details.get("evidence", "No evidence")
                    
                    status = "❌ Not Implemented"
                    if implemented == "yes":
                        status = "✅ Implemented"
                    elif implemented == "partial":
                        status = "⚠️ Partially Implemented"
                    
                    # Using the same 3-column format as Technology Stack section
                    report += f"| {practice_display} | {status} | {evidence} |\n"
                
                report += "\n"
                
                # Add a separate table for recommendations in the same section
                report += "#### Recommendations\n\n"
                report += "| Practice | Recommendation |\n"
                report += "|----------|----------------|\n"
                
                for practice, details in category_data.items():
                    if not isinstance(details, dict):
                        continue
                    
                    practice_display = practice.replace("_", " ").title()
                    recommendation = details.get("recommendation", "No recommendation")
                    
                    report += f"| {practice_display} | {recommendation} |\n"
                
                report += "\n"
        else:
            report += "No security and quality analysis available.\n\n"
        
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
                    file_path = location.get("file", "Unknown")
                    line = location.get("line", "?")
                    code = location.get("code", "")
                    
                    report += f"#### {i+1}. {description} (Severity: {severity.title()})\n\n"
                    report += f"**Location**: {file_path}:{line}\n\n"
                    if code:
                        report += f"**Code**: `{code}`\n\n"
                    report += f"**Recommendation**: {recommendation}\n\n"
            
        else:
            report += "No findings were identified in the codebase.\n\n"
        
        # Create action items from findings
        action_items = []
        
        # Add action items for component mismatches
        if mismatches_count > 0:
            action_items.append({
                "title": "Resolve Component Declaration Mismatches",
                "priority": "High",
                "description": "There are discrepancies between the components declared in the intake form and those detected in the codebase. Review the Component Analysis section to identify and address these mismatches."
            })
        
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
            report += "## Jira Stories\n\n"
            report += "The following Jira stories are relevant to this project:\n\n"
            
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
        
        # Generate HTML content with proper escaping for replace() calls
        css = """
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
.critical, .high { color: #e74c3c; }
.medium { color: #f39c12; }
.low { color: #27ae60; }

.empty-section {
    background-color: #f8f9fa;
    border-left: 4px solid #95a5a6;
    padding: 15px 20px;
    margin: 20px 0;
    border-radius: 0 4px 4px 0;
}

.empty-section p {
    margin: 0 0 10px 0;
    color: #555;
}

.empty-section ul {
    margin: 0 0 10px 20px;
    padding: 0;
}

.empty-section li {
    margin-bottom: 5px;
}

.finding {
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    padding: 15px;
    border-left: 4px solid #95a5a6;
}

.finding.severity-critical, .finding.severity-high {
    border-left-color: #e74c3c;
}

.finding.severity-medium {
    border-left-color: #f39c12;
}

.finding.severity-low {
    border-left-color: #27ae60;
}

.finding-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.finding-number {
    font-weight: bold;
    color: #7f8c8d;
}

.finding-severity {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 500;
    text-transform: uppercase;
}

.finding-severity.critical, .finding-severity.high {
    background-color: #fdeaea;
    color: #c0392b;
}

.finding-severity.medium {
    background-color: #fef5e7;
    color: #d35400;
}

.finding-severity.low {
    background-color: #e9f7ef;
    color: #27ae60;
}

.code-snippet {
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 10px;
    margin: 10px 0;
    overflow-x: auto;
}

.code-snippet pre {
    margin: 0;
}

.code-snippet code {
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
    font-size: 0.9em;
}

.recommendation {
    margin-top: 10px;
}

.tech-category, .security-category, .findings-category {
    margin-bottom: 30px;
}

.executive-summary {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    margin-bottom: 25px;
}
        """
        
        # Start with the basic HTML structure
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application & Platform Hard Gates for  {project_name}</title>
    <style>
    {css}
    </style>
</head>
<body>
    <h1>Application & Platform Hard Gates for  {project_name}</h1>

    <div class="executive-summary">
        <h2>Summary</h2>
        <ul>
            {f"<li>{security_stats.replace('- ', '')}</li>" if security_stats else ""}
            {f"<li>{findings_stats.replace('- ', '')}</li>" if findings_stats else ""}
            {f"<li>{component_stats.replace('- ', '')}</li>" if component_stats else ""}
        </ul>
    </div>

    <div class="component-analysis">
        <h2>Component Analysis</h2>
"""

        if excel_components and component_analysis:
            html_content += """
        <p>The following table compares the components declared in the intake form with the components detected in the codebase:</p>
        <table>
            <tr>
                <th>Component</th>
                <th>Declared</th>
                <th>Detected</th>
                <th>Status</th>
            </tr>
"""
        elif component_analysis:
            html_content += """
        <p>Components detected in the codebase:</p>
        <table>
            <tr>
                <th>Component</th>
                <th>Detected</th>
                <th>Evidence</th>
            </tr>
"""
        else:
            html_content += """
        <p>No component analysis available.</p>
"""

        if excel_components and component_analysis:
            for excel_comp, excel_data in excel_components.items():
                excel_comp_lower = excel_comp.lower()
                excel_declared = excel_data.get("is_yes", False)
                
                matched = False
                detected = False
                
                for comp_name, comp_data in component_analysis.items():
                    if excel_comp_lower in comp_name.lower() or comp_name.lower() in excel_comp_lower:
                        matched = True
                        detected = comp_data["detected"].lower() == "yes"
                        break
                
                status = "Match" if excel_declared == detected else "Mismatch"
                status_class = "low" if status == "Match" else "high"
                
                html_content += f"""
            <tr>
                <td>{excel_comp}</td>
                <td>{'Yes' if excel_declared else 'No'}</td>
                <td>{'Yes' if detected else 'No'}</td>
                <td class="{status_class}">{status}</td>
            </tr>"""
        elif component_analysis:
            for comp_name, comp_data in component_analysis.items():
                detected = comp_data["detected"].lower() == "yes"
                evidence = comp_data.get("evidence", "No evidence")
                evidence_short = (evidence[:75] + '...') if len(evidence) > 75 else evidence
                
                html_content += f"""
            <tr>
                <td>{comp_name}</td>
                <td>{'Yes' if detected else 'No'}</td>
                <td>{evidence_short}</td>
            </tr>"""
        
        html_content += """
        </table>
    </div>

    <div class="technology-stack">
        <h2>Technology Stack</h2>
"""

        if technology_stack:
            for category, techs in technology_stack.items():
                html_content += f"""
        <div class="tech-category">
            <h3>{category.title()}</h3>
"""
                
                if not isinstance(techs, list) or not techs:
                    html_content += """
            <p>No items found in this category.</p>
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
                        <td>{name}</td>
                        <td>{version}</td>
                        <td>{purpose}</td>
                    </tr>
"""
                    
                    html_content += """
                </tbody>
            </table>
"""
                
                html_content += """
        </div>
"""
        else:
            html_content += """
        <div class="empty-section">
            <p>No technology stack information was detected. This may happen if:</p>
            <ul>
                <li>The codebase is very small or consists of simple files</li>
                <li>The files analyzed didn't contain clear technology indicators</li>
                <li>The analysis was unable to complete successfully</li>
            </ul>
            <p>Consider uploading a more complete codebase or checking the analysis logs for errors.</p>
        </div>
"""
        
        # Security & Quality Analysis Section
        html_content += """
    <div class="security-quality">
        <h2>Security & Quality Analysis</h2>
"""
        
        if security_quality_analysis:
            # Categories to display
            categories = [
                ("Auditability", "auditability"),
                ("Availability", "availability"),
                ("Error Handling", "error_handling"),
                ("Monitoring", "monitoring"),
                ("Testing", "testing")
            ]
            
            for display_name, category_key in categories:
                category_data = security_quality_analysis.get(category_key, {})
                if not category_data:
                    continue
                    
                html_content += f"""
        <div class="security-category">
            <h3>{display_name}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Practice</th>
                        <th>Status</th>
                        <th>Evidence</th>
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
                    
                    status_class = ""
                    status_text = "Not Implemented"
                    if implemented == "yes":
                        status_class = "low"
                        status_text = "Implemented"
                    elif implemented == "partial":
                        status_class = "medium"
                        status_text = "Partially Implemented"
                    else:
                        status_class = "high"
                    
                    html_content += f"""
                    <tr>
                        <td>{practice_display}</td>
                        <td><span class="{status_class}">{status_text}</span></td>
                        <td>{evidence}</td>
                    </tr>
"""
                
                html_content += """
                </tbody>
            </table>
            
            <h4>Recommendations</h4>
            <table>
                <thead>
                    <tr>
                        <th>Practice</th>
                        <th>Recommendation</th>
                    </tr>
                </thead>
                <tbody>
"""
                
                for practice, details in category_data.items():
                    if not isinstance(details, dict):
                        continue
                    
                    practice_display = practice.replace("_", " ").title()
                    recommendation = details.get("recommendation", "No recommendation")
                    
                    html_content += f"""
                    <tr>
                        <td>{practice_display}</td>
                        <td>{recommendation}</td>
                    </tr>
"""
                
                html_content += """
                </tbody>
            </table>
        </div>
"""
        else:
            html_content += """
        <div class="empty-section">
            <p>No security and quality analysis information is available. This may happen if:</p>
            <ul>
                <li>The codebase doesn't have clear security or quality patterns to analyze</li>
                <li>The files analyzed weren't sufficient for a comprehensive security review</li>
                <li>The analysis was unable to complete successfully</li>
            </ul>
            <p>Consider uploading a more complete codebase or checking the analysis logs for errors.</p>
        </div>
"""

        html_content += """
    </div>

    <div class="findings">
        <h2>Findings</h2>
"""

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
                html_content += f"""
        <div class="findings-category">
            <h3>{category.title()}</h3>
"""
                
                for i, finding in enumerate(category_findings):
                    severity = finding.get("severity", "low")
                    description = finding.get("description", "No description")
                    recommendation = finding.get("recommendation", "No recommendation")
                    location = finding.get("location", {})
                    file_path = location.get("file", "Unknown")
                    line = location.get("line", "?")
                    code = location.get("code", "")
                    
                    severity_class = severity.lower()
                    
                    html_content += f"""
            <div class="finding severity-{severity_class}">
                <div class="finding-header">
                    <span class="finding-number">{i+1}</span>
                    <span class="finding-severity {severity_class}">{severity.title()}</span>
                </div>
                <h4>{description}</h4>
                <p><strong>Location:</strong> {file_path}:{line}</p>
"""
                    
                    if code:
                        html_content += f"""
                <div class="code-snippet">
                    <pre><code>{code}</code></pre>
                </div>
"""
                    
                    html_content += f"""
                <div class="recommendation">
                    <strong>Recommendation:</strong> {recommendation}
                </div>
            </div>
"""
                
                html_content += """
        </div>
"""
        else:
            html_content += """
        <div class="empty-section">
            <p>No findings were identified in the codebase. This could mean either:</p>
            <ul>
                <li>The codebase follows good practices and has no notable issues</li>
                <li>The analysis was limited in scope or couldn't detect common issues</li>
                <li>The analysis was unable to complete successfully</li>
            </ul>
            <p>You may want to perform a manual review of critical security aspects to confirm the absence of issues.</p>
        </div>
"""
        
        html_content += """
    </div>

    <div class="action-items">
        <h2>Action Items</h2>
"""

        if action_items:
            for i, item in enumerate(action_items):
                priority_class = item['priority'].lower()
                html_content += f"""
        <div class="action-item {priority_class}">
            <h3>{i+1}. {item['title']} (Priority: {item['priority']})</h3>
            <p>{item['description']}</p>
        </div>
"""
        else:
            html_content += """
        <p>No specific action items identified. The codebase appears to follow good practices.</p>
"""

        html_content += """
    </div>
"""

        # Add Jira Stories to HTML with proper string handling
        if jira_stories:
            html_content += """
    <div class="jira-stories">
        <h2>Jira Stories</h2>
"""
            for story in jira_stories:
                status_class = ""
                if story['status'].lower() == "done":
                    status_class = "low"
                elif story['status'].lower() == "in progress":
                    status_class = "medium"
                elif story['status'].lower() == "to do":
                    status_class = "high"
                
                html_content += f"""
        <div class="jira-story">
            <div class="jira-story-header">
                <span class="jira-story-key">{story['key']}</span>
                <span class="jira-story-status {status_class}">{story['status']}</span>
            </div>
            <h3>{story['summary']}</h3>
            <p><strong>Created:</strong> {story['created']}<br>
            <strong>Updated:</strong> {story['updated']}</p>
"""
                
                # Handle description - extract as variable first
                desc = story.get('description', '')
                if desc:
                    desc_html = desc.replace('\n', '<br>')
                    html_content += f"""
            <div class="jira-description">
                {desc_html}
            </div>
"""
                else:
                    html_content += """
            <div class="jira-description">
                No description
            </div>
"""
                
                # Add comments
                if story['comments']:
                    html_content += """
            <h4>Comments</h4>
"""
                    for comment in story['comments']:
                        # Handle comment body - extract as variable first
                        comment_body = comment.get('body', '')
                        comment_html = comment_body.replace('\n', '<br>')
                        
                        html_content += f"""
            <div class="jira-comment">
                <strong>{comment['author']}</strong> ({comment['created']})<br>
                {comment_html}
            </div>
"""
                
                # Add attachments
                if story['attachments']:
                    html_content += """
            <h4>Attachments</h4>
"""
                    for attachment in story['attachments']:
                        if attachment.get('is_image', False) and 'local_path' in attachment:
                            html_content += f"""
            <div class="jira-attachment">
                <p>{attachment['filename']} ({attachment['size']} bytes)</p>
                <img src="{attachment['local_path']}" alt="{attachment['filename']}" class="jira-image">
            </div>
"""
                        else:
                            html_content += f"""
            <div class="jira-attachment">
                <p>{attachment['filename']} ({attachment['size']} bytes)</p>
            </div>
"""
                
                html_content += """
        </div>
"""
            
            html_content += """
    </div>
"""

        # Closing HTML tags
        html_content += """
</body>
</html>
"""

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
            
            # Initialize the ChromaDB store
            store = ReportStore()
            
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