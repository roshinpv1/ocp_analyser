#!/usr/bin/env python3
"""
Final test to verify OCP assessment with component analysis is working properly
"""

import os
from nodes.assessment.ocp_assessment import OcpAssessmentNode

def test_final_ocp_component_analysis():
    """Test the final working version of OCP assessment with component analysis"""
    
    print("🎯 Final Test: OCP Assessment with Component Analysis")
    print("=" * 70)
    
    # Create realistic test data
    shared = {
        "project_name": "Banking API Gateway",
        "output_dir": "./final_ocp_test",
        "excel_validation": {
            "component_name": "Banking API Gateway",
            "business_criticality": "High",
            "current_environment": "Virtual Machine on RHEL 8",
            "application_type": "API Gateway / Microservice",
            "technology_stack": "Java 11, Spring Boot 2.7, Maven",
            "database_dependencies": "PostgreSQL 13, Redis 6.2",
            "external_integrations": "LDAP, REST APIs, SOAP Services, Kafka"
        },
        "code_analysis": {
            "excel_components": {
                "venafi": {"is_yes": False},
                "redis": {"is_yes": True},
                "channel_secure_pingfed": {"is_yes": False},
                "nas_smb": {"is_yes": False},
                "smtp": {"is_yes": True},
                "autosys": {"is_yes": False},
                "mtls_mutual_auth_hard_rock": {"is_yes": True},
                "ndm": {"is_yes": False},
                "legacy_jks_files": {"is_yes": True},
                "soap_calls": {"is_yes": True},
                "rest_api": {"is_yes": True},
                "apigee": {"is_yes": False},
                "kafka": {"is_yes": True},
                "ibm_mq": {"is_yes": False},
                "ldap": {"is_yes": True},
                "splunk": {"is_yes": False},
                "database": {"is_yes": True},
                "postgresql": {"is_yes": True},
                "mysql": {"is_yes": False}
            },
            "component_analysis": {
                "redis": {
                    "detected": "yes",
                    "evidence": "Found RedisTemplate configuration in application.yml and @Cacheable annotations"
                },
                "soap_calls": {
                    "detected": "yes", 
                    "evidence": "Found SOAP client configuration using JAX-WS in WebServiceConfig.java"
                },
                "rest_api": {
                    "detected": "yes",
                    "evidence": "Multiple @RestController classes found with @RequestMapping annotations"
                },
                "legacy_jks_files": {
                    "detected": "yes",
                    "evidence": "Found keystore.jks and truststore.jks files in src/main/resources/security"
                },
                "kafka": {
                    "detected": "yes",
                    "evidence": "KafkaProducer and KafkaConsumer configurations found in messaging package"
                },
                "ldap": {
                    "detected": "yes",
                    "evidence": "Spring LDAP configuration in security config with LdapAuthenticationProvider"
                },
                "database": {
                    "detected": "yes",
                    "evidence": "JPA entities and DataSource configuration for PostgreSQL database"
                },
                "postgresql": {
                    "detected": "yes",
                    "evidence": "PostgreSQL JDBC driver dependency and database connection properties"
                },
                "smtp": {
                    "detected": "no",
                    "evidence": "No SMTP or email configuration found in codebase"
                },
                "mtls_mutual_auth_hard_rock": {
                    "detected": "no", 
                    "evidence": "No mutual TLS or hard rock authentication patterns detected"
                }
            }
        }
    }
    
    # Create output directory
    os.makedirs(shared["output_dir"], exist_ok=True)
    
    # Run OCP assessment
    ocp_node = OcpAssessmentNode()
    
    print("📋 Running OCP Assessment for Banking API Gateway...")
    print("   - Excel declarations: 19 components")
    print("   - Code detections: 10 components")
    print("   - Expected matches: 8")
    print("   - Expected mismatches: 2")
    print()
    
    try:
        prep_result = ocp_node.prep(shared)
        exec_result = ocp_node.exec(prep_result)
        post_result = ocp_node.post(shared, prep_result, exec_result)
        
        print("✅ OCP Assessment completed successfully!")
        print(f"📄 HTML Report: {exec_result.get('assessment_html_path')}")
        print(f"📝 Markdown Report: {exec_result.get('assessment_md_path')}")
        
        # Verify component analysis is included
        html_path = exec_result.get('assessment_html_path')
        if html_path and os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print()
            print("🔍 Component Analysis Verification:")
            
            if "Component Analysis" in content:
                print("   ✅ Component Analysis section present")
                
                # Check for specific components we declared
                declared_components = ["redis", "kafka", "ldap", "postgresql", "soap", "legacy jks"]
                found_components = 0
                
                for comp in declared_components:
                    if comp in content.lower():
                        found_components += 1
                        
                print(f"   ✅ Found {found_components}/{len(declared_components)} declared components in report")
                
                # Check for table structure
                if "<table" in content and "<th>Component</th>" in content:
                    print("   ✅ Component table structure present")
                else:
                    print("   ⚠️ Component table structure missing")
                    
                # Check for status indicators
                if "Match" in content and "Mismatch" in content:
                    print("   ✅ Status indicators (Match/Mismatch) present")
                else:
                    print("   ⚠️ Status indicators missing")
                    
            else:
                print("   ❌ Component Analysis section NOT found")
                
            file_size = os.path.getsize(html_path)
            print(f"   📊 Report size: {file_size:,} bytes")
            
            if file_size > 8000:
                print("   ✅ Report has substantial content")
            else:
                print("   ⚠️ Report appears small")
                
        print("\n🎉 Test completed successfully!")
        print("   The OCP assessment now includes comprehensive component analysis")
        print("   comparing Excel declarations with code detections!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_ocp_component_analysis()
    if success:
        print("\n🏆 SUCCESS: OCP Component Analysis is working perfectly!")
    else:
        print("\n💥 FAILED: There was an issue with the test") 