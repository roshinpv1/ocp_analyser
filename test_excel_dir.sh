#!/bin/bash

# Create a test directory for Excel files
TEST_DIR="test_excel_files"
mkdir -p $TEST_DIR

# Create output directory
OUTPUT_DIR="excel_analysis_results"
mkdir -p $OUTPUT_DIR

# Check if we should create sample Excel files
if [ "$1" == "create-samples" ]; then
    echo "Creating sample Excel files..."
    
    # This requires Python with openpyxl
    python3 -c "
import openpyxl
from openpyxl import Workbook

# Create sample Excel files
for i in range(1, 4):
    wb = Workbook()
    ws = wb.active
    ws.title = 'IntakeForm'
    
    # Add some sample data
    ws['A1'] = f'TestComponent{i}'
    ws['B2'] = 'Git repo URL:'
    ws['C2'] = f'https://github.com/test/component{i}'
    ws['B3'] = 'Is the component using Redis?'
    ws['C3'] = 'Yes' if i % 2 == 0 else 'No'
    ws['B4'] = 'Is the component using Kafka?'
    ws['C4'] = 'Yes' if i % 2 == 1 else 'No'
    
    # Save the file
    filename = f'test_excel_files/component{i}.xlsx'
    wb.save(filename)
    print(f'Created {filename}')
"
    if [ $? -ne 0 ]; then
        echo "Failed to create sample Excel files. Make sure openpyxl is installed."
        echo "You can install it with: pip install openpyxl"
        exit 1
    fi
fi

# Count the Excel files
EXCEL_COUNT=$(ls -1 $TEST_DIR/*.xlsx 2>/dev/null | wc -l)
if [ $EXCEL_COUNT -eq 0 ]; then
    echo "No Excel files found in $TEST_DIR directory."
    echo "Run this script with 'create-samples' argument to create sample files:"
    echo "  ./test_excel_dir.sh create-samples"
    exit 1
fi

echo "Found $EXCEL_COUNT Excel files in $TEST_DIR directory."
echo "Processing all Excel files..."

# Run the main.py script with the excel-dir option
python3 main.py --excel-dir $TEST_DIR --output $OUTPUT_DIR

echo "Processing complete. Check $OUTPUT_DIR for results." 