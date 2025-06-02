# Batch Processing of Excel Files

This guide explains how to process multiple Excel files in a directory to generate analysis reports for each component.

## Overview

The code analyzer can now process a directory containing multiple Excel files, generating separate reports for each file. This is useful for analyzing multiple components at once.

## Usage

### Using the Command Line

```bash
python main.py --excel-dir /path/to/excel/files --output /path/to/output/directory
```

### Options

- `--excel-dir`: Directory containing Excel files to process
- `--output`: Output directory for reports (default: ./analysis_output)
- `--sheet`: (Optional) Sheet name in Excel files (will use the first sheet if not specified)
- `--dir`: (Optional) Local directory to analyze if not specified in Excel files
- `--no-cache`: (Optional) Disable LLM response caching
- `--include`: (Optional) File patterns to include in analysis
- `--exclude`: (Optional) File patterns to exclude from analysis

## Example

```bash
python main.py --excel-dir ./component_excel_files --output ./component_reports
```

This will:
1. Find all Excel files (*.xlsx, *.xls, *.xlsm) in the `./component_excel_files` directory
2. Process each Excel file separately
3. Generate analysis reports in separate subdirectories within `./component_reports`

## Testing

A test script is provided to demonstrate the batch processing functionality:

```bash
# First create sample Excel files
./test_excel_dir.sh create-samples

# Then process the sample Excel files
./test_excel_dir.sh
```

The script:
1. Creates a folder named `test_excel_files` with sample Excel files
2. Processes all Excel files in that directory
3. Generates reports in the `excel_analysis_results` directory

## Notes

- Each Excel file is processed independently
- Reports are saved in separate subdirectories named after the Excel files
- The directory structure will be:
  ```
  output_directory/
  ├── excelfile1_name/
  │   ├── analysis_report.html
  │   ├── analysis_report.md
  │   └── ocp_assessment.html
  ├── excelfile2_name/
  │   ├── analysis_report.html
  │   ├── analysis_report.md
  │   └── ocp_assessment.html
  └── ...
  ``` 