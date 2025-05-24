import os
import re
import tempfile
from urllib.parse import urlparse
from core.genflow import Node
from utils.crawl_github_files import crawl_github_files
from utils.crawl_local_files import crawl_local_files

class FetchRepo(Node):
    def prep(self, shared):
        # Prepare parameters for the fetch operation
        repo_url = shared.get("repo_url")
        local_dir = shared.get("local_dir")
        github_token = shared.get("github_token")
        include_patterns = shared.get("include_patterns")
        exclude_patterns = shared.get("exclude_patterns")
        max_file_size = shared.get("max_file_size", 100000)
        
        # Validate that we have either a repo URL or a local directory
        if not repo_url and not local_dir:
            raise ValueError("Either repo_url or local_dir must be provided")
            
        # Determine project name
        project_name = shared.get("project_name")
        if not project_name:
            if repo_url:
                # Extract project name from URL
                parsed_url = urlparse(repo_url)
                path_parts = parsed_url.path.strip("/").split("/")
                if len(path_parts) >= 2:
                    project_name = path_parts[1]  # Username/repo_name
                else:
                    project_name = "unknown"
            else:
                # Extract project name from local directory
                project_name = os.path.basename(os.path.normpath(local_dir))
            
            # Store project name in shared
            shared["project_name"] = project_name
            
        return {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "github_token": github_token,
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "max_file_size": max_file_size
        }
        
    def exec(self, prep_res):
        # Extract parameters
        repo_url = prep_res["repo_url"]
        local_dir = prep_res["local_dir"]
        github_token = prep_res["github_token"]
        include_patterns = prep_res["include_patterns"]
        exclude_patterns = prep_res["exclude_patterns"]
        max_file_size = prep_res["max_file_size"]
        
        if repo_url:
            print(f"Fetching from GitHub repo: {repo_url}")
            try:
                # Create a temporary directory for repo files
                temp_dir = tempfile.mkdtemp(prefix="repo_")
                
                # Crawl GitHub repo
                result = crawl_github_files(
                    repo_url,
                    token=github_token,
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns,
                    max_file_size=max_file_size
                )
                
                # Format the result with repo info
                return {
                    "files_data": result["files"],
                    "source": "github",
                    "repo_url": repo_url,
                    "temp_dir": temp_dir,
                    "file_count": len(result["files"]),
                    "repo_name": result.get("repo_name", "Unknown")
                }
                
            except Exception as e:
                print(f"Error fetching GitHub repo: {str(e)}")
                raise
        else:
            print(f"Analyzing local directory: {local_dir}")
            try:
                # Crawl local directory
                result = crawl_local_files(
                    local_dir,
                    include_patterns=include_patterns,
                    exclude_patterns=exclude_patterns,
                    max_file_size=max_file_size
                )
                
                # Format the result with local dir info
                return {
                    "files_data": result["files"],
                    "source": "local",
                    "local_dir": local_dir,
                    "file_count": len(result["files"]),
                    "repo_name": os.path.basename(os.path.normpath(local_dir))
                }
                
            except Exception as e:
                print(f"Error analyzing local directory: {str(e)}")
                raise
    
    def post(self, shared, prep_res, exec_res):
        # Store the result in shared state
        shared["files_data"] = exec_res["files_data"]
        shared["repo_source"] = exec_res["source"]
        if "temp_dir" in exec_res:
            shared["temp_dir"] = exec_res["temp_dir"]
        
        print(f"Fetched {exec_res['file_count']} files from {exec_res['source']}")
        
        # Continue to the next step
        return "default" 