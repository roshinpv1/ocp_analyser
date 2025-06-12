import json
from typing import Dict, Any, List
from datetime import datetime

def format_as_json(assessment_results: Dict[str, Any], project_name: str) -> Dict[str, Any]:
    """
    Format assessment results as JSON for API responses.
    """
    return {
        "project_name": project_name,
        "assessment_date": datetime.now().isoformat(),
        "assessment_type": "hard_gate_assessment",
        "results": assessment_results
    }

def format_for_table(assessment_results: Dict[str, Any], project_name: str) -> List[Dict[str, Any]]:
    """
    Format assessment results as table data for VS Code extension.
    
    Returns a list of table rows with category, practice, status, evidence, and recommendation.
    """
    table_data = []
    
    security_quality = assessment_results.get("security_quality_analysis", {})
    
    for category, practices in security_quality.items():
        if not isinstance(practices, dict):
            continue
            
        for practice, details in practices.items():
            if not isinstance(details, dict):
                continue
                
            # Format practice name
            practice_display = practice.replace("_", " ").title()
            category_display = category.replace("_", " ").title()
            
            status = details.get("implemented", "no")
            evidence = details.get("evidence", "No evidence")
            recommendation = details.get("recommendation", "No recommendation")
            
            # Map status to display values
            status_display = {
                "yes": "✓ Implemented",
                "partial": "⚬ Partial", 
                "no": "✗ Missing"
            }.get(status, status)
            
            table_data.append({
                "category": category_display,
                "practice": practice_display,
                "status": status_display,
                "evidence": evidence,
                "recommendation": recommendation
            })
    
    # Add technology stack information
    tech_stack = assessment_results.get("technology_stack", {})
    if tech_stack:
        languages = tech_stack.get("languages", [])
        frameworks = tech_stack.get("frameworks", [])
        databases = tech_stack.get("databases", [])
        
        for lang in languages:
            if isinstance(lang, dict):
                table_data.append({
                    "category": "Technology",
                    "practice": f"Language: {lang.get('name', 'Unknown')}",
                    "status": "✓ Detected",
                    "evidence": f"Version: {lang.get('version', 'N/A')}, Purpose: {lang.get('purpose', 'N/A')}",
                    "recommendation": "Continue using as appropriate"
                })
    
    return table_data

def generate_html_report(assessment_results: Dict[str, Any], project_name: str) -> str:
    """
    Generate HTML report for CLI output.
    """
    
    # Calculate statistics
    security_quality = assessment_results.get("security_quality_analysis", {})
    total_gates = 0
    gates_met = 0
    gates_partial = 0
    gates_not_met = 0
    
    for category, practices in security_quality.items():
        if isinstance(practices, dict):
            for practice, details in practices.items():
                if isinstance(details, dict):
                    total_gates += 1
                    status = details.get("implemented", "no")
                    if status == "yes":
                        gates_met += 1
                    elif status == "partial":
                        gates_partial += 1
                    else:
                        gates_not_met += 1
    
    compliance_percentage = ((gates_met + 0.5 * gates_partial) / total_gates * 100) if total_gates > 0 else 0
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hard Gate Assessment - {project_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #374151;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f3f4f6;
        }}
        
        h1 {{
            font-size: 2em;
            color: #1f2937;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        
        h2 {{
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        
        h3 {{
            color: #374151;
            margin-top: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        th {{
            background: #2563eb;
            color: #fff;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        tr:hover {{
            background: #f9fafb;
        }}
        
        .status-implemented {{
            color: #059669;
            background: #ecfdf5;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .status-partial {{
            color: #d97706;
            background: #fffbeb;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .status-not-implemented {{
            color: #dc2626;
            background: #fef2f2;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2563eb;
        }}
        
        .stat-label {{
            color: #6b7280;
            margin-top: 5px;
        }}
        
        .compliance-bar {{
            width: 100%;
            height: 20px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .compliance-fill {{
            height: 100%;
            background: linear-gradient(90deg, #dc2626 0%, #d97706 50%, #059669 100%);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <h1>{project_name}</h1>
    <p style="color: #2563eb; margin-bottom: 30px; font-weight: 500;">Hard Gate Assessment Report</p>
    
    <h2>Executive Summary</h2>
    
    <div class="summary-stats">
        <div class="stat-card">
            <div class="stat-number">{total_gates}</div>
            <div class="stat-label">Total Gates Evaluated</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{gates_met}</div>
            <div class="stat-label">Gates Met</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{gates_partial}</div>
            <div class="stat-label">Partially Met</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{gates_not_met}</div>
            <div class="stat-label">Not Met</div>
        </div>
    </div>
    
    <h3>Overall Compliance</h3>
    <div class="compliance-bar">
        <div class="compliance-fill" style="width: {compliance_percentage:.1f}%"></div>
    </div>
    <p><strong>{compliance_percentage:.1f}% Hard Gates Compliance</strong></p>
"""

    # Technology Stack section
    tech_stack = assessment_results.get("technology_stack", {})
    if tech_stack:
        html_content += """
    <h2>Technology Stack</h2>
    <table>
        <thead>
            <tr>
                <th>Type</th>
                <th>Name</th>
                <th>Version</th>
                <th>Purpose</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for tech_type in ["languages", "frameworks", "databases"]:
            items = tech_stack.get(tech_type, [])
            for item in items:
                if isinstance(item, dict):
                    html_content += f"""
            <tr>
                <td><strong>{tech_type.capitalize()}</strong></td>
                <td>{item.get('name', 'Unknown')}</td>
                <td>{item.get('version', 'N/A')}</td>
                <td>{item.get('purpose', 'N/A')}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
"""

    # Hard Gates Analysis section
    html_content += """
    <h2>Hard Gates Analysis</h2>
"""
    
    if security_quality:
        for category, practices in security_quality.items():
            if not isinstance(practices, dict):
                continue
                
            category_display = category.replace("_", " ").title()
            html_content += f"""
    <h3>{category_display}</h3>
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
            
            for practice, details in practices.items():
                if not isinstance(details, dict):
                    continue
                    
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

    # Findings section
    findings = assessment_results.get("findings", [])
    if findings:
        html_content += """
    <h2>Code Analysis Findings</h2>
    <table>
        <thead>
            <tr>
                <th>Category</th>
                <th>Severity</th>
                <th>Description</th>
                <th>Location</th>
                <th>Recommendation</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for finding in findings:
            if isinstance(finding, dict):
                html_content += f"""
            <tr>
                <td>{finding.get('category', 'N/A').title()}</td>
                <td>{finding.get('severity', 'N/A').title()}</td>
                <td>{finding.get('description', 'N/A')}</td>
                <td>{finding.get('location', 'N/A')}</td>
                <td>{finding.get('recommendation', 'N/A')}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
"""

    html_content += f"""
    <footer style="margin-top: 50px; text-align: center; color: #6b7280; border-top: 1px solid #e5e7eb; padding-top: 20px;">
        <p>Hard Gate Assessment Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </footer>
</body>
</html>"""

    return html_content

if __name__ == "__main__":
    # Test the formatters
    test_data = {
        "technology_stack": {
            "languages": [{"name": "Python", "version": "3.9+", "purpose": "main application"}],
            "frameworks": [{"name": "FastAPI", "version": "0.68+", "purpose": "web framework"}],
            "databases": [{"name": "PostgreSQL", "version": "13+", "purpose": "data storage"}]
        },
        "security_quality_analysis": {
            "security": {
                "input_validation": {
                    "implemented": "no",
                    "evidence": "No validation found",
                    "recommendation": "Add input validation"
                }
            }
        },
        "findings": [
            {
                "category": "security",
                "severity": "high",
                "description": "Missing input validation",
                "location": "app.py:25",
                "recommendation": "Add validation middleware"
            }
        ]
    }
    
    # Test JSON format
    json_result = format_as_json(test_data, "Test Project")
    print("JSON Format:")
    print(json.dumps(json_result, indent=2))
    
    # Test table format
    table_result = format_for_table(test_data, "Test Project")
    print("\nTable Format:")
    print(f"Generated {len(table_result)} table rows")
    
    # Test HTML format
    html_result = generate_html_report(test_data, "Test Project")
    print(f"\nHTML Format: Generated {len(html_result)} characters") 