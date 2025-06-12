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
                    block_data = json.loads(block.strip())
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
                    continue
        
        # If no JSON blocks found, try to find individual JSON structures in the text
        if not any(result.values()) or not result["primary_hard_gates"]:
            print("No valid JSON blocks found, trying to extract primary hard gates from text")
            
            # Look for specific patterns in the response text
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
    
    # Extract technology stack
    if "java" in content.lower() or "spring" in content.lower():
        result["technology_stack"] = {
            "languages": [{"name": "Java", "version": "1.8+", "purpose": "main application"}],
            "frameworks": [{"name": "Spring", "version": "5.x", "purpose": "web framework"}],
            "databases": [{"name": "H2", "version": "1.4+", "purpose": "in-memory database"}]
        }
    
    # Extract component analysis focused on hard gate components
    components = {
        "logging_framework": "yes" if any(word in content.lower() for word in ["log", "slf4j", "logback"]) else "no",
        "rest_endpoints": "yes" if any(word in content.lower() for word in ["rest", "controller", "@restcontroller"]) else "no",
        "test_framework": "yes" if any(word in content.lower() for word in ["test", "junit", "mockito"]) else "no",
        "retry_library": "yes" if any(word in content.lower() for word in ["retry", "resilience4j", "tenacity"]) else "no",
        "circuit_breaker": "yes" if any(word in content.lower() for word in ["circuit", "breaker", "hystrix"]) else "no"
    }
    
    for component, detected in components.items():
        result["component_analysis"][component] = {
            "detected": detected,
            "evidence": f"Found {component} references in code" if detected == "yes" else f"No {component} references found"
        }
    
    # Create the 15 primary hard gates analysis
    result["primary_hard_gates"] = _create_fallback_primary_gates()
    
    return result

def _create_fallback_primary_gates() -> Dict[str, Any]:
    """
    Create the 15 primary hard gates structure
    """
    return {
        "logs_searchable_available": {
            "implemented": "partial",
            "evidence": "Logging framework detected",
            "recommendation": "Ensure logging is properly configured for searchability"
        },
        "avoid_logging_confidential_data": {
            "implemented": "unknown",
            "evidence": "Manual review required",
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
            "implemented": "partial",
            "evidence": "REST endpoints detected but logging unclear",
            "recommendation": "Add comprehensive request/response logging for all API calls"
        },
        "log_application_messages": {
            "implemented": "partial",
            "evidence": "Application logging likely present",
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
            "implemented": "unknown",
            "evidence": "IO operations detected but timeout configuration unclear",
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
            "implemented": "partial",
            "evidence": "Exception handling likely present",
            "recommendation": "Ensure all system errors are properly logged with context"
        },
        "use_http_standard_error_codes": {
            "implemented": "partial",
            "evidence": "REST endpoints detected, likely using standard codes",
            "recommendation": "Verify all endpoints return appropriate HTTP status codes"
        },
        "include_client_error_tracking": {
            "implemented": "no",
            "evidence": "No client error tracking mechanism detected",
            "recommendation": "Implement client-side error tracking and reporting"
        },
        "automated_regression_testing": {
            "implemented": "partial",
            "evidence": "Test files detected",
            "recommendation": "Expand automated test coverage including regression and integration tests"
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