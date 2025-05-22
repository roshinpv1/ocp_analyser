import os
import argparse
from flow import create_analysis_flow, create_excel_analysis_flow

def main():
    parser = argparse.ArgumentParser(description="Analyze codebase for resiliency and observability")
    parser.add_argument("--repo", help="GitHub repository URL to analyze")
    parser.add_argument("--dir", help="Local directory to analyze")
    parser.add_argument("--excel", help="Excel file to extract repo/component info from")
    parser.add_argument("--sheet", help="Sheet name in Excel file (optional)")
    parser.add_argument("--include", nargs="+", 
        default=[
            "*.py", "*.js", "*.ts", "*.java", "*.go", "*.rb", "*.php",
            "*.cpp", "*.h", "*.hpp", "*.c", "*.cs", "*.swift",
            "*.yaml", "*.yml", "*.json", "*.xml", "*.html", "*.css",
            "Dockerfile", "docker-compose*.yml", "*.sh", "*.bash",
            "*.md", "*.rst", "*.txt"  # Include documentation for context
        ],
        help="File patterns to include")
    parser.add_argument("--exclude", nargs="+", 
        default=[
            "tests/*", "test/*", "docs/*", "node_modules/*", "__pycache__/*",
            "*.test.*", "*.spec.*", "*.min.*", "dist/*", "build/*",
            ".git/*", ".github/*", ".vscode/*", "*.log"
        ],
        help="File patterns to exclude")
    parser.add_argument("--max-size", type=int, default=100000, help="Maximum file size in bytes")
    parser.add_argument("--output", default="./analysis_output", help="Output directory for analysis report")
    parser.add_argument("--no-cache", action="store_true", help="Disable LLM response caching")
    parser.add_argument("--github-token", help="GitHub authentication token for private repositories")
    
    # Add Jira integration arguments
    parser.add_argument("--jira-url", help="Jira server URL (e.g., https://your-domain.atlassian.net)")
    parser.add_argument("--jira-username", help="Jira username or email")
    parser.add_argument("--jira-api-token", help="Jira API token")
    parser.add_argument("--jira-project-key", default="XYZ", help="Jira project key to search for (default: XYZ)")
    
    args = parser.parse_args()

    # Validate input arguments
    if not args.repo and not args.dir and not args.excel:
        parser.error("Either --repo, --dir, or --excel must be specified")

    # Get GitHub token from args or environment variable
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    if args.repo and not github_token and "github.com" in args.repo:
        print("\nWarning: No GitHub token provided. This may fail for private repositories.")
        print("You can provide a token using --github-token or the GITHUB_TOKEN environment variable.")

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Initialize shared state
    shared = {
        "repo_url": args.repo,
        "local_dir": args.dir,
        "include_patterns": args.include,
        "exclude_patterns": args.exclude,
        "max_file_size": args.max_size,
        "use_cache": not args.no_cache,
        "output_dir": args.output,
        "github_token": github_token,
        # Add Jira configuration
        "jira_url": args.jira_url,
        "jira_username": args.jira_username,
        "jira_api_token": args.jira_api_token,
        "jira_project_key": args.jira_project_key
    }

    # If Excel is provided, set excel_file and (optionally) sheet_name
    if args.excel:
        shared["excel_file"] = args.excel
        if args.sheet:
            shared["sheet_name"] = args.sheet
        # Remove repo_url so it will be set by ProcessExcel
        shared["repo_url"] = None

    try:
        # Choose the correct flow based on input type
        if args.excel:
            print(f"\nProcessing Excel file: {args.excel}")
            analysis_flow = create_excel_analysis_flow()
        else:
            analysis_flow = create_analysis_flow()
            
        analysis_flow.run(shared)

        # The reports are already saved by the GenerateReport node
        # Just print the paths from the shared state
        if "analysis_report" in shared:
            print("\nAnalysis complete! Reports generated:")
            print(f"- Markdown: {shared['analysis_report']['markdown']}")
            print(f"- HTML: {shared['analysis_report']['html']}")
            if shared['analysis_report']['pdf']:
                print(f"- PDF: {shared['analysis_report']['pdf']}")
        
    except ValueError as e:
        print(f"\nError: {str(e)}")
        print("\nTry adjusting the include/exclude patterns to match your codebase.")
        print("Example: python main.py --repo <url> --include '*.py' '*.js' --exclude 'tests/*'")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
