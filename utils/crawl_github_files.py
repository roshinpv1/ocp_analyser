import requests
import base64
import os
import tempfile
import git
import time
import fnmatch
from typing import Union, Set, List, Dict, Tuple, Any
from urllib.parse import urlparse
import re
import shutil
from pathlib import Path
from git import Repo
from utils.crawl_local_files import crawl_local_files

def crawl_github_files(
    repo_url: str,
    token: str = None,
    include_patterns: list = None,
    exclude_patterns: list = None,
    max_file_size: int = 100000,
    use_relative_paths: bool = True,
    shallow_clone: bool = False,  # Changed default to False to ensure all subdirectories are cloned
    clone_timeout: int = 300,
    max_depth: int = 10  # Increased depth to ensure subdirectories are included
) -> dict:
    """
    Clone a GitHub repository to a temporary directory and crawl its files.
    
    Args:
        repo_url: GitHub repository URL
        token: GitHub API token (optional)
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        max_file_size: Maximum file size in bytes
        use_relative_paths: Whether to use relative paths in output
        shallow_clone: Whether to perform a shallow clone (default: False)
        clone_timeout: Maximum time in seconds to wait for clone (default: 300)
        max_depth: Depth for shallow clone (default: 10)
        
    Returns:
        Dict containing file contents and metadata
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="github_crawl_")
    try:
        print(f"Cloning repository to temporary directory: {temp_dir}")
        print(f"Repository URL: {repo_url}")
        print(f"Include patterns: {include_patterns}")
        print(f"Exclude patterns: {exclude_patterns}")
        
        # Extract specific path within repo if specified
        target_path = None
        if "/tree/" in repo_url:
            # If the URL points to a specific path within the repo, extract it
            path_match = re.search(r'/tree/[^/]+/(.+)$', repo_url)
            if path_match:
                target_path = path_match.group(1)
                # Clean up the repo URL to point to the root
                repo_url = repo_url.split("/tree/")[0]
                print(f"Detected specific path in repo: {target_path}")
                print(f"Cleaned repo URL: {repo_url}")
        
        # Clone the repository with timeout
        start_time = time.time()
        if token:
            # Use token in URL for authentication
            auth_url = repo_url.replace("https://", f"https://{token}@")
            if shallow_clone:
                repo = Repo.clone_from(auth_url, temp_dir, depth=max_depth)
            else:
                repo = Repo.clone_from(auth_url, temp_dir)
        else:
            if shallow_clone:
                repo = Repo.clone_from(repo_url, temp_dir, depth=max_depth)
            else:
                repo = Repo.clone_from(repo_url, temp_dir)
                
        # Check if clone took too long
        if time.time() - start_time > clone_timeout:
            raise TimeoutError(f"Repository clone took longer than {clone_timeout} seconds")
            
        print("Repository cloned successfully")
        
        # If a specific path within the repo was specified, adjust the directory to scan
        scan_dir = temp_dir
        if target_path:
            target_dir = os.path.join(temp_dir, target_path)
            if os.path.exists(target_dir):
                scan_dir = target_dir
                print(f"Scanning specific path: {target_path}")
            else:
                print(f"Warning: Specified path '{target_path}' not found in repository. Scanning entire repo.")
        
        # Use the local file crawler to process the cloned repository
        result = crawl_local_files(
            directory=scan_dir,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_file_size=max_file_size,
            use_relative_paths=use_relative_paths
        )
        
        # Add repository information to the result
        result["repo_name"] = os.path.basename(repo_url.rstrip('/'))
        if target_path:
            result["target_path"] = target_path
            
        return result
        
    finally:
        # Clean up the temporary directory
        print("Cleaning up temporary directory...")
        shutil.rmtree(temp_dir)

# Example usage
if __name__ == "__main__":
    # Get token from environment variable (recommended for private repos)
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Warning: No GitHub token found in environment variable 'GITHUB_TOKEN'.\n"
              "Private repositories will not be accessible without a token.\n"
              "To access private repos, set the environment variable or pass the token explicitly.")
    
    repo_url = "https://github.com/pydantic/pydantic"
    
    # Example: Get Python and Markdown files, but exclude test files
    result = crawl_github_files(
        repo_url, 
        token=github_token,
        max_file_size=1 * 1024 * 1024,  # 1 MB in bytes
        use_relative_paths=True,  # Enable relative paths
        include_patterns={"*.py", "*.md"},  # Include Python and Markdown files
    )
    
    files = result["files"]
    
    print(f"\nDownloaded {len(files)} files.")
    
    # Display all file paths in the dictionary
    print("\nFiles in dictionary:")
    for file_path in sorted(files.keys()):
        print(f"  {file_path}")
    
    # Example: accessing content of a specific file
    if files:
        sample_file = next(iter(files))
        print(f"\nSample file: {sample_file}")
        print(f"Content preview: {files[sample_file][:200]}...")
