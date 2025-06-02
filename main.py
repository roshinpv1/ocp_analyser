import os
import argparse
import glob
import re
from flow import create_analysis_flow, create_excel_analysis_flow

def main():
    parser = argparse.ArgumentParser(description="Analyze codebase for resiliency and observability")
    parser.add_argument("--repo", help="GitHub repository URL to analyze")
    parser.add_argument("--dir", help="Local directory to analyze")
    parser.add_argument("--excel", help="Excel file to extract repo/component info from")
    parser.add_argument("--excel-dir", help="Directory containing multiple Excel files to process")
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
    
    args = parser.parse_args()

    # Validate input arguments
    if not args.repo and not args.dir and not args.excel and not args.excel_dir:
        parser.error("Either --repo, --dir, --excel, or --excel-dir must be specified")

    # Get GitHub token from args or environment variable
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    if args.repo and not github_token and "github.com" in args.repo:
        print("\nWarning: No GitHub token provided. This may fail for private repositories.")
        print("You can provide a token using --github-token or the GITHUB_TOKEN environment variable.")

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    print("\nUsing legacy analysis flow")

    # Process a directory of Excel files
    if args.excel_dir:
        # Find all Excel files in the directory
        excel_files = []
        excel_patterns = ["*.xlsx", "*.xls", "*.xlsm"]
        
        for pattern in excel_patterns:
            excel_files.extend(glob.glob(os.path.join(args.excel_dir, pattern)))
        
        if not excel_files:
            print(f"No Excel files found in directory: {args.excel_dir}")
            return
        
        # Filter out Excel temporary files (starting with ~$)
        valid_excel_files = [f for f in excel_files if not os.path.basename(f).startswith("~$")]
        
        skipped_files = len(excel_files) - len(valid_excel_files)
        if skipped_files > 0:
            print(f"Skipping {skipped_files} temporary Excel files (names starting with ~$)")
        
        if not valid_excel_files:
            print("No valid Excel files found after filtering out temporary files.")
            return
        
        # Process each Excel file
        print(f"Found {len(valid_excel_files)} valid Excel files to process")
        
        success_count = 0
        failure_count = 0
        
        for i, excel_file in enumerate(valid_excel_files):
            excel_filename = os.path.basename(excel_file)
            print(f"\n[{i+1}/{len(valid_excel_files)}] Processing Excel file: {excel_filename}")
            
            try:
                # Create a separate output directory for each Excel file
                # Clean the filename for directory name (remove special characters)
                safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', os.path.splitext(excel_filename)[0])
                file_output_dir = os.path.join(args.output, safe_filename)
                os.makedirs(file_output_dir, exist_ok=True)
                
                # Initialize shared state for this Excel file
                shared = {
                    "repo_url": None,  # Will be set by ProcessExcel
                    "local_dir": args.dir,
                    "include_patterns": args.include,
                    "exclude_patterns": args.exclude,
                    "max_file_size": args.max_size,
                    "use_cache": not args.no_cache,
                    "output_dir": file_output_dir,
                    "github_token": github_token,
                    "excel_file": excel_file
                }
                
                if args.sheet:
                    shared["sheet_name"] = args.sheet
                
                # Process the Excel file
                result = process_single_excel(shared)
                
                if result:
                    success_count += 1
                else:
                    failure_count += 1
                    
            except Exception as e:
                print(f"Error processing file {excel_filename}: {str(e)}")
                failure_count += 1
                import traceback
                traceback.print_exc()
        
        # Print summary
        print(f"\n===== Processing Summary =====")
        print(f"Total Excel files processed: {len(valid_excel_files)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {failure_count}")
        
    else:
        # Initialize shared state for standard processing
        shared = {
            "repo_url": args.repo,
            "local_dir": args.dir,
            "include_patterns": args.include,
            "exclude_patterns": args.exclude,
            "max_file_size": args.max_size,
            "use_cache": not args.no_cache,
            "output_dir": args.output,
            "github_token": github_token
        }

        # If Excel is provided, set excel_file and (optionally) sheet_name
        if args.excel:
            # Check if file is a temporary Excel file
            if os.path.basename(args.excel).startswith("~$"):
                print(f"Error: The provided Excel file '{args.excel}' appears to be a temporary file.")
                print("Please close the file in Excel and try again with the actual Excel file.")
                return
                
            shared["excel_file"] = args.excel
            if args.sheet:
                shared["sheet_name"] = args.sheet
            # Remove repo_url so it will be set by ProcessExcel
            shared["repo_url"] = None

        process_single_excel(shared)

def process_single_excel(shared):
    """Process a single Excel file or repository."""
    try:
        # Check if the file is a valid Excel file (if one is specified)
        if "excel_file" in shared and shared["excel_file"]:
            excel_file = shared["excel_file"]
            
            # Check if file exists
            if not os.path.exists(excel_file):
                print(f"Error: Excel file '{excel_file}' does not exist.")
                return False
                
            # Check file size (extremely small files are likely empty or corrupt)
            if os.path.getsize(excel_file) < 100:
                print(f"Error: Excel file '{excel_file}' is too small to be valid.")
                return False
            
            print(f"Processing Excel file: {excel_file}")
            
            # Use legacy Excel analysis flow
            analysis_flow = create_excel_analysis_flow()
        else:
            # For non-Excel processing
            if not shared.get("repo_url") and not shared.get("local_dir"):
                print("Error: No repository URL or local directory specified.")
                return False
            
            # Use legacy analysis flow
            analysis_flow = create_analysis_flow()
            
        analysis_flow.run(shared)

        # The reports are already saved by the GenerateReport node
        # Just print the paths from the shared state
        if "analysis_report" in shared:
            print(f"\nAnalysis reports generated:")
            print(f"- Markdown: {shared['analysis_report']['markdown']}")
            print(f"- HTML: {shared['analysis_report']['html']}")
            
            print(f"\nOpen the HTML report with: open {shared['analysis_report']['html']}")
            
            # Print OpenShift assessment report info if available
            if "ocp_assessment_html" in shared:
                print(f"- OpenShift Assessment Report: {shared['ocp_assessment_html']}")
                
            return True
        else:
            print("Warning: Analysis completed but no reports were generated.")
            return False
        
    except ValueError as e:
        print(f"\nError: {str(e)}")
        print("\nTry adjusting the include/exclude patterns to match your codebase.")
        print("Example: python main.py --repo <url> --include '*.py' '*.js' --exclude 'tests/*'")
        return False
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
