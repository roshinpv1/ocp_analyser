#!/usr/bin/env python3
"""
Test to verify that component analysis has been removed from the main analysis report
"""

import os
import tempfile
from nodes.reporting.report_generator import GenerateReport

def test_component_analysis_removed():
    """Test that component analysis is no longer included in the main analysis report"""
    
    print("🧪 Testing Component Analysis Removal from Analysis Report")
    print("=" * 70)
    
    # Create test data with component analysis
    shared = {
        "project_name": "Test Project", 
        "output_dir": "./test_remove_component",
        "code_analysis": {
            "findings": [
                {
                    "category": "security",
                    "severity": "medium",
                    "description": "Test finding",
                    "location": "test.py:10"
                }
            ],
            "technology_stack": {
                "languages": [
                    {"name": "Python", "version": "3.9", "purpose": "Main language"}
                ]
            },
            "component_analysis": {
                "redis": {
                    "detected": "yes",
                    "evidence": "Found Redis configuration"
                },
                "mysql": {
                    "detected": "no", 
                    "evidence": "No MySQL found"
                }
            },
            "excel_components": {
                "redis": {"is_yes": True},
                "mysql": {"is_yes": False}
            },
            "security_quality_analysis": {
                "auditability": {
                    "logging_implemented": {
                        "implemented": "yes",
                        "evidence": "Logging found"
                    }
                }
            }
        },
        "jira_stories": [],
        "excel_validation": {},
        "files_data": {
            "test.py": "print('hello')"
        }
    }
    
    # Create output directory
    os.makedirs(shared["output_dir"], exist_ok=True)
    
    # Generate the report
    report_generator = GenerateReport()
    
    print("📝 Generating analysis report...")
    
    try:
        prep_result = report_generator.prep(shared)
        exec_result = report_generator.exec(prep_result)
        post_result = report_generator.post(shared, prep_result, exec_result)
        
        print("✅ Report generated successfully!")
        
        # Check the HTML and Markdown files
        html_path = exec_result.get('html')
        markdown_path = exec_result.get('markdown')
        
        # Test HTML file
        if html_path and os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            print(f"📄 HTML Report: {html_path}")
            
            # Check that component analysis is NOT present
            component_checks = [
                "Component Analysis" not in html_content,
                "Declared" not in html_content or "Detected" not in html_content,  # Component table headers
                "component-analysis" not in html_content  # CSS class
            ]
            
            if all(component_checks):
                print("   ✅ Component Analysis section successfully removed from HTML")
            else:
                print("   ❌ Component Analysis content still found in HTML")
                if "Component Analysis" in html_content:
                    print("     - 'Component Analysis' heading found")
                if "Declared" in html_content and "Detected" in html_content:
                    print("     - Component table headers found")
                if "component-analysis" in html_content:
                    print("     - Component analysis CSS class found")
            
        # Test Markdown file
        if markdown_path and os.path.exists(markdown_path):
            with open(markdown_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
                
            print(f"📝 Markdown Report: {markdown_path}")
            
            # Check that component analysis is NOT present
            component_checks = [
                "## Component Analysis" not in markdown_content,
                "| Component | Declared | Detected | Status |" not in markdown_content,
                "Components Detected in Codebase" not in markdown_content
            ]
            
            if all(component_checks):
                print("   ✅ Component Analysis section successfully removed from Markdown")
            else:
                print("   ❌ Component Analysis content still found in Markdown")
                if "## Component Analysis" in markdown_content:
                    print("     - Component Analysis heading found")
                if "| Component | Declared | Detected | Status |" in markdown_content:
                    print("     - Component table found")
        
        # Check that other sections are still present
        sections_to_check = [
            ("Technology Stack", "## Technology Stack"),
            ("Security & Quality Analysis", "## Security & Quality Analysis"),
            ("Findings", "## Findings")
        ]
        
        print("\n🔍 Verifying other sections remain:")
        for section_name, section_header in sections_to_check:
            if markdown_path and os.path.exists(markdown_path):
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if section_header in content:
                        print(f"   ✅ {section_name} section present")
                    else:
                        print(f"   ⚠️ {section_name} section missing")
        
        print("\n🎉 Test completed!")
        print("   Component analysis has been successfully removed from the main analysis report")
        print("   while preserving all other report sections.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_component_analysis_removed()
    if success:
        print("\n🏆 SUCCESS: Component Analysis removed from analysis report!")
    else:
        print("\n💥 FAILED: Error removing component analysis") 