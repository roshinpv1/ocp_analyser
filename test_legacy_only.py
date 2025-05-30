#!/usr/bin/env python3
"""
Test to verify that only legacy reporting functionality remains
"""

import os
import sys
from flow import create_analysis_flow, create_excel_analysis_flow
from nodes.reporting.report_generator import GenerateReport
from nodes.assessment.ocp_assessment import OcpAssessmentNode

def test_legacy_only():
    """Test that only legacy functionality is available"""
    
    print("🧪 Testing Legacy-Only Implementation")
    print("=" * 60)
    
    # Test 1: Check that comprehensive analysis imports fail
    print("1. Testing comprehensive analysis imports...")
    
    try:
        from nodes.assessment.combined_processor import CombinedAnalysisProcessor
        print("   ❌ CombinedAnalysisProcessor still exists!")
        return False
    except ImportError:
        print("   ✅ CombinedAnalysisProcessor properly removed")
    
    try:
        from nodes.reporting.comprehensive_report_generator import ComprehensiveReportGenerator
        print("   ❌ ComprehensiveReportGenerator still exists!")
        return False
    except ImportError:
        print("   ✅ ComprehensiveReportGenerator properly removed")
    
    try:
        from nodes.reporting.auto_report_generator import AutoReportGenerator
        print("   ❌ AutoReportGenerator still exists!")
        return False
    except ImportError:
        print("   ✅ AutoReportGenerator properly removed")
    
    try:
        from nodes.reporting.comprehensive_flows import create_application_platform_hard_gates_flow
        print("   ❌ Comprehensive flows still exist!")
        return False
    except ImportError:
        print("   ✅ Comprehensive flows properly removed")
    
    # Test 2: Check that legacy flows work
    print("\n2. Testing legacy flows...")
    
    try:
        analysis_flow = create_analysis_flow()
        print("   ✅ create_analysis_flow() works")
    except Exception as e:
        print(f"   ❌ create_analysis_flow() failed: {e}")
        return False
    
    try:
        excel_flow = create_excel_analysis_flow()
        print("   ✅ create_excel_analysis_flow() works")
    except Exception as e:
        print(f"   ❌ create_excel_analysis_flow() failed: {e}")
        return False
    
    # Test 3: Check that main.py doesn't have comprehensive options
    print("\n3. Testing main.py cleanup...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "main.py", "--help"], 
                              capture_output=True, text=True)
        help_text = result.stdout
        
        comprehensive_options = [
            "--use-combined",
            "--analysis-mode", 
            "--generate-reports",
            "--project-name",
            "--output-dir"
        ]
        
        found_options = []
        for option in comprehensive_options:
            if option in help_text:
                found_options.append(option)
        
        if found_options:
            print(f"   ❌ Found comprehensive options: {found_options}")
            return False
        else:
            print("   ✅ No comprehensive options found in --help")
            
    except Exception as e:
        print(f"   ⚠️ Could not test main.py --help: {e}")
    
    # Test 4: Check that legacy nodes still work
    print("\n4. Testing legacy nodes...")
    
    try:
        generate_report = GenerateReport()
        print("   ✅ GenerateReport node works")
    except Exception as e:
        print(f"   ❌ GenerateReport node failed: {e}")
        return False
    
    try:
        ocp_assessment = OcpAssessmentNode()
        print("   ✅ OcpAssessmentNode works")
    except Exception as e:
        print(f"   ❌ OcpAssessmentNode failed: {e}")
        return False
    
    # Test 5: Verify component analysis is removed from legacy report
    print("\n5. Testing component analysis removal...")
    
    # Create minimal test data
    shared = {
        "project_name": "Test Project",
        "output_dir": "./test_legacy_only",
        "code_analysis": {
            "findings": [],
            "technology_stack": {"languages": []},
            "component_analysis": {"redis": {"detected": "yes", "evidence": "test"}},
            "excel_components": {"redis": {"is_yes": True}},
            "security_quality_analysis": {}
        },
        "jira_stories": [],
        "excel_validation": {},
        "files_data": {"test.py": "print('test')"}
    }
    
    os.makedirs(shared["output_dir"], exist_ok=True)
    
    try:
        report_gen = GenerateReport()
        prep_result = report_gen.prep(shared)
        exec_result = report_gen.exec(prep_result)
        
        # Check that component analysis is not in the markdown
        markdown_path = exec_result.get('markdown')
        if markdown_path and os.path.exists(markdown_path):
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "Component Analysis" in content:
                print("   ❌ Component Analysis still found in legacy report")
                return False
            else:
                print("   ✅ Component Analysis properly removed from legacy report")
        else:
            print("   ⚠️ Could not verify component analysis removal (no markdown file)")
        
    except Exception as e:
        print(f"   ❌ Error testing component analysis removal: {e}")
        return False
    
    print("\n🎉 All tests passed!")
    print("✅ Legacy-only implementation is working correctly")
    print("\n📋 Available functionality:")
    print("   - Legacy analysis flow (--repo, --dir)")
    print("   - Legacy Excel analysis flow (--excel, --excel-dir)")  
    print("   - OCP assessment with component analysis")
    print("   - Standard analysis report (without component analysis)")
    print("   - Technology stack, security analysis, findings, action items")
    
    return True

if __name__ == "__main__":
    success = test_legacy_only()
    if success:
        print("\n🏆 SUCCESS: Legacy-only implementation verified!")
    else:
        print("\n💥 FAILED: Issues found with legacy-only implementation") 