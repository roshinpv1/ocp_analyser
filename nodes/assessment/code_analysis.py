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
        
        # Check for Excel folders in files_data
        excel_extensions = {'.xlsx', '.xls', '.xlsm', '.xlsb', '.csv'}
        excel_folders = set()
        
        for file_path in files_data.keys():
            dir_path = os.path.dirname(file_path)
            dir_parts = dir_path.split(os.sep)
            for part in dir_parts:
                if any(part.lower().endswith(ext) for ext in excel_extensions):
                    excel_folders.add(part)
        
        if excel_folders:
            print(f"Found files from Excel folders: {', '.join(excel_folders)}")
        
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
        context = self.create_llm_context(files_data, excel_folders)
        
        return context, file_listing, len(files_data), project_name, use_cache, file_content_map, component_questions, excel_folders
    
    def create_llm_context(self, files_data, excel_folders=None):
        # Extract content and create a summary
        context_parts = []
        
        # Sort files by extension to group similar files together
        sorted_files = sorted(files_data.items(), key=lambda x: os.path.splitext(x[0])[1])
        
        # Add file snippets to provide context
        file_count = 0
        for file_path, file_content in sorted_files:
            # Limit to first 20 files to keep context manageable (increased from 10)
            if file_count >= 20:
                break
                
            # Check if file is in Excel folder (prioritize these)
            in_excel_folder = excel_folders and any(folder in file_path for folder in excel_folders)
            
            # Skip very large files for context unless they're in Excel folders
            if len(file_content) > 5000 and not in_excel_folder:
                continue
                
            # Truncate very large files
            if len(file_content) > 3000:
                file_content = file_content[:1500] + "\n...\n" + file_content[-1500:]
                
            context_parts.append(f"File: {file_path}\n```\n{file_content}\n```\n")
            file_count += 1
            
        # Add special note for Excel folder files
        if excel_folders:
            context_parts.append(f"\nNOTE: The codebase includes files from Excel folders: {', '.join(excel_folders)}\n")
            
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
        context, file_listing, file_count, project_name, use_cache, file_content_map, component_questions, excel_folders = prep_res
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

        # Simplified and shorter prompt to avoid token limits
        prompt = f"""Analyze this {project_name} codebase ({file_count} files) and provide analysis in VALID JSON format.

CODE SAMPLES:
{context[:3000]}...

Return ONLY valid JSON with this structure:

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
      "category": "security",
      "severity": "high",
      "description": "Security issue found",
      "location": "file.java:123",
      "recommendation": "Fix this"
    }}
  ],
  "component_analysis": {{
    "Redis": {{"detected": "yes", "evidence": "Found redis imports"}},
    "KAFKA": {{"detected": "no", "evidence": "No kafka references"}},
    "REST API": {{"detected": "yes", "evidence": "REST controllers found"}},
    "SOAP": {{"detected": "no", "evidence": "No SOAP services"}},
    "LDAP": {{"detected": "no", "evidence": "No LDAP config"}},
    "MySQL": {{"detected": "yes", "evidence": "Database config found"}},
    "JWT": {{"detected": "yes", "evidence": "JWT tokens used"}},
    "MTLS": {{"detected": "no", "evidence": "No mutual TLS"}}
  }},
  "security_quality_analysis": {{
    "auditability": {{
      "logging_practices": {{"implemented": "yes", "evidence": "Logging found", "recommendation": "Continue"}},
      "audit_trails": {{"implemented": "no", "evidence": "No audit system", "recommendation": "Add audit logs"}}
    }},
    "availability": {{
      "retry_logic": {{"implemented": "partial", "evidence": "Some retries", "recommendation": "Add more"}},
      "timeouts": {{"implemented": "yes", "evidence": "Timeouts set", "recommendation": "Review values"}}
    }},
    "error_handling": {{
      "error_logging": {{"implemented": "yes", "evidence": "Error logs", "recommendation": "Standardize"}},
      "http_codes": {{"implemented": "yes", "evidence": "Standard codes", "recommendation": "Continue"}}
    }},
    "monitoring": {{
      "url_monitoring": {{"implemented": "no", "evidence": "No monitoring", "recommendation": "Add health checks"}}
    }},
    "testing": {{
      "automated_testing": {{"implemented": "partial", "evidence": "Some tests", "recommendation": "Increase coverage"}}
    }}
  }}
}}

Focus on: Java frameworks, databases, security patterns, API types, authentication. Return ONLY the JSON, no other text.
"""

        try:
            # Create a cache key based on project_name and file_count
            cache_key = f"{project_name}_{file_count}"
            if excel_folders:
                # Add Excel folders to cache key to ensure proper cache differentiation
                excel_folders_str = "_".join(sorted(excel_folders))
                cache_key += f"_excel_{excel_folders_str}"
                
            cache_file = os.path.join("cache", "code_analysis", f"{cache_key}.json")
            
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            # Check if we should use cached results
            if use_cache and os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_result = json.load(f)
                    print(f"Using cached analysis results from {cache_file}")
                    return cached_result
                except Exception as e:
                    print(f"Error loading cached results: {str(e)}. Will perform fresh analysis.")
            
            # Make multiple attempts to get a valid response from the LLM
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"LLM analysis attempt {attempt + 1}/{max_retries}...")
                    
                    # Call the LLM for analysis
                    response = call_llm(prompt)
                    
                    # Extract JSON from response - more robust extraction
                    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                    
                    if not json_match:
                        print(f"WARNING: No JSON found in LLM response on attempt {attempt + 1}. Retrying...")
                        print("Response snippet:", response[:200])
                        continue
                    
                    json_str = json_match.group(1)
                    
                    # Validate JSON format
                    try:
                        analysis = json.loads(json_str)
                    except json.JSONDecodeError as je:
                        print(f"WARNING: Invalid JSON in LLM response on attempt {attempt + 1}: {str(je)}")
                        print("JSON snippet:", json_str[:200])
                        continue
                    
                    # Basic structure validation
                    required_keys = ["technology_stack", "findings", "component_analysis", "security_quality_analysis"]
                    missing_keys = [key for key in required_keys if key not in analysis]
                    
                    if missing_keys:
                        print(f"WARNING: Missing required keys in analysis: {missing_keys}. Retrying...")
                        continue
                    
                    # Success - we have a valid analysis
                    break
                    
                except Exception as e:
                    print(f"Error during LLM analysis attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        print("ERROR: All attempts to get valid analysis failed.")
                        return {
                            "technology_stack": {},
                            "findings": [],
                            "component_analysis": {},
                            "security_quality_analysis": {},
                            "error": f"Failed to get valid analysis after {max_retries} attempts: {str(e)}"
                        }
            else:
                # All attempts failed
                print("ERROR: Could not get valid analysis from LLM.")
                return {
                    "technology_stack": {},
                    "findings": [],
                    "component_analysis": {},
                    "security_quality_analysis": {},
                    "error": "Failed to extract valid JSON from LLM response"
                }
            
            # Now we have a valid analysis, process it
            try:
                # Validate and standardize technology stack
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
                    if not all(k in finding for k in ["category", "severity", "description"]):
                        continue
                        
                    # Allow findings without location or with partial location
                    if "location" not in finding:
                        finding["location"] = {
                            "file": "Unknown",
                            "line": 0,
                            "code": ""
                        }
                    else:
                        location = finding["location"]
                        if not isinstance(location, dict):
                            finding["location"] = {
                                "file": "Unknown",
                                "line": 0,
                                "code": ""
                            }
                        else:
                            # Fill in any missing location fields
                            if "file" not in location:
                                location["file"] = "Unknown"
                            if "line" not in location:
                                location["line"] = 0
                            if "code" not in location:
                                location["code"] = ""
                    
                    # Make sure recommendation exists
                    if "recommendation" not in finding:
                        finding["recommendation"] = "No specific recommendation provided"
                        
                    # Validate types
                    if not isinstance(finding["category"], str) or \
                       not isinstance(finding["severity"], str) or \
                       not isinstance(finding["description"], str) or \
                       not isinstance(finding["recommendation"], str):
                        continue
                    
                    # Convert line to int if it's a string
                    try:
                        finding["location"]["line"] = int(finding["location"]["line"])
                    except (ValueError, TypeError):
                        finding["location"]["line"] = 0
                    
                    # Only validate file and line if the file is known
                    if finding["location"]["file"] != "Unknown" and finding["location"]["file"] in file_content_map:
                        file_path = finding["location"]["file"]
                        file_content = file_content_map[file_path]
                        file_lines = file_content.split('\n')
                        
                        # Fix line number if out of range
                        if not (0 <= finding["location"]["line"] < len(file_lines)):
                            finding["location"]["line"] = 0
                            
                        # Only validate code snippet if it's not empty and line is valid
                        if finding["location"]["code"] and finding["location"]["line"] > 0:
                            actual_line = file_lines[finding["location"]["line"]].strip()
                            reported_snippet = finding["location"]["code"].strip()
                            
                            # If code snippet doesn't match line content, don't validate it
                            # but keep the finding
                            if reported_snippet not in actual_line:
                                # No validation required, keep the finding as is
                                pass
                    
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
                
                # Add additional information about Excel folders if present
                if excel_folders:
                    if "Excel Folder Analysis" not in validated_tech_stack:
                        validated_tech_stack["Excel Folder Analysis"] = []
                    
                    for folder in excel_folders:
                        folder_files = [path for path in file_content_map.keys() if folder in path]
                        if folder_files:
                            validated_tech_stack["Excel Folder Analysis"].append({
                                "name": f"Excel Folder: {folder}",
                                "version": "N/A",
                                "purpose": "Contains related application files",
                                "files": folder_files[:10]  # Limit to first 10 files
                            })
                
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
                
                # Save valid analysis to cache
                try:
                    result = {
                        "technology_stack": validated_tech_stack,
                        "findings": validated_findings,
                        "component_analysis": validated_component_analysis,
                        "excel_components": component_questions if component_questions else {},
                        "security_quality_analysis": validated_security_quality
                    }
                    
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2)
                    print(f"Cached analysis results to {cache_file}")
                    
                    return result
                    
                except Exception as e:
                    print(f"Warning: Could not cache results: {str(e)}")
                    # Return the result even if caching fails
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
        else:
            # Only cache successful results without errors
            try:
                # Get project name for cache key
                project_name = shared.get("project_name", "Unknown Project")
                file_count = len(shared.get("files_data", {}))
                
                # Get Excel folders if any
                excel_folders = []
                for file_path in shared.get("files_data", {}).keys():
                    dir_path = os.path.dirname(file_path)
                    dir_parts = dir_path.split(os.sep)
                    for part in dir_parts:
                        if any(part.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.xlsm', '.xlsb', '.csv']):
                            excel_folders.append(part)
                excel_folders = list(set(excel_folders))
                
                # Create a cache key based on project_name and file_count
                cache_key = f"{project_name}_{file_count}"
                if excel_folders:
                    # Add Excel folders to cache key
                    excel_folders_str = "_".join(sorted(excel_folders))
                    cache_key += f"_excel_{excel_folders_str}"
                    
                cache_dir = os.path.join("cache", "code_analysis")
                cache_file = os.path.join(cache_dir, f"{cache_key}.json")
                
                # Ensure cache directory exists
                os.makedirs(cache_dir, exist_ok=True)
                
                # Cache the successful result
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(exec_res, f, indent=2)
                print(f"Cached analysis results to {cache_file}")
            except Exception as e:
                print(f"Warning: Failed to cache analysis results: {str(e)}")
        
        print("DEBUG: Technology stack found:", list(exec_res.get("technology_stack", {}).keys()))
        print("DEBUG: Number of findings:", len(exec_res.get("findings", [])))
        print("DEBUG: Components detected:", len(exec_res.get("component_analysis", {})))
        print("DEBUG: Security and quality checks:", list(exec_res.get("security_quality_analysis", {}).keys()))
        
        # Check if we have Excel folder information and log it
        excel_folder_tech = exec_res.get("technology_stack", {}).get("Excel Folder Analysis", [])
        if excel_folder_tech:
            print(f"DEBUG: Excel folder analysis included {len(excel_folder_tech)} folder entries")
            for folder_entry in excel_folder_tech:
                print(f"  - {folder_entry.get('name')} with {len(folder_entry.get('files', []))} files")
        
        # Validate we have actual data before storing in shared state
        if not exec_res.get("technology_stack") and not exec_res.get("findings") and not exec_res.get("component_analysis"):
            print("WARNING: Analysis appears to be empty. Report may be incomplete.")
            
            # Check if we have a previously cached result we can use
            try:
                project_name = shared.get("project_name", "Unknown Project")
                file_count = len(shared.get("files_data", {}))
                cache_key = f"{project_name}_{file_count}"
                cache_file = os.path.join("cache", "code_analysis", f"{cache_key}.json")
                
                if os.path.exists(cache_file):
                    print(f"Attempting to use previously cached analysis from {cache_file}")
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_result = json.load(f)
                    
                    # Only use cache if it has some actual data
                    if (cached_result.get("technology_stack") or 
                        cached_result.get("findings") or 
                        cached_result.get("component_analysis")):
                        print("Using cached analysis instead of empty result")
                        exec_res = cached_result
            except Exception as e:
                print(f"Failed to load cached analysis: {str(e)}")
        
        shared["code_analysis"] = exec_res
        print("DEBUG: Stored code_analysis in shared state")
        return "default" 