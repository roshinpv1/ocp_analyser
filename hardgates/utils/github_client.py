import os
import subprocess
import tempfile
import shutil
from typing import Dict, Optional
from pathlib import Path

def fetch_github_repo(repo_url: str, branch: str = "main", github_token: Optional[str] = None) -> Dict[str, str]:
    """
    Fetch repository content using git clone.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
        branch: Branch name to fetch (defaults to main)
        github_token: GitHub authentication token (optional, used for private repos)
        
    Returns:
        Dictionary mapping file paths to file contents
    """
    
    # Validate GitHub URL - support custom domains like github.xyz.com
    if not (repo_url.startswith("https://") and "github" in repo_url.split("//")[1].split("/")[0]):
        raise ValueError("Repository URL must be a GitHub URL (supports github.com and GitHub Enterprise domains)")
    
    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = os.path.join(temp_dir, "repo")
        
        try:
            # Prepare clone URL with token if provided
            if github_token:
                # Insert token into URL for authentication
                clone_url = repo_url.replace("https://", f"https://{github_token}@")
            else:
                clone_url = repo_url
            
            # Clone the repository with specific branch and minimal depth
            cmd = [
                "git", "clone", 
                "--depth", "1",  # Shallow clone for speed
                "--branch", branch,
                "--single-branch",
                clone_url, 
                clone_dir
            ]
            
            print(f"Cloning repository: {repo_url} (branch: {branch})")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                # Try alternative branch names if the specified branch fails
                for alt_branch in ["master", "develop", "dev"]:
                    if alt_branch != branch:
                        try:
                            alt_cmd = [
                                "git", "clone", 
                                "--depth", "1",
                                "--branch", alt_branch,
                                "--single-branch",
                                clone_url, 
                                clone_dir
                            ]
                            print(f"Trying alternative branch: {alt_branch}")
                            result = subprocess.run(alt_cmd, capture_output=True, text=True, timeout=300)
                            if result.returncode == 0:
                                print(f"Successfully cloned using branch: {alt_branch}")
                                break
                        except:
                            continue
                else:
                    raise ValueError(f"Failed to clone repository. Error: {result.stderr}")
            
            # Read files from cloned repository
            files_data = {}
            
            # File filtering configuration
            allowed_extensions = {
                '.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cpp', '.h', '.hpp', 
                '.c', '.cs', '.swift', '.yaml', '.yml', '.json', '.xml', '.html', '.css',
                '.md', '.rst', '.txt', '.dockerfile', '.sh', '.bash', '.sql', '.scala',
                '.kt', '.dart', '.rs', '.lua', '.r', '.m', '.mm', '.gradle', '.maven'
            }
            
            excluded_dirs = {
                '.git', '.github', '.vscode', '.idea', '__pycache__', 'node_modules', 
                'dist', 'build', 'target', 'bin', 'obj', '.next', '.nuxt', 'vendor',
                'env', '.env', '.venv', 'venv', 'logs', 'tmp', 'temp', '.cache'
            }
            
            excluded_files = {
                '.gitignore', '.gitmodules', '.DS_Store', 'Thumbs.db', '.dockerignore',
                'package-lock.json', 'yarn.lock', 'composer.lock', 'Gemfile.lock'
            }
            
            # Walk through the repository directory
            repo_path = Path(clone_dir)
            for file_path in repo_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Get relative path from repo root
                relative_path = file_path.relative_to(repo_path)
                relative_path_str = str(relative_path)
                
                # Skip excluded directories
                if any(excluded_dir in relative_path.parts for excluded_dir in excluded_dirs):
                    continue
                
                # Skip excluded files
                if relative_path.name in excluded_files:
                    continue
                
                # Check file extension or special files
                file_ext = file_path.suffix.lower()
                is_special_file = any(pattern in relative_path.name.lower() 
                                    for pattern in ["dockerfile", "makefile", "cmakelists.txt", "readme"])
                
                if file_ext not in allowed_extensions and not is_special_file:
                    continue
                
                # Skip large files (> 500KB)
                try:
                    if file_path.stat().st_size > 500000:
                        print(f"Skipping large file: {relative_path_str} ({file_path.stat().st_size} bytes)")
                        continue
                except:
                    continue
                
                # Skip binary files and minified files
                if any(pattern in relative_path_str.lower() for pattern in ['.min.', '.bundle.', '.chunk.']):
                    continue
                
                # Read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Skip empty files or files with only whitespace
                    if content.strip():
                        files_data[relative_path_str] = content
                        
                except Exception as e:
                    print(f"Warning: Could not read {relative_path_str}: {str(e)}")
                    continue
            
            if not files_data:
                raise ValueError("No valid files found in repository")
            
            print(f"Successfully fetched {len(files_data)} files")
            return files_data
            
        except subprocess.TimeoutExpired:
            raise ValueError("Repository clone timed out. Repository may be too large.")
        except Exception as e:
            if "does not exist" in str(e).lower():
                raise ValueError(f"Repository or branch '{branch}' not found")
            else:
                raise ValueError(f"Failed to fetch repository: {str(e)}")

def check_git_availability():
    """
    Check if git is available on the system.
    """
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

if __name__ == "__main__":
    # Test the function
    if not check_git_availability():
        print("Error: git is not available on this system")
        exit(1)
        
    test_repo = "https://github.com/octocat/Hello-World"
    try:
        files = fetch_github_repo(test_repo)
        print(f"Fetched {len(files)} files:")
        for path in list(files.keys())[:10]:  # Show first 10 files
            print(f"  - {path}")
            
        # Show some content
        if files:
            first_file = list(files.keys())[0]
            content = files[first_file]
            print(f"\nSample content from {first_file}:")
            print(content[:200] + "..." if len(content) > 200 else content)
            
    except Exception as e:
        print(f"Error: {e}") 