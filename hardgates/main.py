#!/usr/bin/env python3
"""
Hard Gate Assessment CLI Tool

This tool analyzes GitHub repositories for hard gate compliance and generates HTML reports.
"""

import argparse
import os
import sys
from core.flow import Flow
from nodes.fetch_repo import FetchRepo
from nodes.analyze_code import AnalyzeCode
from nodes.generate_report import GenerateReport

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

def create_assessment_flow():
    """
    Create and return the hard gate assessment flow.
    """
    # Create nodes
    fetch_repo = FetchRepo(max_retries=2, wait=5)
    analyze_code = AnalyzeCode(max_retries=3, wait=10)
    generate_report = GenerateReport()
    
    # Connect nodes in sequence
    fetch_repo >> analyze_code >> generate_report
    
    # Create the flow
    return Flow(start=fetch_repo)

def main():
    parser = argparse.ArgumentParser(
        description="Hard Gate Assessment Tool - Analyze GitHub repositories for compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repo https://github.com/user/repo --token TOKEN --output ./report.html
  %(prog)s --repo https://github.com/user/repo --branch develop --token TOKEN
  %(prog)s --repo https://github.com/user/repo --token TOKEN --output /tmp/assessment.html

Environment Variables:
  GITHUB_TOKEN     - GitHub authentication token
  OPENAI_API_KEY   - OpenAI API key for LLM analysis
  ANTHROPIC_API_KEY - Anthropic API key for LLM analysis  
  GOOGLE_API_KEY   - Google API key for LLM analysis
        """
    )
    
    parser.add_argument("--repo", required=True,
                       help="GitHub repository URL (e.g., https://github.com/user/repo)")
    parser.add_argument("--branch", default="main",
                       help="Branch to analyze (default: main)")
    parser.add_argument("--token",
                       help="GitHub authentication token (can also use GITHUB_TOKEN env var)")
    parser.add_argument("--output", default="./hard_gate_assessment.html",
                       help="Output HTML file path (default: ./hard_gate_assessment.html)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Validate GitHub URL - support custom domains like github.xyz.com
    if not (args.repo.startswith("https://") and "github" in args.repo.split("//")[1].split("/")[0]):
        print("Error: Please provide a valid GitHub repository URL (supports github.com and GitHub Enterprise domains)")
        return 1
    
    # Get GitHub token from args or environment
    github_token = args.token or os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("Warning: No GitHub token provided. This may fail for private repositories.")
        print("You can provide a token using --token or the GITHUB_TOKEN environment variable.")
    
    # Check for LLM API keys
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), os.getenv("GOOGLE_API_KEY")]):
        parser.error("No LLM API key found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY environment variable.")
    
    # Initialize shared state
    shared = {
        "repo_url": args.repo,
        "branch": args.branch,
        "github_token": github_token,
        "output_format": "html",
        "output_path": args.output,
        "project_name": args.repo.split("/")[-1].replace(".git", "")
    }
    
    if args.verbose:
        print(f"Repository: {args.repo}")
        print(f"Branch: {args.branch}")
        print(f"Output: {args.output}")
        print(f"GitHub token: {'✓' if github_token else '✗'}")
        print()
    
    try:
        # Create and run the assessment flow
        print("Starting hard gate assessment...")
        assessment_flow = create_assessment_flow()
        assessment_flow.run(shared)
        
        # Get the report path
        report_path = shared.get("report_path")
        
        if not report_path or not os.path.exists(report_path):
            raise ValueError("HTML report was not generated successfully")
        
        # Print success message
        print(f"\n✅ Hard gate assessment completed successfully!")
        print(f"📄 Report saved to: {report_path}")
        print(f"🌐 Open report with: open {report_path}")
        
        # Print summary statistics for primary hard gates
        compliance_metrics = shared.get("compliance_metrics", {})
        if compliance_metrics:
            total_gates = compliance_metrics.get("total_gates", 0)
            gates_implemented = compliance_metrics.get("gates_implemented", 0)
            compliance_percentage = compliance_metrics.get("compliance_percentage", 0)
            
            print(f"📊 Primary Hard Gates Compliance: {compliance_percentage:.1f}% ({gates_implemented}/{total_gates})")
        
        findings_count = len(shared.get("assessment_results", {}).get("findings", []))
        if findings_count > 0:
            print(f"🔍 Code Findings: {findings_count} issues identified")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Assessment cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Assessment failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 