import os
import re
import json
from core.genflow import Node
from utils.call_llm import call_llm

class AnalyzeCode(Node):
    def prep(self, shared):
        # Get the files data from the FetchRepo node
        files_data = shared.get("files_data", {})
        
        # Get project name
        project_name = shared.get("project_name", "Unknown Project")
        
        # Get caching preference
        use_cache = shared.get("use_cache", True)
        
        # Build a file content map for validation later
        file_content_map = {}
        for file_path, file_content in files_data.items():
            file_content_map[file_path] = file_content
            
        # Generate a file listing for the LLM
        file_listing = []
        for file_path, file_content in files_data.items():
            file_size = len(file_content)
            file_listing.append(f"{file_path} ({file_size} bytes)")
            
        # Extract component questions from Excel validation (if available)
        component_questions = shared.get("excel_validation", {}).get("component_questions", None)
        
        # Create context for LLM
        context = self.create_llm_context(files_data)
        
        return context, file_listing, len(files_data), project_name, use_cache, file_content_map, component_questions
    
    def create_llm_context(self, files_data):
        # Extract content and create a summary
        context_parts = []
        
        # Add file snippets to provide context
        file_count = 0
        for file_path, file_content in files_data.items():
            # Limit to first 10 files to keep context manageable
            if file_count >= 10:
                break
                
            # Truncate very large files
            if len(file_content) > 3000:
                file_content = file_content[:1500] + "\n...\n" + file_content[-1500:]
                
            context_parts.append(f"File: {file_path}\n```\n{file_content}\n```\n")
            file_count += 1
            
        # Add a summary of other files by extension
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
        context, file_listing, file_count, project_name, use_cache, file_content_map, component_questions = prep_res
        print(f"Analyzing code for comprehensive review...")

        # Check if there are any files to analyze
        if file_count == 0:
            print("WARNING: No files found to analyze. Skipping code analysis.")
            return {
                "technology_stack": {},
                "findings": [],
                "component_analysis": {},
                "security_quality_analysis": {},
                "error": "No files to analyze"
            }

        # Create a list of components to check for in the codebase
        component_check_list = """
1. Venafi
2. Redis
3. Channel Secure / PingFed
4. NAS / SMB
5. SMTP
6. AutoSys
7. CRON/quartz/spring batch
8. MTLS / Mutual Auth / Hard Rock pattern
9. NDM
10. Legacy JKS files
11. SOAP Calls
12. REST API
13. APIGEE
14. KAFKA
15. IBM MQ
16. LDAP
17. Splunk
18. AppD / AppDynamics
19. ELASTIC APM
20. Harness or UCD for CI/CD
21. Hashicorp vault
22. Bridge Utility server
23. RabbitMQ
24. Databases:
   - MongoDB
   - SQLServer
   - MySQL
   - PostgreSQL
   - Oracle
   - Cassandra
   - Couchbase
   - Neo4j
   - Hadoop
   - Spark
25. Authentication methods:
   - Okta
   - SAML
   - Auth
   - JWT
   - OpenID
   - ADFS
"""
        
        # Create a prompt for the LLM to analyze the code
        prompt = f"""You are a software engineering consultant with expertise in code assessment, security reviews, and architecture analysis. Your current task is to analyze the codebase for a project called "{project_name}" and assess it for:

1. Technology stack identification
2. Component detection vs the component declared in the excel sheet provided by the user.
3. Quality and resiliency issues
4. Security findings
5. OpenShift migration readiness 

The project has {file_count} files. Here is a list of the files:
{file_listing[:20]}
...
{file_listing[-20:] if len(file_listing) > 20 else ""}

I will provide you with some code samples and information about the project. Based on this information, you will need to:

1. Identify the technologies and frameworks being used (languages, frameworks, libraries, databases, etc.)
2. Detect specific components that are used. Please check for the following components:
{component_check_list}

3. Analyze the code for quality, resiliency, observability issues, and security vulnerabilities
4. Provide an assessment of the code's readiness for migration to OpenShift

Please provide your analysis in the following JSON format:

```json
{{
  "technology_stack": {{
    "languages": [
      {{ "name": "language name", "version": "version if available", "purpose": "what it's used for", "files": ["file paths"] }}
    ],
    "frameworks": [
      {{ "name": "framework name", "version": "version if available", "purpose": "what it's used for", "files": ["file paths"] }}
    ],
    "libraries": [
      {{ "name": "library name", "version": "version if available", "purpose": "what it's used for", "files": ["file paths"] }}
    ],
    "databases": [
      {{ "name": "database name", "version": "version if available", "purpose": "what it's used for", "files": ["file paths"] }}
    ],
    "infrastructure": [
      {{ "name": "infrastructure component", "version": "version if available", "purpose": "what it's used for", "files": ["file paths"] }}
    ]
  }},
  "findings": [
    {{
      "category": "one of: security, quality, resiliency, observability, openshift-readiness",
      "severity": "one of: critical, high, medium, low",
      "description": "detailed description of the issue",
      "location": {{
        "file": "file path",
        "line": line number,
        "code": "code snippet"
      }},
      "recommendation": "how to fix the issue"
    }}
  ],
  "component_analysis": {{
    "Venafi": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Redis": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Channel Secure / PingFed": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "NAS / SMB": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "SMTP": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "AutoSys": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "CRON/quartz/spring batch": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "MTLS / Mutual Auth / Hard Rock pattern": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "NDM": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Legacy JKS files": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "SOAP Calls": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "REST API": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "APIGEE": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "KAFKA": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "IBM MQ": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "LDAP": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Splunk": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "AppD / AppDynamics": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "ELASTIC APM": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Harness or UCD for CI/CD": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Hashicorp vault": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Bridge Utility server": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "RabbitMQ": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "MongoDB": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "SQLServer": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "MySQL": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "PostgreSQL": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Oracle": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Cassandra": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Couchbase": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Neo4j": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Hadoop": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Spark": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Okta": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "SAML": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "Auth": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "JWT": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "OpenID": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }},
    "ADFS": {{ "detected": "yes/no", "evidence": "evidence of detection or lack thereof" }}
  }},
  "security_quality_analysis": {{
    "auditability": {{
      "avoid_logging_confidential_data": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "create_audit_trail_logs": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "tracking_id_for_log_messages": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "log_rest_api_calls": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "log_application_messages": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "client_ui_errors_are_logged": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }}
    }},
    "availability": {{
      "retry_logic": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "set_timeouts_on_io_operations": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "throttling_drop_request": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "circuit_breakers_on_outgoing_requests": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }}
    }},
    "error_handling": {{
      "log_system_errors": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "use_http_standard_error_codes": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }},
      "include_client_error_tracking": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }}
    }},
    "monitoring": {{
      "url_monitoring": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }}
    }},
    "testing": {{
      "automated_regression_testing": {{ "implemented": "yes/no/partial", "evidence": "evidence", "recommendation": "recommendation" }}
    }}
  }}
}}
```

Here are some code samples from the project to help with your analysis:

{context}

Remember, if you cannot detect a component with high confidence, mark it as "no" in the component_analysis section. If you don't find enough information to assess a security or quality practice, default to "no" for the implemented field. Focus on accuracy in your analysis.

Also, if you find any additional components or technology stack items not explicitly mentioned in the component list, please include them in your analysis.
"""

        try:
            # Call LLM with the analysis prompt
            response = call_llm(prompt, use_cache=use_cache)
            
            # Extract and parse JSON from response
            try:
                # Clean the response - remove any non-JSON content
                response = response.strip()
                
                # Find the first { and last }
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx == -1 or end_idx == 0:
                    print("Warning: No JSON object found in response. Returning empty findings.")
                    print("Response was:", response)
                    return {"technology_stack": {}, "findings": [], "component_analysis": {}, "security_quality_analysis": {}}
                    
                json_str = response[start_idx:end_idx]
                
                # Remove any comments from the JSON string
                json_str = re.sub(r'//.*?\n', '\n', json_str)
                
                # Try to parse the JSON
                try:
                    analysis = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse JSON response: {str(e)}")
                    print("JSON string was:", json_str)
                    return {"technology_stack": {}, "findings": [], "component_analysis": {}, "security_quality_analysis": {}}
                
                # Validate analysis structure
                if not isinstance(analysis, dict):
                    print("Warning: Response is not a dictionary. Returning empty findings.")
                    print("Response was:", analysis)
                    return {"technology_stack": {}, "findings": [], "component_analysis": {}, "security_quality_analysis": {}}
                    
                # Ensure technology_stack exists and is a dict
                if "technology_stack" not in analysis or not isinstance(analysis["technology_stack"], dict):
                    analysis["technology_stack"] = {}
                    
                # Ensure findings exists and is a list
                if "findings" not in analysis or not isinstance(analysis["findings"], list):
                    analysis["findings"] = []
                    
                # Ensure component_analysis exists and is a dict
                if "component_analysis" not in analysis or not isinstance(analysis["component_analysis"], dict):
                    analysis["component_analysis"] = {}
                    
                # Ensure security_quality_analysis exists and is a dict
                if "security_quality_analysis" not in analysis or not isinstance(analysis["security_quality_analysis"], dict):
                    analysis["security_quality_analysis"] = {}
                
                # Add Excel component questions to analysis result
                if component_questions:
                    analysis["excel_components"] = component_questions
                
                # Validate and clean up technology stack
                validated_tech_stack = {}
                for category, techs in analysis["technology_stack"].items():
                    if not isinstance(techs, list):
                        continue
                        
                    validated_techs = []
                    for tech in techs:
                        if not isinstance(tech, dict):
                            continue
                            
                        # Ensure required fields exist
                        if "name" not in tech:
                            continue
                            
                        # Add missing fields with defaults
                        tech = {
                            "name": tech["name"],
                            "version": tech.get("version", "unknown"),
                            "purpose": tech.get("purpose", "N/A"),
                            "files": tech.get("files", [])
                        }
                        
                        # Validate files exist
                        valid_files = []
                        for file_path in tech["files"]:
                            if file_path in file_content_map:
                                valid_files.append(file_path)
                        
                        tech["files"] = valid_files
                        validated_techs.append(tech)
                    
                    if validated_techs:
                        validated_tech_stack[category] = validated_techs
                
                # Validate findings
                validated_findings = []
                for finding in analysis["findings"]:
                    if not isinstance(finding, dict):
                        continue
                        
                    # Check required fields
                    if not all(k in finding for k in ["category", "severity", "description", "location", "recommendation"]):
                        continue
                        
                    # Validate location
                    location = finding["location"]
                    if not isinstance(location, dict) or not all(k in location for k in ["file", "line", "code"]):
                        continue
                        
                    # Validate types
                    if not isinstance(finding["category"], str) or \
                       not isinstance(finding["severity"], str) or \
                       not isinstance(finding["description"], str) or \
                       not isinstance(finding["recommendation"], str) or \
                       not isinstance(location["file"], str) or \
                       not isinstance(location["code"], str):
                        continue
                        
                    # Convert line to int if it's a string
                    try:
                        location["line"] = int(location["line"])
                    except (ValueError, TypeError):
                        continue
                    
                    # Validate file exists and line number is valid
                    file_path = location["file"]
                    if file_path not in file_content_map:
                        continue
                        
                    file_content = file_content_map[file_path]
                    file_lines = file_content.split('\n')
                    
                    if not (0 <= location["line"] < len(file_lines)):
                        continue
                    
                    # Validate code snippet matches the actual line
                    actual_line = file_lines[location["line"]].strip()
                    reported_snippet = location["code"].strip()
                    
                    if reported_snippet not in actual_line:
                        continue
                            
                    validated_findings.append(finding)
                
                # Validate component analysis
                validated_component_analysis = {}
                for component, analysis_data in analysis.get("component_analysis", {}).items():
                    if not isinstance(analysis_data, dict):
                        continue
                    
                    if "detected" not in analysis_data:
                        continue
                    
                    detected = analysis_data["detected"].lower()
                    if detected not in ["yes", "no"]:
                        detected = "no"
                    
                    evidence = analysis_data.get("evidence", "No evidence provided")
                    
                    validated_component_analysis[component] = {
                        "detected": detected,
                        "evidence": evidence
                    }
                
                # Validate security and quality analysis
                validated_security_quality = {}
                
                # Define expected categories and practices
                expected_security_structure = {
                    "auditability": [
                        "avoid_logging_confidential_data",
                        "create_audit_trail_logs",
                        "tracking_id_for_log_messages",
                        "log_rest_api_calls",
                        "log_application_messages",
                        "client_ui_errors_are_logged"
                    ],
                    "availability": [
                        "retry_logic",
                        "set_timeouts_on_io_operations",
                        "throttling_drop_request",
                        "circuit_breakers_on_outgoing_requests"
                    ],
                    "error_handling": [
                        "log_system_errors",
                        "use_http_standard_error_codes",
                        "include_client_error_tracking"
                    ],
                    "monitoring": [
                        "url_monitoring"
                    ],
                    "testing": [
                        "automated_regression_testing"
                    ]
                }
                
                security_quality = analysis.get("security_quality_analysis", {})
                
                # For each expected category, validate the practices
                for category, practices in expected_security_structure.items():
                    category_data = security_quality.get(category, {})
                    validated_practices = {}
                    
                    for practice in practices:
                        practice_data = category_data.get(practice, {})
                        
                        if not isinstance(practice_data, dict):
                            practice_data = {
                                "implemented": "no",
                                "evidence": "Not analyzed",
                                "recommendation": "Implement this practice"
                            }
                        
                        # Ensure all required fields are present
                        implemented = practice_data.get("implemented", "no").lower()
                        if implemented not in ["yes", "no", "partial"]:
                            implemented = "no"
                            
                        evidence = practice_data.get("evidence", "No evidence provided")
                        recommendation = practice_data.get("recommendation", "Implement this practice")
                        
                        validated_practices[practice] = {
                            "implemented": implemented,
                            "evidence": evidence,
                            "recommendation": recommendation
                        }
                    
                    validated_security_quality[category] = validated_practices
                
                print(f"Found {sum(len(techs) for techs in validated_tech_stack.values())} technologies, {len(validated_findings)} findings, and {len(validated_component_analysis)} components.")
                print(f"Analyzed {len(validated_security_quality)} security and quality categories.")
                
                # Compare component analysis from code with Excel answers
                if component_questions:
                    print("\nComparing components found in code with Excel declarations:")
                    for component_name, data in validated_component_analysis.items():
                        for excel_comp, excel_data in component_questions.items():
                            if component_name.lower() in excel_comp.lower() or excel_comp.lower() in component_name.lower():
                                excel_answer = "Yes" if excel_data.get("is_yes", False) else "No"
                                code_answer = "Yes" if data["detected"].lower() == "yes" else "No"
                                match_str = "MATCH" if excel_answer == code_answer else "MISMATCH"
                                print(f"- {component_name}: Excel={excel_answer}, Code={code_answer} => {match_str}")
                
                return {
                    "technology_stack": validated_tech_stack,
                    "findings": validated_findings,
                    "component_analysis": validated_component_analysis,
                    "excel_components": component_questions if component_questions else {},
                    "security_quality_analysis": validated_security_quality
                }
                
            except Exception as e:
                print(f"Warning: Unexpected error processing response: {str(e)}")
                print("Response was:", response)
                return {"technology_stack": {}, "findings": [], "component_analysis": {}, "security_quality_analysis": {}}
        
        except Exception as e:
            print(f"Error in code analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"technology_stack": {}, "findings": [], "component_analysis": {}, "security_quality_analysis": {}}

    def post(self, shared, prep_res, exec_res):
        print("\nDEBUG: AnalyzeCode post")
        
        # Check if we encountered an error during analysis
        if "error" in exec_res:
            error_msg = exec_res.get("error", "Unknown error")
            print(f"WARNING: Analysis completed with errors: {error_msg}")
            
            # If we've reached max retries, provide a clear message rather than retrying again
            max_retry_reached = hasattr(self, 'cur_retry') and self.cur_retry >= (self.max_retries - 1)
            if max_retry_reached:
                print("ERROR: Maximum retry attempts reached for code analysis.")
                print("Proceeding with limited or empty results. Report may be incomplete.")
                
                # Ensure we have at least empty structures for the report generator
                if "technology_stack" not in exec_res:
                    exec_res["technology_stack"] = {}
                if "findings" not in exec_res:
                    exec_res["findings"] = []
                if "component_analysis" not in exec_res:
                    exec_res["component_analysis"] = {}
                if "security_quality_analysis" not in exec_res:
                    exec_res["security_quality_analysis"] = {}
        
        print("DEBUG: Technology stack found:", list(exec_res.get("technology_stack", {}).keys()))
        print("DEBUG: Number of findings:", len(exec_res.get("findings", [])))
        print("DEBUG: Components detected:", len(exec_res.get("component_analysis", {})))
        print("DEBUG: Security and quality checks:", list(exec_res.get("security_quality_analysis", {}).keys()))
        
        shared["code_analysis"] = exec_res
        print("DEBUG: Stored code_analysis in shared state")
        return "default" 