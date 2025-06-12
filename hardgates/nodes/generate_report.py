import os
import json
from datetime import datetime
from core.flow import Node

class GenerateReport(Node):
    def prep(self, shared):
        """
        Retrieve assessment results and configuration from shared store.
        """
        assessment_results = shared.get("assessment_results", {})
        project_name = shared.get("project_name", "Unknown Project")
        output_format = shared.get("output_format", "html")
        output_path = shared.get("output_path", "hardgates_assessment.html")
        
        if not assessment_results:
            raise ValueError("No assessment results found. Analysis may have failed.")
        
        return assessment_results, project_name, output_format, output_path
    
    def exec(self, prep_res):
        """
        Generate assessment report in the specified format.
        """
        assessment_results, project_name, output_format, output_path = prep_res
        
        if output_format.lower() == "html":
            return self._generate_html_report(assessment_results, project_name, output_path)
        elif output_format.lower() == "json":
            return self._generate_json_report(assessment_results, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def _generate_html_report(self, assessment_results, project_name, output_path):
        """
        Generate comprehensive HTML report for hard gates assessment using the user's template.
        Only the 15 primary hard gates count toward executive summary statistics.
        """
        from datetime import datetime
        
        # Define the 15 primary hard gates for executive summary counting
        primary_gates_keys = {
            "logs_searchable_available",
            "avoid_logging_confidential_data", 
            "create_audit_trail_logs",
            "tracking_id_for_log_messages",
            "log_rest_api_calls",
            "log_application_messages",
            "client_ui_errors_logged",
            "retry_logic",
            "set_timeouts_io_operations",
            "throttling_drop_request",
            "circuit_breakers_outgoing_requests",
            "log_system_errors",
            "use_http_standard_error_codes",
            "include_client_error_tracking",
            "automated_regression_testing"
        }
        
        # Get all assessment data
        primary_hard_gates = assessment_results.get("primary_hard_gates", {})
        security_quality_analysis = assessment_results.get("security_quality_analysis", {})
        tech_stack = assessment_results.get("technology_stack", {})
        
        # Calculate executive summary stats ONLY for the 15 primary gates
        total_primary_gates = 0
        gates_met = 0
        gates_partial = 0
        gates_not_met = 0
        
        # Count from primary_hard_gates first
        for gate_key, gate_data in primary_hard_gates.items():
            if gate_key in primary_gates_keys and isinstance(gate_data, dict):
                total_primary_gates += 1
                status = gate_data.get("implemented", "no")
                if status == "yes":
                    gates_met += 1
                elif status == "partial":
                    gates_partial += 1
                else:
                    gates_not_met += 1
        
        # If we don't have enough from primary_hard_gates, look in security_quality_analysis
        if total_primary_gates < 15:
            # Map the 15 primary gates to their likely locations in security_quality_analysis
            primary_gate_mapping = {
                "avoid_logging_confidential_data": ["auditability", "avoid_logging_confidential_data"],
                "create_audit_trail_logs": ["auditability", "create_audit_trail_logs"],
                "tracking_id_for_log_messages": ["auditability", "tracking_id_for_log_messages"],
                "log_rest_api_calls": ["auditability", "log_rest_api_calls"],
                "log_application_messages": ["auditability", "log_application_messages"],
                "client_ui_errors_logged": ["auditability", "client_ui_errors_are_logged"],
                "retry_logic": ["availability", "retry_logic"],
                "set_timeouts_io_operations": ["availability", "set_timeouts_on_io_operations"],
                "throttling_drop_request": ["availability", "throttling_drop_request"],
                "circuit_breakers_outgoing_requests": ["availability", "circuit_breakers_on_outgoing_requests"],
                "log_system_errors": ["error_handling", "log_system_errors"],
                "use_http_standard_error_codes": ["error_handling", "use_http_standard_error_codes"],
                "include_client_error_tracking": ["error_handling", "include_client_error_tracking"],
                "automated_regression_testing": ["testing", "automated_regression_testing"],
                "logs_searchable_available": ["auditability", "logs_searchable_available"]
            }
            
            for gate_key in primary_gates_keys:
                if gate_key not in primary_hard_gates:  # Not already counted
                    mapping = primary_gate_mapping.get(gate_key)
                    if mapping and len(mapping) == 2:
                        category, practice = mapping
                        gate_data = security_quality_analysis.get(category, {}).get(practice, {})
                        if isinstance(gate_data, dict):
                            total_primary_gates += 1
                            status = gate_data.get("implemented", "no")
                            if status == "yes":
                                gates_met += 1
                            elif status == "partial":
                                gates_partial += 1
                            else:
                                gates_not_met += 1
        
        # Ensure we have exactly 15 primary gates for the executive summary
        if total_primary_gates == 0:
            total_primary_gates = 15
            gates_met = 0
            gates_partial = 0
            gates_not_met = 15
        
        # Calculate compliance percentage
        compliance_percentage = ((gates_met + 0.5 * gates_partial) / total_primary_gates * 100) if total_primary_gates > 0 else 0
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Start building the HTML using the exact user template
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
            <div class="stat-number">{total_primary_gates}</div>
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
        
        # Add technology stack
        for category, items in tech_stack.items():
            if items and isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        name = item.get("name", "Unknown")
                        version = item.get("version", "Unknown")
                        purpose = item.get("purpose", "")
                        html_content += f"""
            <tr>
                <td><strong>{category.replace('_', ' ').title()}</strong></td>
                <td>{name}</td>
                <td>{version}</td>
                <td>{purpose}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>

    <h2>Hard Gates Analysis</h2>
"""
        
        # Helper function to get practice data from either source
        def get_practice_data(category, practice_key, alt_key=None):
            # Try primary_hard_gates first
            if practice_key in primary_hard_gates:
                return primary_hard_gates[practice_key]
            
            # Handle special key mappings for the 15 primary gates
            special_mappings = {
                "client_ui_errors_logged": "client_ui_errors_are_logged",
                "set_timeouts_io_operations": "set_timeouts_on_io_operations", 
                "circuit_breakers_outgoing_requests": "circuit_breakers_on_outgoing_requests",
                "throttling_drop_request": "throttling_drop_request",
                "logs_searchable_available": "logs_searchable_available"
            }
            
            # Try with special mapping
            mapped_key = special_mappings.get(practice_key)
            if mapped_key and mapped_key in primary_hard_gates:
                return primary_hard_gates[mapped_key]
            
            # Try security_quality_analysis with original key
            practice_data = security_quality_analysis.get(category, {}).get(practice_key, {})
            if practice_data:
                return practice_data
            
            # Try security_quality_analysis with mapped key
            if mapped_key:
                practice_data = security_quality_analysis.get(category, {}).get(mapped_key, {})
                if practice_data:
                    return practice_data
            
            # Return empty dict if not found
            return {}
        
        def format_status(status):
            if status == "yes":
                return '<span class="status-implemented">✓ Implemented</span>'
            elif status == "partial":
                return '<span class="status-partial">⚬ Partial</span>'
            else:
                return '<span class="status-not-implemented">✗ Missing</span>'
        
        def format_practice_name(name):
            return name.replace('_', ' ').title()
        
        # Define all categories and their practices - ONLY THE 15 PRIMARY GATES
        categories = {
            "Auditability": [
                ("logs_searchable_available", "Logs Are Searchable And Available"),
                ("avoid_logging_confidential_data", "Avoid Logging Confidential Data"),
                ("create_audit_trail_logs", "Create Audit Trail Logs"), 
                ("tracking_id_for_log_messages", "Implement Tracking ID For Log Messages"),
                ("log_rest_api_calls", "Log REST API Calls"),
                ("log_application_messages", "Log Application Messages"),
                ("client_ui_errors_logged", "Client UI Errors Are Logged")
            ],
            "Availability": [
                ("retry_logic", "Retry Logic"),
                ("set_timeouts_io_operations", "Set Timeouts On IO Operation"),
                ("throttling_drop_request", "Throttling, Drop Request"),
                ("circuit_breakers_outgoing_requests", "Set Circuit Breakers On Outgoing Requests")
            ],
            "Error Handling": [
                ("log_system_errors", "Log System Errors"),
                ("use_http_standard_error_codes", "Use HTTP Standard Error Codes"),
                ("include_client_error_tracking", "Include Client Error Tracking")
            ],
            "Testing": [
                ("automated_regression_testing", "Automated Regression Testing")
            ]
        }
        
        # Generate sections for each category
        category_map = {
            "Auditability": "auditability",
            "Availability": "availability", 
            "Error Handling": "error_handling",
            "Testing": "testing"
        }
        
        for category_name, practices in categories.items():
            html_content += f"""
    <h3>{category_name}</h3>
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
            
            category_key = category_map.get(category_name, category_name.lower().replace(' ', '_'))
            
            for practice_key, practice_display in practices:
                practice_data = get_practice_data(category_key, practice_key)
                
                if practice_data:
                    status = practice_data.get("implemented", "no")
                    evidence = practice_data.get("evidence", "No evidence provided")
                    recommendation = practice_data.get("recommendation", "No recommendation provided")
                else:
                    status = "no"
                    evidence = "Not analyzed"
                    recommendation = "Requires manual review"
                
                html_content += f"""
            <tr>
                <td><strong>{practice_display}</strong></td>
                <td>{format_status(status)}</td>
                <td>{evidence}</td>
                <td>{recommendation}</td>
            </tr>
"""
            
            html_content += """
        </tbody>
    </table>
"""
        
        # Footer
        html_content += f"""
    <footer style="margin-top: 50px; text-align: center; color: #6b7280; border-top: 1px solid #e5e7eb; padding-top: 20px;">
        <p>Hard Gate Assessment Report generated on {timestamp}</p>
    </footer>
</body>
</html>
"""
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

    def _generate_json_report(self, assessment_results, output_path):
        """
        Generate JSON report for hard gates assessment.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(assessment_results, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def post(self, shared, prep_res, exec_res):
        """
        Store the generated report path in shared store.
        """
        assessment_results, project_name, output_format, output_path = prep_res
        generated_path = exec_res
        
        if generated_path:
            shared["report_path"] = generated_path
            print(f"Report generated successfully: {generated_path}")
        else:
            print("Failed to generate report")
        
        return "default"

if __name__ == "__main__":
    # Test the report generation
    sample_assessment = {
        "technology_stack": {
            "languages": [{"name": "Java", "version": "17", "purpose": "main application"}],
            "frameworks": [{"name": "Spring Boot", "version": "2.7.x", "purpose": "web framework"}]
        },
        "primary_hard_gates": {
            "logs_searchable_available": {
                "implemented": "yes",
                "evidence": "SLF4J logging configured",
                "recommendation": "Ensure log aggregation is setup"
            },
            "avoid_logging_confidential_data": {
                "implemented": "partial",
                "evidence": "Some logging patterns found",
                "recommendation": "Review all log statements"
            },
            "retry_logic": {
                "implemented": "no",
                "evidence": "No retry patterns found", 
                "recommendation": "Implement retry logic"
            }
        },
        "findings": [
            {
                "category": "logging",
                "severity": "medium",
                "description": "Missing tracking IDs in log messages",
                "location": "src/main/java/com/example/App.java:25",
                "recommendation": "Add correlation IDs to all log statements"
            }
        ]
    }
    
    shared = {
        "assessment_results": sample_assessment,
        "project_name": "Test Project",
        "output_format": "html",
        "output_path": "test_report.html"
    }
    
    node = GenerateReport()
    try:
        result = node.run(shared)
        print(f"Test report generated: {result}")
    except Exception as e:
        print(f"Error: {e}") 