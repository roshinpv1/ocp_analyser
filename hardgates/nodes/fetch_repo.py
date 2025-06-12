import os
from core.flow import Node
from utils.github_client import fetch_github_repo

class FetchRepo(Node):
    def prep(self, shared):
        """
        Read repository URL, branch, and token from shared store.
        """
        repo_url = shared.get("repo_url")
        branch = shared.get("branch", "main")
        github_token = shared.get("github_token")
        
        if not repo_url:
            raise ValueError("Repository URL is required")
        
        return repo_url, branch, github_token
    
    def exec(self, prep_res):
        """
        Fetch repository content using GitHub API.
        """
        repo_url, branch, github_token = prep_res
        
        print(f"Fetching repository: {repo_url}")
        if branch != "main":
            print(f"Using branch: {branch}")
        
        try:
            files_data = fetch_github_repo(repo_url, branch, github_token)
            print(f"Successfully fetched {len(files_data)} files")
            return files_data
        except Exception as e:
            print(f"Error fetching repository: {str(e)}")
            raise
    
    def post(self, shared, prep_res, exec_res):
        """
        Store fetched files data in shared store.
        """
        repo_url, branch, github_token = prep_res
        files_data = exec_res
        
        # Store the files data
        shared["files_data"] = files_data
        
        # Extract project name from repo URL
        if repo_url:
            # Extract project name from URL (e.g., https://github.com/user/repo -> repo)
            project_name = repo_url.rstrip('/').split('/')[-1]
            shared["project_name"] = project_name
        
        # Store file statistics for reporting
        file_summary = {
            "count": len(files_data),
            "extensions": {}
        }
        
        for file_path in files_data.keys():
            _, ext = os.path.splitext(file_path)
            if ext:
                file_summary["extensions"][ext] = file_summary["extensions"].get(ext, 0) + 1
        
        shared["file_summary"] = file_summary
        
        print(f"Stored {len(files_data)} files for analysis")
        return "default"

if __name__ == "__main__":
    # Test the node
    shared = {
        "repo_url": "https://github.com/octocat/Hello-World",
        "branch": "master",
        "github_token": None
    }
    
    node = FetchRepo()
    try:
        result = node.run(shared)
        print(f"Result: {result}")
        print(f"Files stored: {len(shared.get('files_data', {}))}")
        print(f"Project name: {shared.get('project_name')}")
    except Exception as e:
        print(f"Error: {e}") 