#!/usr/bin/env python3
import os
import sys
import shutil
from core.genflow import Flow, Node
from nodes import FetchRepo, AnalyzeCode, GenerateReport

def create_test_excel_folder():
    """Create a test directory structure with Excel folders for testing"""
    # Create test folder
    os.makedirs("test_data", exist_ok=True)
    
    # Create an Excel folder
    excel_folder = os.path.join("test_data", "reports.xlsx")
    os.makedirs(excel_folder, exist_ok=True)
    
    # Create some test files in the Excel folder
    for i in range(1, 6):
        with open(os.path.join(excel_folder, f"file{i}.txt"), "w") as f:
            f.write(f"Test content for file {i}")
    
    # Create another Excel folder
    excel_folder2 = os.path.join("test_data", "data.csv")
    os.makedirs(excel_folder2, exist_ok=True)
    
    # Create some test files in the second Excel folder
    for i in range(1, 15):
        with open(os.path.join(excel_folder2, f"data{i}.txt"), "w") as f:
            f.write(f"Data content for file {i}")
    
    # Create regular folders and files
    os.makedirs(os.path.join("test_data", "src"), exist_ok=True)
    with open(os.path.join("test_data", "src", "main.py"), "w") as f:
        f.write("print('Hello, world!')")
    
    print(f"Created test data structure in {os.path.abspath('test_data')}")
    return os.path.abspath("test_data")

def test_excel_folder_analysis():
    """Test the Excel folder detection and analysis"""
    # Create test data
    test_dir = create_test_excel_folder()
    
    # Create output directory
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize shared state
    shared = {
        "local_dir": test_dir,
        "output_dir": output_dir,
        "use_cache": False,  # Don't use cache for testing
        "project_name": "Excel Folder Test"
    }
    
    # Create analysis flow
    fetch_repo = FetchRepo()
    analyze_code = AnalyzeCode(max_retries=2)
    generate_report = GenerateReport()
    
    # Connect nodes
    fetch_repo >> analyze_code >> generate_report
    
    # Create flow
    flow = Flow(start=fetch_repo)
    
    # Run the flow
    print("\nRunning analysis flow...")
    flow.run(shared)
    
    # Check if report was generated
    report_path = os.path.join(output_dir, "analysis_report.html")
    if os.path.exists(report_path):
        print(f"\nReport generated successfully: {report_path}")
        print("Open the report to verify Excel folder content is properly included")
    else:
        print("\nERROR: Report was not generated")
    
def cleanup():
    """Clean up test data and output"""
    try:
        shutil.rmtree("test_data")
        shutil.rmtree("test_output")
        print("Test data and output cleaned up")
    except Exception as e:
        print(f"Error cleaning up: {e}")

if __name__ == "__main__":
    try:
        test_excel_folder_analysis()
        
        # Ask user if they want to clean up
        response = input("\nDo you want to clean up test data? (y/n): ")
        if response.lower() == 'y':
            cleanup()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError running test: {e}") 