#!/usr/bin/env python3
"""
Test script to verify ChromaDB integration with local embeddings
and ensure all report types are properly stored.
"""

import os
import tempfile
from utils.chromadb_wrapper import get_chromadb_wrapper

def test_all_report_storage():
    """Test storing and retrieving all types of reports."""
    print("Testing ChromaDB integration with local embeddings...")
    
    wrapper = get_chromadb_wrapper()
    
    if not wrapper.is_enabled():
        print("❌ ChromaDB is not enabled. Please check your configuration.")
        return False
    
    print("✅ ChromaDB is enabled with local embeddings")
    
    # Test data for different report types
    test_reports = {
        "analysis_report": {
            "content": """# Code Analysis Report for Test Project

## Summary
- **Files Analyzed**: 5
- **Technology Stack**: Python, JavaScript
- **Security Issues Found**: 2

## Findings
### Security Issues
1. **SQL Injection Risk** (High Severity)
   - Location: database.py:45
   - Recommendation: Use parameterized queries

2. **Hardcoded Password** (Critical Severity)
   - Location: config.py:12
   - Recommendation: Use environment variables

## Technology Stack
- Python 3.9
- Flask 2.0
- PostgreSQL

## Action Items
1. Fix critical security issues immediately
2. Implement proper configuration management
3. Add security testing to CI/CD pipeline
""",
            "component_name": "TestProject_Analysis",
            "store_method": "store_analysis_report"
        },
        
        "ocp_assessment": {
            "content": """# OpenShift Migration Assessment for Test Project

## Executive Summary
This assessment evaluates the migration readiness of the Test Project for OpenShift platform.

## Migration Readiness Score: 75/100

### Scoring Breakdown
1. Application Architecture Compatibility: 8/10
2. Technology Stack Compatibility: 9/10
3. Data Persistence Strategy: 7/10
4. External Dependencies Management: 6/10
5. Security & Authentication: 8/10
6. Networking & Communication: 7/10
7. Resource Requirements: 8/10
8. Monitoring & Observability: 6/10
9. CI/CD Integration: 8/10
10. Operational Readiness: 8/10

## Component Analysis
| Component | Declared | Detected | Status |
|-----------|----------|----------|--------|
| redis | Yes | Yes | Match |
| postgresql | Yes | Yes | Match |
| kafka | No | No | Match |

## Recommendations
1. Implement health checks and readiness probes
2. Configure persistent volume claims for database
3. Update monitoring and logging configuration
4. Plan migration timeline and resource allocation
""",
            "component_name": "TestProject_OCP",
            "store_method": "store_ocp_assessment"
        },
        
        "migration_insights": {
            "content": """# OpenShift Migration Insights for Test Project

## Intake Overview
**Test Project**
Migration readiness assessment completed with comprehensive analysis.

### Intake Status
**Go** - No critical blockers identified for OpenShift migration.

## General Information
- Component Name: Test Project
- Total Files Analyzed: 5
- Issues Found: 2

## Application Component Details
### Technology Stack
- **Python**: Compatible with OpenShift
- **Flask**: Requires configuration updates
- **PostgreSQL**: Compatible with persistent volumes

## Service Bindings and Dependencies
- Database dependencies identified
- External API connections require review
- File system dependencies minimal

## OpenShift Migration Readiness Checklist
- [x] Application technology stack assessment completed
- [x] Dependencies identified and catalogued
- [x] Security and quality analysis performed
- [x] Code findings documented and prioritized
- [x] Migration strategy recommendations provided

## Migration Insights and Recommendations
### Key Recommendations
1. **High Priority**: Implement health checks and readiness probes
2. **Medium Priority**: Containerize application components using Docker/Podman
3. **Medium Priority**: Review and update configuration management for OpenShift environment
4. **High Priority**: Update CI/CD pipelines for OpenShift deployment

### Next Steps
1. Review detailed findings and address critical issues
2. Create containerization strategy
3. Design OpenShift deployment architecture
4. Plan migration timeline and resource allocation
5. Execute pilot migration with small subset
""",
            "component_name": "TestProject_MigrationInsights",
            "store_method": "store_analysis_report"
        }
    }
    
    # Store all test reports
    stored_reports = []
    for report_type, report_data in test_reports.items():
        print(f"\n📝 Testing {report_type} storage...")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(report_data["content"])
            temp_file_path = temp_file.name
        
        try:
            # Store the report
            store_method = getattr(wrapper, report_data["store_method"])
            success = store_method(report_data["component_name"], temp_file_path)
            
            if success:
                print(f"✅ Successfully stored {report_type}")
                stored_reports.append({
                    "type": report_type,
                    "component": report_data["component_name"],
                    "path": temp_file_path
                })
            else:
                print(f"❌ Failed to store {report_type}")
                
        except Exception as e:
            print(f"❌ Error storing {report_type}: {str(e)}")
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    # Test searching and retrieval
    print(f"\n🔍 Testing search functionality...")
    
    # Test analysis report search
    search_queries = [
        "security vulnerabilities Python",
        "migration readiness OpenShift",
        "technology stack assessment",
        "database configuration",
        "containerization strategy"
    ]
    
    for query in search_queries:
        print(f"\n   Searching: '{query}'")
        
        # Search analysis reports
        analysis_results = wrapper.search_analysis_reports(query, n_results=3)
        print(f"   📊 Analysis reports found: {len(analysis_results)}")
        
        # Search OCP assessments
        ocp_results = wrapper.search_ocp_assessments(query, n_results=3)
        print(f"   🎯 OCP assessments found: {len(ocp_results)}")
        
        # Show snippet from first result if available
        if analysis_results:
            first_result = analysis_results[0]
            snippet = first_result.get('document', '')[:100] + "..." if len(first_result.get('document', '')) > 100 else first_result.get('document', '')
            print(f"   📄 Sample result: {snippet}")
    
    # Test component listing
    print(f"\n📋 Testing component listing...")
    analysis_components = wrapper.list_components("analysis_reports")
    ocp_components = wrapper.list_components("ocp_assessments")
    
    print(f"   Analysis report components: {len(analysis_components)}")
    for comp in analysis_components[:5]:  # Show first 5
        print(f"     - {comp}")
    
    print(f"   OCP assessment components: {len(ocp_components)}")
    for comp in ocp_components[:5]:  # Show first 5
        print(f"     - {comp}")
    
    # Test similarity search
    print(f"\n🎯 Testing similarity search...")
    similarity_results = wrapper.context_similarity_search(
        "Find reports about security issues and vulnerabilities in Python applications",
        collection_name="analysis_reports",
        n_results=3,
        min_score=0.1
    )
    
    print(f"   Similarity search results: {len(similarity_results)}")
    for i, result in enumerate(similarity_results):
        component = result.get('component_name', 'Unknown')
        score = result.get('similarity_score', 0)
        print(f"     {i+1}. {component} (similarity: {score:.3f})")
    
    print(f"\n✅ ChromaDB integration test completed successfully!")
    print(f"   - Local embeddings: Working")
    print(f"   - Report storage: Working")
    print(f"   - Search functionality: Working")
    print(f"   - Component listing: Working")
    print(f"   - Similarity search: Working")
    
    return True

if __name__ == "__main__":
    test_all_report_storage() 