from core.flow import Node
from utils.formatters import format_as_json, format_for_table, generate_html_report

class FormatOutput(Node):
    def prep(self, shared):
        """
        Read assessment results and output format preference from shared store.
        """
        assessment_results = shared.get("assessment_results", {})
        project_name = shared.get("project_name", "Unknown Project")
        output_format = shared.get("output_format", "json")
        
        if not assessment_results:
            raise ValueError("No assessment results found. Analysis may have failed.")
        
        return assessment_results, project_name, output_format
    
    def exec(self, prep_res):
        """
        Format the assessment results according to the requested output format.
        """
        assessment_results, project_name, output_format = prep_res
        
        print(f"Formatting output as {output_format}...")
        
        try:
            if output_format == "json":
                formatted_output = format_as_json(assessment_results, project_name)
            elif output_format == "html":
                formatted_output = generate_html_report(assessment_results, project_name)
            elif output_format == "table":
                formatted_output = format_for_table(assessment_results, project_name)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
            
            return formatted_output
            
        except Exception as e:
            print(f"Error formatting output: {str(e)}")
            # Return a fallback JSON format
            return {
                "error": f"Failed to format output as {output_format}",
                "format_error": str(e),
                "raw_results": assessment_results
            }
    
    def post(self, shared, prep_res, exec_res):
        """
        Store the formatted output in shared store.
        """
        assessment_results, project_name, output_format = prep_res
        formatted_output = exec_res
        
        # Store the formatted output
        shared["formatted_output"] = formatted_output
        
        print(f"Output successfully formatted as {output_format}")
        
        # If HTML format, provide additional info about the report
        if output_format == "html" and isinstance(formatted_output, str):
            print(f"HTML report generated: {len(formatted_output)} characters")
        elif output_format == "table" and isinstance(formatted_output, list):
            print(f"Table data generated: {len(formatted_output)} rows")
        elif output_format == "json" and isinstance(formatted_output, dict):
            print(f"JSON response prepared with {len(formatted_output.get('results', {}))} result categories")
        
        return "default"

if __name__ == "__main__":
    # Test the node with sample data
    sample_assessment = {
        "technology_stack": {
            "languages": [{"name": "Python", "version": "3.9+", "purpose": "main application"}]
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
    shared = {
        "assessment_results": sample_assessment,
        "project_name": "Test Project",
        "output_format": "json"
    }
    
    node = FormatOutput()
    try:
        result = node.run(shared)
        print(f"JSON Result: {result}")
        print(f"Formatted output type: {type(shared.get('formatted_output'))}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test HTML format
    shared["output_format"] = "html"
    try:
        result = node.run(shared)
        print(f"HTML Result length: {len(shared.get('formatted_output', ''))}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test table format
    shared["output_format"] = "table"
    try:
        result = node.run(shared)
        print(f"Table Result rows: {len(shared.get('formatted_output', []))}")
    except Exception as e:
        print(f"Error: {e}") 