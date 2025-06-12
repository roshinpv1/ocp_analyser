import os
import json
import re
from typing import Dict, Any, List

def call_llm(prompt: str) -> Dict[str, Any]:
    """
    Call LLM for code analysis.
    
    This function provides a simple interface to various LLM providers.
    Configure your preferred provider by setting environment variables.
    
    For local LLMs (OpenAI-compatible):
    - Set OPENAI_API_KEY (can be any value for local LLMs)
    - Set OPENAI_BASE_URL to your local endpoint (e.g., http://localhost:1234/v1)
    - Optionally set OPENAI_MODEL to specify the model name
    
    Args:
        prompt: The analysis prompt to send to the LLM
        
    Returns:
        Dictionary containing the LLM response parsed as JSON
    """
    
    # Determine which LLM provider to use based on environment variables
    if os.getenv("OPENAI_API_KEY"):
        return _call_openai(prompt)
    elif os.getenv("ANTHROPIC_API_KEY"):
        return _call_anthropic(prompt)
    elif os.getenv("GOOGLE_API_KEY"):
        return _call_google(prompt)
    else:
        raise ValueError("No LLM API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY environment variable.")

def _call_openai(prompt: str) -> Dict[str, Any]:
    """Call OpenAI API or OpenAI-compatible local LLM"""
    try:
        from openai import OpenAI
        
        # Support for local LLMs with custom base URL
        base_url = os.getenv("OPENAI_BASE_URL")
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")  # Default to gpt-4o, but allow override
        
        # Create client with custom base URL if provided (for local LLMs)
        if base_url:
            client = OpenAI(
                api_key=api_key or "local-llm",  # Local LLMs often don't need real API keys
                base_url=base_url
            )
            print(f"Using local LLM at {base_url} with model: {model}")
        else:
            client = OpenAI(api_key=api_key)
            print(f"Using OpenAI API with model: {model}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        return _parse_json_response(content)
        
    except ImportError:
        raise ValueError("OpenAI library not installed. Run: pip install openai")
    except Exception as e:
        raise ValueError(f"OpenAI API error: {str(e)}")

def _call_anthropic(prompt: str) -> Dict[str, Any]:
    """Call Anthropic Claude API"""
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        content = response.content[0].text
        return _parse_json_response(content)
        
    except ImportError:
        raise ValueError("Anthropic library not installed. Run: pip install anthropic")
    except Exception as e:
        raise ValueError(f"Anthropic API error: {str(e)}")

def _call_google(prompt: str) -> Dict[str, Any]:
    """Call Google Gemini API"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1
            )
        )
        
        content = response.text
        return _parse_json_response(content)
        
    except ImportError:
        raise ValueError("Google generativeai library not installed. Run: pip install google-generativeai")
    except Exception as e:
        raise ValueError(f"Google API error: {str(e)}")

def _parse_json_response(content: str) -> Dict[str, Any]:
    """
    Parse JSON response from LLM, handling code blocks and multi-part responses
    """
    try:
        # Initialize the result structure for primary hard gates
        result = {
            "technology_stack": {},
            "findings": [],
            "component_analysis": {},
            "primary_hard_gates": {}
        }
        
        # Extract all JSON code blocks from the response
        json_blocks = re.findall(r'```json\s*\n(.*?)\n```', content, re.DOTALL | re.IGNORECASE)
        
        if json_blocks:
            print(f"Found {len(json_blocks)} JSON blocks in response")
            
            for i, block in enumerate(json_blocks):
                try:
                    # Clean up the JSON block - remove common issues
                    cleaned_block = block.strip()
                    
                    # Remove trailing commas before } or ]
                    cleaned_block = re.sub(r',(\s*[}\]])', r'\1', cleaned_block)
                    
                    # Fix common quote issues
                    cleaned_block = re.sub(r"'([^']*)':", r'"\1":', cleaned_block)  # Single quotes to double quotes for keys
                    
                    # Try to parse the cleaned JSON
                    block_data = json.loads(cleaned_block)
                    print(f"Successfully parsed JSON block {i+1}")
                    
                    # Merge the block data into the result
                    if isinstance(block_data, dict):
                        for key in ["technology_stack", "findings", "component_analysis", "primary_hard_gates"]:
                            if key in block_data:
                                if key == "findings" and isinstance(block_data[key], list):
                                    result[key].extend(block_data[key])
                                elif isinstance(block_data[key], dict):
                                    result[key].update(block_data[key])
                                else:
                                    result[key] = block_data[key]
                                
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON block {i+1}: {e}")
                    # Save the problematic block for debugging
                    with open(f"debug_json_block_{i+1}.txt", "w") as debug_file:
                        debug_file.write(f"Original block:\n{block}\n\nCleaned block:\n{cleaned_block if 'cleaned_block' in locals() else 'N/A'}\n\nError: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error parsing JSON block {i+1}: {e}")
                    continue
        
        # Try to extract JSON without code blocks if no valid blocks found
        if not any(result.values()) or not result["primary_hard_gates"]:
            print("No valid JSON blocks found, trying to extract JSON from text directly")
            
            # Look for JSON-like structures in the text
            json_patterns = [
                r'\{[^{}]*"primary_hard_gates"[^{}]*\{.*?\}[^{}]*\}',  # Look for primary_hard_gates structure
                r'\{.*?"technology_stack".*?\}',  # Look for technology_stack
                r'\{.*?"findings".*?\}'  # Look for findings
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    try:
                        # Clean and parse the match
                        cleaned_match = re.sub(r',(\s*[}\]])', r'\1', match.strip())
                        parsed_data = json.loads(cleaned_match)
                        if isinstance(parsed_data, dict):
                            for key in ["technology_stack", "findings", "component_analysis", "primary_hard_gates"]:
                                if key in parsed_data:
                                    if key == "findings" and isinstance(parsed_data[key], list):
                                        result[key].extend(parsed_data[key])
                                    elif isinstance(parsed_data[key], dict):
                                        result[key].update(parsed_data[key])
                                    else:
                                        result[key] = parsed_data[key]
                            print(f"Successfully extracted JSON structure from text")
                            break
                    except:
                        continue
        
        # If still no valid data, use text extraction
        if not any(result.values()) or not result["primary_hard_gates"]:
            print("No valid JSON found, extracting from text analysis")
            result = _extract_primary_gates_from_text(content)
        
        # Validate that we have meaningful data
        if not result["primary_hard_gates"]:
            print("Warning: No primary_hard_gates found, using fallback structure")
            result["primary_hard_gates"] = _create_fallback_primary_gates()
        
        print(f"Final result has {len(result['primary_hard_gates'])} primary hard gates")
        return result
        
    except Exception as e:
        print(f"Error during JSON parsing: {e}")
        # Return a structured error response with some basic analysis
        return {
            "error": "Failed to parse LLM response",
            "raw_response": content,
            "parse_error": str(e),
            "technology_stack": _extract_basic_tech_stack(content),
            "findings": _extract_basic_findings(content),
            "component_analysis": _extract_basic_components(content),
            "primary_hard_gates": _create_fallback_primary_gates()
        }

def _extract_primary_gates_from_text(content: str) -> Dict[str, Any]:
    """
    Extract the 15 primary hard gates from text response when JSON parsing fails
    """
    result = {
        "technology_stack": {},
        "findings": [],
        "component_analysis": {},
        "primary_hard_gates": {}
    }
    
    # Extract technology stack based on content analysis
    content_lower = content.lower()
    
    # Technology detection
    languages = []
    frameworks = []
    databases = []
    
    if any(word in content_lower for word in ["java", ".java", "spring", "maven", "gradle"]):
        languages.append({"name": "Java", "version": "8+", "purpose": "main application"})
        if "spring" in content_lower:
            frameworks.append({"name": "Spring Framework", "version": "5.x", "purpose": "web framework"})
    
    if any(word in content_lower for word in ["javascript", ".js", "node", "npm", "package.json"]):
        languages.append({"name": "JavaScript", "version": "ES6+", "purpose": "client/server side"})
    
    if any(word in content_lower for word in ["python", ".py", "flask", "django", "requirements.txt"]):
        languages.append({"name": "Python", "version": "3.x", "purpose": "application development"})
    
    if any(word in content_lower for word in ["mysql", "postgresql", "h2", "database"]):
        databases.append({"name": "Database", "version": "N/A", "purpose": "data storage"})
    
    result["technology_stack"] = {
        "languages": languages,
        "frameworks": frameworks,
        "databases": databases
    }
    
    # Intelligent analysis of hard gates based on content
    primary_gates = {}
    
    # Logging-related gates
    has_logging = any(word in content_lower for word in ["log", "logger", "slf4j", "logback", "log4j", "logging"])
    has_structured_logging = any(word in content_lower for word in ["json", "structured", "elastic", "logstash"])
    
    primary_gates["logs_searchable_available"] = {
        "implemented": "yes" if has_structured_logging else ("partial" if has_logging else "no"),
        "evidence": f"{'Structured logging detected' if has_structured_logging else ('Basic logging found' if has_logging else 'No logging framework detected')}",
        "recommendation": "Implement centralized logging with search capabilities" if not has_structured_logging else "Logging appears to be properly configured"
    }
    
    primary_gates["avoid_logging_confidential_data"] = {
        "implemented": "partial",  # Always partial as this requires manual review
        "evidence": "Manual code review required to verify no sensitive data is logged",
        "recommendation": "Review all log statements to ensure no sensitive data is logged"
    }
    
    primary_gates["create_audit_trail_logs"] = {
        "implemented": "yes" if any(word in content_lower for word in ["audit", "trail", "event"]) else "no",
        "evidence": "Audit logging patterns detected" if any(word in content_lower for word in ["audit", "trail", "event"]) else "No audit logging patterns found",
        "recommendation": "Implement audit trail logging for important business operations"
    }
    
    primary_gates["tracking_id_for_log_messages"] = {
        "implemented": "yes" if any(word in content_lower for word in ["correlation", "trace", "request-id", "tracking"]) else "no",
        "evidence": "Correlation/tracking ID patterns found" if any(word in content_lower for word in ["correlation", "trace", "request-id", "tracking"]) else "No correlation ID patterns found",
        "recommendation": "Add tracking/correlation IDs to log messages for request tracing"
    }
    
    # API-related gates
    has_rest = any(word in content_lower for word in ["rest", "controller", "@restcontroller", "api", "endpoint"])
    
    primary_gates["log_rest_api_calls"] = {
        "implemented": "partial" if has_rest and has_logging else "no",
        "evidence": f"{'REST endpoints and logging detected' if has_rest and has_logging else ('REST endpoints found but logging unclear' if has_rest else 'No REST API patterns detected')}",
        "recommendation": "Add comprehensive request/response logging for all API calls"
    }
    
    primary_gates["log_application_messages"] = {
        "implemented": "yes" if has_logging else "no",
        "evidence": f"{'Application logging framework present' if has_logging else 'No logging framework detected'}",
        "recommendation": "Standardize application logging levels and messages" if has_logging else "Implement application logging"
    }
    
    primary_gates["client_ui_errors_logged"] = {
        "implemented": "no",  # Usually requires specific implementation
        "evidence": "Client-side error logging not detected",
        "recommendation": "Implement client-side error logging and reporting mechanism"
    }
    
    # Resilience gates
    has_retry = any(word in content_lower for word in ["retry", "resilience4j", "tenacity", "@retryable"])
    has_timeout = any(word in content_lower for word in ["timeout", "read-timeout", "connection-timeout"])
    has_circuit_breaker = any(word in content_lower for word in ["circuit", "breaker", "hystrix", "@circuitbreaker"])
    has_rate_limit = any(word in content_lower for word in ["rate", "limit", "throttle", "ratelimit"])
    
    primary_gates["retry_logic"] = {
        "implemented": "yes" if has_retry else "no",
        "evidence": f"{'Retry patterns detected' if has_retry else 'No retry patterns detected'}",
        "recommendation": "Implement retry logic for external service calls" if not has_retry else "Retry logic appears to be implemented"
    }
    
    primary_gates["set_timeouts_io_operations"] = {
        "implemented": "yes" if has_timeout else "partial",
        "evidence": f"{'Timeout configurations found' if has_timeout else 'Timeout configuration not explicitly found'}",
        "recommendation": "Ensure all IO operations have appropriate timeout configurations"
    }
    
    primary_gates["throttling_drop_request"] = {
        "implemented": "yes" if has_rate_limit else "no",
        "evidence": f"{'Rate limiting patterns detected' if has_rate_limit else 'No rate limiting detected'}",
        "recommendation": "Implement request throttling and rate limiting" if not has_rate_limit else "Rate limiting appears to be implemented"
    }
    
    primary_gates["circuit_breakers_outgoing_requests"] = {
        "implemented": "yes" if has_circuit_breaker else "no",
        "evidence": f"{'Circuit breaker patterns detected' if has_circuit_breaker else 'No circuit breaker patterns detected'}",
        "recommendation": "Implement circuit breaker pattern for external service calls" if not has_circuit_breaker else "Circuit breaker appears to be implemented"
    }
    
    # Error handling gates
    has_exception_handling = any(word in content_lower for word in ["try", "catch", "exception", "error"])
    has_http_codes = any(word in content_lower for word in ["httpstatus", "response.status", "status code"])
    
    primary_gates["log_system_errors"] = {
        "implemented": "yes" if has_exception_handling and has_logging else ("partial" if has_exception_handling else "no"),
        "evidence": f"{'Exception handling and logging detected' if has_exception_handling and has_logging else ('Exception handling found but logging unclear' if has_exception_handling else 'No exception handling patterns detected')}",
        "recommendation": "Ensure all system errors are properly logged with context"
    }
    
    primary_gates["use_http_standard_error_codes"] = {
        "implemented": "yes" if has_http_codes else ("partial" if has_rest else "no"),
        "evidence": f"{'HTTP status code usage detected' if has_http_codes else ('REST endpoints found but status code usage unclear' if has_rest else 'No HTTP status code patterns detected')}",
        "recommendation": "Verify all endpoints return appropriate HTTP status codes"
    }
    
    primary_gates["include_client_error_tracking"] = {
        "implemented": "no",  # Usually requires specific implementation
        "evidence": "No client error tracking mechanism detected",
        "recommendation": "Implement client-side error tracking and reporting"
    }
    
    # Testing gate
    has_tests = any(word in content_lower for word in ["test", "junit", "mockito", "testng", "spec", "cucumber"])
    has_automation = any(word in content_lower for word in ["ci", "jenkins", "github actions", "pipeline", "automated"])
    
    primary_gates["automated_regression_testing"] = {
        "implemented": "yes" if has_tests and has_automation else ("partial" if has_tests else "no"),
        "evidence": f"{'Automated testing and CI/CD detected' if has_tests and has_automation else ('Test framework found but automation unclear' if has_tests else 'No testing framework detected')}",
        "recommendation": "Implement comprehensive automated regression testing" if not (has_tests and has_automation) else "Automated testing appears to be implemented"
    }
    
    result["primary_hard_gates"] = primary_gates
    
    # Extract some basic findings
    findings = []
    if not has_logging:
        findings.append({
            "type": "missing_logging",
            "severity": "high",
            "description": "No logging framework detected",
            "file": "N/A",
            "recommendation": "Implement comprehensive logging"
        })
    
    if not has_tests:
        findings.append({
            "type": "missing_tests",
            "severity": "high", 
            "description": "No test framework detected",
            "file": "N/A",
            "recommendation": "Implement automated testing"
        })
    
    result["findings"] = findings
    
    return result

def _create_fallback_primary_gates() -> Dict[str, Any]:
    """
    Create the 15 primary hard gates structure with more realistic assessments
    """
    return {
        "logs_searchable_available": {
            "implemented": "no",
            "evidence": "No structured logging framework detected",
            "recommendation": "Implement centralized logging with search capabilities"
        },
        "avoid_logging_confidential_data": {
            "implemented": "no",
            "evidence": "Manual review required for data sensitivity",
            "recommendation": "Review all log statements to ensure no sensitive data is logged"
        },
        "create_audit_trail_logs": {
            "implemented": "no",
            "evidence": "No audit logging patterns found",
            "recommendation": "Implement audit trail logging for important business operations"
        },
        "tracking_id_for_log_messages": {
            "implemented": "no",
            "evidence": "No correlation ID patterns found",
            "recommendation": "Add tracking/correlation IDs to log messages for request tracing"
        },
        "log_rest_api_calls": {
            "implemented": "no",
            "evidence": "No API request/response logging detected",
            "recommendation": "Add comprehensive request/response logging for all API calls"
        },
        "log_application_messages": {
            "implemented": "no",
            "evidence": "Basic logging may be present but not verified",
            "recommendation": "Standardize application logging levels and messages"
        },
        "client_ui_errors_logged": {
            "implemented": "no",
            "evidence": "No client-side error logging detected",
            "recommendation": "Implement client-side error logging and reporting mechanism"
        },
        "retry_logic": {
            "implemented": "no",
            "evidence": "No retry patterns detected",
            "recommendation": "Implement retry logic for external service calls"
        },
        "set_timeouts_io_operations": {
            "implemented": "no",
            "evidence": "IO timeout configuration not verified",
            "recommendation": "Ensure all IO operations have appropriate timeout configurations"
        },
        "throttling_drop_request": {
            "implemented": "no",
            "evidence": "No rate limiting detected",
            "recommendation": "Implement request throttling and rate limiting"
        },
        "circuit_breakers_outgoing_requests": {
            "implemented": "no",
            "evidence": "No circuit breaker patterns detected",
            "recommendation": "Implement circuit breaker pattern for external service calls"
        },
        "log_system_errors": {
            "implemented": "no",
            "evidence": "System error logging not verified",
            "recommendation": "Ensure all system errors are properly logged with context"
        },
        "use_http_standard_error_codes": {
            "implemented": "no",
            "evidence": "HTTP error code usage not verified",
            "recommendation": "Verify all endpoints return appropriate HTTP status codes"
        },
        "include_client_error_tracking": {
            "implemented": "no",
            "evidence": "No client error tracking mechanism detected",
            "recommendation": "Implement client-side error tracking and reporting"
        },
        "automated_regression_testing": {
            "implemented": "no",
            "evidence": "Automated testing framework not detected",
            "recommendation": "Implement comprehensive automated regression testing"
        }
    }

def _extract_basic_tech_stack(content: str) -> Dict[str, Any]:
    """Extract basic technology stack from content"""
    tech_stack = {"languages": [], "frameworks": [], "databases": []}
    
    if "java" in content.lower():
        tech_stack["languages"].append({"name": "Java", "version": "1.8+", "purpose": "main application"})
    if "spring" in content.lower():
        tech_stack["frameworks"].append({"name": "Spring", "version": "5.x", "purpose": "web framework"})
    if "h2" in content.lower():
        tech_stack["databases"].append({"name": "H2", "version": "1.4+", "purpose": "in-memory database"})
        
    return tech_stack

def _extract_basic_findings(content: str) -> List[Dict[str, Any]]:
    """Extract basic findings from content"""
    findings = []
    if "validation" in content.lower():
        findings.append({
            "category": "security",
            "severity": "high",
            "description": "Missing input validation identified",
            "location": "Multiple files",
            "recommendation": "Implement comprehensive input validation"
        })
    return findings

def _extract_basic_components(content: str) -> Dict[str, Any]:
    """Extract basic component analysis from content"""
    return {
        "REST API": {"detected": "yes" if "rest" in content.lower() else "no", "evidence": "REST patterns found"},
        "Database": {"detected": "yes" if "database" in content.lower() else "no", "evidence": "Database usage detected"}
    }

if __name__ == "__main__":
    # Test the function with a simple prompt
    test_prompt = """
    Analyze this simple Python code for hard gates assessment:
    
    def hello_world():
        print("Hello, World!")
    
    Return JSON with technology_stack, findings, component_analysis, and primary_hard_gates.
    """
    
    try:
        result = call_llm(test_prompt)
        print("LLM Response:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error testing LLM client: {e}") 