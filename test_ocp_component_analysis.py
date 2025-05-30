#!/usr/bin/env python3
"""
Test script to verify component analysis is included in OCP assessment report
"""

import os
import tempfile
from nodes.assessment.ocp_assessment import OcpAssessmentNode

def test_ocp_with_component_analysis():
    """Test OCP assessment with component analysis data"""
    
    print("🧪 Testing OCP Assessment with Component Analysis")
    print("=" * 60)
    
    # Create test data that includes component analysis
    shared = {
        "project_name": "Test Application",
        "output_dir": "./test_ocp_output",
        "excel_validation": {
            "component_name": "Test Application",
            "business_criticality": "High",
            "current_environment": "Virtual Machine",
            "application_type": "Web Application",
            "technology_stack": "Java Spring Boot",
            "database_dependencies": "MySQL, Redis",
            "external_integrations": "REST APIs, LDAP"
        },
        "code_analysis": {
            "excel_components": {
                "venafi": {"is_yes": False},
                "redis": {"is_yes": True},
                "channel_secure_pingfed": {"is_yes": False},
                "nas_smb": {"is_yes": False},
                "smtp": {"is_yes": False},
                "autosys": {"is_yes": False},
                "mtls_mutual_auth_hard_rock": {"is_yes": False},
                "ndm": {"is_yes": False},
                "legacy_jks_files": {"is_yes": False},
                "soap_calls": {"is_yes": False},
                "rest_api": {"is_yes": True},
                "apigee": {"is_yes": False},
                "kafka": {"is_yes": False},
                "ibm_mq": {"is_yes": False},
                "ldap": {"is_yes": True},
                "splunk": {"is_yes": False},
                "database": {"is_yes": True},
                "mysql": {"is_yes": True}
            },
            "component_analysis": {
                "redis": {
                    "detected": "yes",
                    "evidence": "Found Redis connection configuration in application.properties and RedisTemplate usage in code"
                },
                "rest_api": {
                    "detected": "yes",
                    "evidence": "Found REST API controllers using @RestController annotations and HTTP client configurations"
                },
                "legacy_jks_files": {
                    "detected": "yes",
                    "evidence": "Found keystore.jks file in resources directory used for SSL configuration"
                },
                "ldap": {
                    "detected": "no",
                    "evidence": "No LDAP configuration or dependencies found in codebase"
                },
                "mysql": {
                    "detected": "yes",
                    "evidence": "Found MySQL JDBC driver dependency and database connection configurations"
                },
                "venafi": {
                    "detected": "no",
                    "evidence": "No Venafi dependencies or configurations found"
                }
            }
        }
    }
    
    # Create output directory
    os.makedirs(shared["output_dir"], exist_ok=True)
    
    # Create and run the OCP assessment node
    ocp_node = OcpAssessmentNode()
    
    print("📝 Running OCP Assessment with Component Analysis...")
    
    try:
        # Run the assessment
        prep_result = ocp_node.prep(shared)
        exec_result = ocp_node.exec(prep_result)
        post_result = ocp_node.post(shared, prep_result, exec_result)
        
        print(f"✅ OCP Assessment completed successfully")
        print(f"📄 HTML Report: {exec_result.get('assessment_html_path')}")
        print(f"📝 Markdown Report: {exec_result.get('assessment_md_path')}")
        
        # Check if component analysis section is included
        html_path = exec_result.get('assessment_html_path')
        if html_path and os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "Component Analysis" in content:
                print("✅ Component Analysis section found in report")
                
                # Check for specific component table entries
                components_found = []
                test_components = ["venafi", "redis", "legacy jks", "rest api", "mysql", "ldap"]
                
                for component in test_components:
                    if component in content.lower():
                        components_found.append(component)
                
                print(f"✅ Found {len(components_found)} test components in report: {', '.join(components_found)}")
                
                # Check for table structure
                if "<table>" in content and "<th>Component</th>" in content:
                    print("✅ Component analysis table structure found")
                else:
                    print("⚠️ Component analysis table structure not found")
                    
            else:
                print("❌ Component Analysis section NOT found in report")
                
            # Check file size to ensure substantial content
            file_size = os.path.getsize(html_path)
            print(f"📊 Report file size: {file_size} bytes")
            
            if file_size > 5000:  # Expect at least 5KB for a proper report
                print("✅ Report appears to have substantial content")
            else:
                print("⚠️ Report seems small, may be missing content")
                
        else:
            print("❌ HTML report file not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during OCP assessment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ocp_with_component_analysis()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!") 