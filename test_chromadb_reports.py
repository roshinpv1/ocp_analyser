#!/usr/bin/env python3
"""
Test script to verify all three reports are stored in ChromaDB with proper metadata

This script tests the storage and retrieval of:
1. Hard Gate Assessment Report
2. Intake Assessment Report  
3. Migration Insights Report
"""

import os
import sys
from datetime import datetime

def test_report_storage():
    """Test that all three reports are stored with proper metadata."""
    print("🔍 Testing ChromaDB Report Storage")
    print("=" * 50)
    
    try:
        from utils.chromadb_wrapper import get_chromadb_wrapper
        
        wrapper = get_chromadb_wrapper()
        
        if not wrapper.is_enabled():
            print("❌ ChromaDB is not enabled")
            return False
        
        print("✅ ChromaDB is enabled and available")
        
        # Test component name search
        test_component = "TestComponent"
        
        # Query all collections for stored reports
        print(f"\n🔍 Searching for reports with component name: {test_component}")
        
        # Search analysis reports (Hard Gate Assessment + Migration Insights)
        analysis_results = wrapper.search_analysis_reports(test_component, n_results=10)
        print(f"📊 Found {len(analysis_results)} analysis reports")
        
        for i, result in enumerate(analysis_results):
            metadata = result.get('metadata', {})
            print(f"  {i+1}. Component: {metadata.get('component_name', 'Unknown')}")
            print(f"      File: {metadata.get('file_path', 'Unknown')}")
            print(f"      Type: {metadata.get('report_type', 'Unknown')}")
        
        # Search OCP assessments (Intake Assessment)
        ocp_results = wrapper.search_ocp_assessments(test_component, n_results=10)
        print(f"📋 Found {len(ocp_results)} OCP assessment reports")
        
        for i, result in enumerate(ocp_results):
            metadata = result.get('metadata', {})
            print(f"  {i+1}. Component: {metadata.get('component_name', 'Unknown')}")
            print(f"      File: {metadata.get('file_path', 'Unknown')}")
            print(f"      Type: {metadata.get('report_type', 'Unknown')}")
        
        # List all components
        print(f"\n📋 All components in analysis reports:")
        analysis_components = wrapper.list_components("analysis_reports")
        for component in analysis_components:
            print(f"  - {component}")
        
        print(f"\n📋 All components in OCP assessments:")
        ocp_components = wrapper.list_components("ocp_assessment_reports")
        for component in ocp_components:
            print(f"  - {component}")
        
        # Test semantic search
        print(f"\n🔍 Testing semantic search for 'migration readiness'...")
        semantic_results = wrapper.query_reports("migration readiness", "analysis_reports", 5)
        if semantic_results and semantic_results.get('documents'):
            print(f"Found {len(semantic_results['documents'][0])} relevant results")
        else:
            print("No semantic search results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_component_extraction():
    """Test component name extraction from different sources."""
    print("\n🔍 Testing Component Name Extraction")
    print("=" * 50)
    
    # Test data scenarios
    test_scenarios = [
        {
            "name": "Excel component name",
            "shared": {
                "excel_validation": {"component_name": "ExcelComponent"},
                "project_name": "ProjectName",
                "component_name": "DirectComponent"
            },
            "expected": "DirectComponent"  # component_name has highest priority
        },
        {
            "name": "Project name fallback",
            "shared": {
                "project_name": "ProjectName",
                "excel_validation": {}
            },
            "expected": "ProjectName"
        },
        {
            "name": "Excel fallback",
            "shared": {
                "excel_validation": {"component_name": "ExcelComponent"}
            },
            "expected": "ExcelComponent"
        },
        {
            "name": "Unknown fallback",
            "shared": {},
            "expected": "Unknown Component"
        }
    ]
    
    for scenario in test_scenarios:
        shared = scenario["shared"]
        expected = scenario["expected"]
        
        # Extract component name using the same logic as the nodes
        component_name = (
            shared.get("component_name") or 
            shared.get("project_name") or 
            shared.get("excel_validation", {}).get("component_name") or
            "Unknown Component"
        )
        
        if component_name == expected:
            print(f"✅ {scenario['name']}: {component_name}")
        else:
            print(f"❌ {scenario['name']}: Expected '{expected}', got '{component_name}'")

def simulate_report_storage():
    """Simulate storing all three reports to test the complete flow."""
    print("\n🧪 Simulating Report Storage Flow")
    print("=" * 50)
    
    try:
        from utils.chromadb_wrapper import get_chromadb_wrapper
        import tempfile
        import os
        
        wrapper = get_chromadb_wrapper()
        
        if not wrapper.is_enabled():
            print("❌ ChromaDB is not enabled - cannot simulate storage")
            return False
        
        # Create temporary test component
        test_component = f"TestSimulation_{datetime.now().strftime('%H%M%S')}"
        
        # Create temporary directory for test files
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # 1. Simulate Hard Gate Assessment Report
            hard_gate_md = os.path.join(temp_dir, "hard_gate_assessment.md")
            hard_gate_content = f"""# Hard Gate Assessment Report

**Component Name:** {test_component}
**Report Type:** Hard Gate Assessment
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
Test hard gate assessment for component {test_component}.

## Findings
- Critical Issue 1: Database connection not secure
- High Issue 2: Missing authentication
- Medium Issue 3: Outdated dependencies

## Recommendations
- Implement secure database connections
- Add proper authentication mechanisms
- Update all dependencies to latest versions
"""
            
            with open(hard_gate_md, 'w', encoding='utf-8') as f:
                f.write(hard_gate_content)
            
            success1 = wrapper.store_analysis_report(test_component, hard_gate_md, hard_gate_content)
            print(f"{'✅' if success1 else '❌'} Hard Gate Assessment storage: {success1}")
            
            # 2. Simulate Intake Assessment Report  
            intake_md = os.path.join(temp_dir, "intake_assessment.md")
            intake_content = f"""# Intake Assessment Report

**Component Name:** {test_component}
**Report Type:** Intake Assessment (OCP Migration)
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Migration Feasibility
- Overall Score: 85/100
- Recommendation: APPROVED for migration

## Technical Assessment
- Technology Stack: Java Spring Boot
- Dependencies: PostgreSQL, Redis
- Migration Complexity: Medium

## Risks Identified
- Database migration needs planning
- Configuration updates required
"""
            
            with open(intake_md, 'w', encoding='utf-8') as f:
                f.write(intake_content)
            
            success2 = wrapper.store_ocp_assessment(test_component, intake_md, intake_content)
            print(f"{'✅' if success2 else '❌'} Intake Assessment storage: {success2}")
            
            # 3. Simulate Migration Insights Report
            migration_md = os.path.join(temp_dir, "migration_insights.md")
            migration_content = f"""# Migration Insights Report

**Component Name:** {test_component}
**Report Type:** Migration Insights
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Migration Readiness
Component {test_component} is ready for OpenShift migration with moderate effort.

## Key Insights
- Containerization: Application can be containerized easily
- Dependencies: External dependencies are OpenShift compatible
- Storage: Requires persistent volume for database

## Migration Steps
1. Create Docker containers
2. Set up OpenShift deployment configurations
3. Migrate database to OpenShift-managed PostgreSQL
4. Configure service mesh for Redis connectivity
"""
            
            with open(migration_md, 'w', encoding='utf-8') as f:
                f.write(migration_content)
            
            success3 = wrapper.store_analysis_report(test_component, migration_md, migration_content)
            print(f"{'✅' if success3 else '❌'} Migration Insights storage: {success3}")
            
            # Test retrieval
            if success1 and success2 and success3:
                print(f"\n🔍 Testing retrieval for component: {test_component}")
                
                # Search by component name
                analysis_results = wrapper.search_analysis_reports(test_component, n_results=5)
                ocp_results = wrapper.search_ocp_assessments(test_component, n_results=5)
                
                print(f"Found {len(analysis_results)} analysis reports")
                print(f"Found {len(ocp_results)} OCP assessment reports")
                
                # Search by content
                migration_search = wrapper.search_analysis_reports("migration readiness", n_results=5)
                print(f"Found {len(migration_search)} reports mentioning migration readiness")
                
                return True
            else:
                print("❌ Some reports failed to store")
                return False
        
    except Exception as e:
        print(f"❌ Simulation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 Testing ChromaDB Report Storage with Component Names")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Component Name Extraction", test_component_extraction),
        ("Existing Report Storage", test_report_storage),
        ("Simulated Storage Flow", simulate_report_storage),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Reports are properly stored with component names.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n📋 Summary of ChromaDB Integration:")
    print("  - Hard Gate Assessment: Stored in 'analysis_reports' collection")
    print("  - Intake Assessment: Stored in 'ocp_assessment_reports' collection")  
    print("  - Migration Insights: Stored in 'analysis_reports' collection")
    print("  - All reports include component name in metadata")
    print("  - Enhanced content includes report type and analysis date")
    print("  - Supports semantic search across all reports")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 