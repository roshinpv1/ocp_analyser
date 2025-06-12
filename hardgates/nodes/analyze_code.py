import os
import json
from core.flow import Node
from utils.llm_client import call_llm

class AnalyzeCode(Node):
    def prep(self, shared):
        """
        Read files data and project information from shared store.
        """
        files_data = shared.get("files_data", {})
        project_name = shared.get("project_name", "Unknown Project")
        
        if not files_data:
            raise ValueError("No files data found. Repository fetch may have failed.")
        
        # Create context for LLM analysis
        context = self._create_llm_context(files_data)
        file_count = len(files_data)
        
        return context, file_count, project_name
    
    def _create_llm_context(self, files_data):
        """
        Create formatted context from files data for LLM analysis.
        """
        context_parts = []
        
        # Sort files by extension to group similar files together
        sorted_files = sorted(files_data.items(), key=lambda x: os.path.splitext(x[0])[1])
        
        # Add file snippets to provide context (limit to first 20 files)
        file_count = 0
        for file_path, file_content in sorted_files:
            if file_count >= 20:
                break
                
            # Skip very large files for context
            if len(file_content) > 5000:
                continue
                
            # Truncate very large files
            if len(file_content) > 3000:
                file_content = file_content[:1500] + "\n...\n" + file_content[-1500:]
                
            context_parts.append(f"File: {file_path}\n```\n{file_content}\n```\n")
            file_count += 1
            
        # Add a summary of file extensions
        extensions = {}
        for file_path in files_data.keys():
            _, ext = os.path.splitext(file_path)
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
                
        ext_summary = "\nFile Extension Summary:\n"
        for ext, count in extensions.items():
            ext_summary += f"- {ext}: {count} files\n"
            
        context_parts.append(ext_summary)
        
        return "\n".join(context_parts)
    
    def exec(self, prep_res):
        """
        Perform hard gate assessment using LLM analysis.
        """
        context, file_count, project_name = prep_res
        
        print(f"Analyzing {file_count} files for hard gate assessment...")
        
        # Create focused hard gate assessment prompt for the specific 15 items
        prompt = f"""Analyze this {project_name} codebase ({file_count} files) for the following 15 PRIMARY HARD GATES ONLY.

CODE SAMPLES:
{context[:4000]}...

ANALYZE ONLY THESE 15 PRIMARY HARD GATES WITH COMPREHENSIVE ASSESSMENT:

1. **Logs are searchable and available** - Check for logging frameworks (SLF4J, Logback, Log4j), log configuration files, log levels setup
2. **Avoid logging confidential data** - Scan for patterns like password, token, secret, api_key, credential in log statements
3. **Create audit trail logs** - Look for audit logging, business event logging, user action tracking
4. **Implement tracking ID for log messages** - Search for correlation IDs, trace IDs, MDC usage, request tracking
5. **Log REST API calls** - Check for HTTP request/response logging, API interceptors, middleware logging
6. **Log application messages** - Verify general application logging practices and structured logging
7. **Client UI errors are logged** - Look for frontend error handling, error reporting mechanisms to backend
8. **Retry Logic** - Search for retry patterns, @Retryable annotations, retry libraries (Resilience4j, Spring Retry)
9. **Set timeouts on IO operation** - Check HTTP client timeouts, database connection timeouts, external service timeouts
10. **Throttling, drop request** - Look for rate limiting, request throttling, circuit breaker patterns
11. **Set circuit breakers on outgoing requests** - Search for circuit breaker implementations (Hystrix, Resilience4j)
12. **Log system errors** - Verify exception logging in catch blocks, error handling patterns
13. **Use HTTP standard error codes** - Check REST controller response codes, error response patterns
14. **Include Client error tracking** - Look for client-side error tracking, error headers, frontend monitoring
15. **Automated Regression Testing** - Check for test files, test frameworks (JUnit, TestNG), CI/CD test automation

PROVIDE DETAILED EVIDENCE AND SPECIFIC RECOMMENDATIONS FOR EACH GATE.

Return ONLY valid JSON with this exact structure:

{{
  "technology_stack": {{
    "languages": [
      {{"name": "Java", "version": "1.8+", "purpose": "main application", "files": ["src/main/java/**"]}}
    ],
    "frameworks": [
      {{"name": "Spring", "version": "5.x", "purpose": "web framework", "files": ["various"]}}
    ],
    "databases": [
      {{"name": "MySQL", "version": "8.x", "purpose": "data storage", "files": ["config"]}}
    ]
  }},
  "findings": [
    {{
      "category": "logging",
      "severity": "medium",
      "description": "Missing tracking IDs in log messages",
      "location": "file.java:123",
      "recommendation": "Add correlation IDs to all log statements"
    }}
  ],
  "component_analysis": {{
    "logging_framework": {{"detected": "yes", "evidence": "SLF4J/Logback found in dependencies"}},
    "rest_endpoints": {{"detected": "yes", "evidence": "REST controllers found"}},
    "test_framework": {{"detected": "yes", "evidence": "JUnit tests present"}},
    "retry_library": {{"detected": "no", "evidence": "No retry patterns found"}},
    "circuit_breaker": {{"detected": "no", "evidence": "No circuit breaker implementation"}}
  }},
  "primary_hard_gates": {{
    "logs_searchable_available": {{"implemented": "yes", "evidence": "SLF4J logging configured with proper log levels", "recommendation": "Ensure log aggregation is setup for searchability"}},
    "avoid_logging_confidential_data": {{"implemented": "partial", "evidence": "Some logging patterns found but need review", "recommendation": "Audit all log statements to ensure no sensitive data like passwords, tokens, or API keys are logged"}},
    "create_audit_trail_logs": {{"implemented": "no", "evidence": "No dedicated audit logging found", "recommendation": "Implement audit trail logging for important business operations and user actions"}},
    "tracking_id_for_log_messages": {{"implemented": "no", "evidence": "No correlation IDs or MDC usage found", "recommendation": "Add MDC (Mapped Diagnostic Context) or similar for request tracking across logs"}},
    "log_rest_api_calls": {{"implemented": "partial", "evidence": "Some controller logging detected", "recommendation": "Add comprehensive API request/response logging using interceptors or filters"}},
    "log_application_messages": {{"implemented": "yes", "evidence": "Application logging present throughout codebase", "recommendation": "Standardize log levels and ensure consistent logging format"}},
    "client_ui_errors_logged": {{"implemented": "no", "evidence": "No client-side error logging mechanism found", "recommendation": "Implement frontend error reporting mechanism to send client errors to backend logging"}},
    "retry_logic": {{"implemented": "no", "evidence": "No retry patterns or libraries found", "recommendation": "Implement retry logic for external service calls using Spring Retry or Resilience4j"}},
    "set_timeouts_io_operations": {{"implemented": "partial", "evidence": "Some timeout configurations found", "recommendation": "Ensure all IO operations (HTTP clients, DB connections) have appropriate timeout settings"}},
    "throttling_drop_request": {{"implemented": "no", "evidence": "No rate limiting or throttling mechanisms found", "recommendation": "Implement request throttling and rate limiting to protect against abuse"}},
    "circuit_breakers_outgoing_requests": {{"implemented": "no", "evidence": "No circuit breaker patterns found", "recommendation": "Implement circuit breakers for external service calls to prevent cascade failures"}},
    "log_system_errors": {{"implemented": "yes", "evidence": "Exception logging found in catch blocks", "recommendation": "Ensure all exceptions are properly logged with sufficient context"}},
    "use_http_standard_error_codes": {{"implemented": "yes", "evidence": "Standard HTTP status codes used in REST controllers", "recommendation": "Continue using appropriate HTTP status codes for all API responses"}},
    "include_client_error_tracking": {{"implemented": "no", "evidence": "No client error tracking mechanism detected", "recommendation": "Add mechanism to track and log client-side errors with proper correlation to server logs"}},
    "automated_regression_testing": {{"implemented": "partial", "evidence": "Unit tests found but limited coverage", "recommendation": "Expand automated test suite to include comprehensive regression and integration tests"}}
  }}
}}

Analyze the ACTUAL CODE PATTERNS and provide SPECIFIC EVIDENCE with file paths and line numbers where possible. Give ACTIONABLE RECOMMENDATIONS for each of the 15 primary hard gates."""

        try:
            result = call_llm(prompt)
            print("LLM analysis completed successfully")
            return result
        except Exception as e:
            print(f"Error during LLM analysis: {str(e)}")
            # Return a fallback structure
            return {
                "technology_stack": {},
                "findings": [],
                "component_analysis": {},
                "primary_hard_gates": {},
                "error": str(e)
            }
    
    def post(self, shared, prep_res, exec_res):
        """
        Store analysis results in shared store.
        """
        context, file_count, project_name = prep_res
        analysis_results = exec_res
        
        # Store the complete analysis results
        shared["assessment_results"] = analysis_results
        
        # Calculate compliance for the 15 primary hard gates
        primary_gates = analysis_results.get("primary_hard_gates", {})
        if primary_gates:
            total_gates = len(primary_gates)
            gates_implemented = sum(1 for gate in primary_gates.values() 
                                  if isinstance(gate, dict) and gate.get("implemented") == "yes")
            gates_partial = sum(1 for gate in primary_gates.values() 
                              if isinstance(gate, dict) and gate.get("implemented") == "partial")
            gates_not_implemented = total_gates - gates_implemented - gates_partial
            
            compliance_percentage = ((gates_implemented + 0.5 * gates_partial) / total_gates * 100) if total_gates > 0 else 0
            
            print(f"Hard Gates Compliance: {compliance_percentage:.1f}% ({gates_implemented}/{total_gates})")
            
            # Store compliance metrics
            shared["compliance_metrics"] = {
                "total_gates": total_gates,
                "gates_implemented": gates_implemented,
                "gates_partial": gates_partial,
                "gates_not_implemented": gates_not_implemented,
                "compliance_percentage": compliance_percentage
            }
        
        print(f"Hard gate assessment completed for {project_name}")
        return "default"

if __name__ == "__main__":
    # Test the node with sample data
    sample_assessment = {
        "technology_stack": {
            "languages": [{"name": "Python", "version": "3.9+", "purpose": "main application"}]
        },
        "primary_hard_gates": {
            "logs_searchable_available": {
                "implemented": "yes",
                "evidence": "Logging configured",
                "recommendation": "Continue practice"
            },
            "avoid_logging_confidential_data": {
                "implemented": "no",
                "evidence": "No validation found",
                "recommendation": "Add input validation"
            }
        },
        "findings": [
            {
                "category": "logging",
                "severity": "high",
                "description": "Missing tracking IDs",
                "location": "app.py:25",
                "recommendation": "Add correlation IDs"
            }
        ]
    }
    
    # Test with sample data
    shared = {
        "assessment_results": sample_assessment,
        "project_name": "Test Project",
        "output_format": "json"
    }
    
    node = AnalyzeCode()
    try:
        print(f"Sample assessment structure created")
    except Exception as e:
        print(f"Error: {e}") 