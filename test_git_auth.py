#!/usr/bin/env python3

import os
import sys
from utils.crawl_github_files import crawl_github_files

def test_git_auth():
    """Test git authentication with access token."""
    
    # You can set your token here or via environment variable
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not github_token:
        print("Please set GITHUB_TOKEN environment variable or edit this script")
        print("Usage: export GITHUB_TOKEN=your_token_here")
        return False
    
    # Test with a simple public repository first
    test_repo = "https://github.com/octocat/Hello-World"
    
    print(f"Testing git authentication with token...")
    print(f"Repository: {test_repo}")
    print(f"Token: {'*' * (len(github_token) - 4) + github_token[-4:]}")
    
    try:
        result = crawl_github_files(
            repo_url=test_repo,
            token=github_token,
            max_file_size=10000,
            include_patterns=["*.md", "*.txt"],
            shallow_clone=True
        )
        
        files = result.get("files", {})
        print(f"\n✅ Success! Downloaded {len(files)} files")
        
        if files:
            print("\nFiles found:")
            for file_path in sorted(files.keys()):
                print(f"  - {file_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_git_auth()
    sys.exit(0 if success else 1) 