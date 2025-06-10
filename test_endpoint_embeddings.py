#!/usr/bin/env python3
"""
Test script for endpoint embeddings functionality

This script tests the endpoint embedding integration with ChromaDB.
"""

import os
import sys
import tempfile
import shutil

def test_endpoint_embedding_function():
    """Test the endpoint embedding function directly."""
    print("Testing endpoint embedding function...")
    
    try:
        from utils.endpoint_embedding import EndpointEmbeddingFunction
        
        # Initialize the embedding function
        embedding_func = EndpointEmbeddingFunction("http://localhost:1234")
        
        # Test with sample texts
        test_texts = ["Hello, world!", "This is a test.", "Endpoint embeddings work!"]
        embeddings = embedding_func(test_texts)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        print(f"✅ Embedding dimension: {len(embeddings[0])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint embedding test failed: {str(e)}")
        return False

def test_chromadb_with_endpoints():
    """Test ChromaDB integration with endpoint embeddings."""
    print("Testing ChromaDB with endpoint embeddings...")
    
    try:
        from utils.endpoint_chromadb_store import EndpointReportStore
        
        # Create a temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Initialize the store
            store = EndpointReportStore(
                persist_directory=temp_dir,
                endpoint_url="http://localhost:1234",
                timeout=30
            )
            
            # Test storing a report
            test_content = "This is a test analysis report for component testing."
            report_id = store.store_analysis_report(
                component_name="test_component",
                report_file_path="test_report.html",
                report_content=test_content
            )
            
            if report_id:
                print(f"✅ Stored test report with ID: {report_id}")
                
                # Test querying
                results = store.query_reports("test analysis", n_results=1)
                if results and results.get('documents') and len(results['documents'][0]) > 0:
                    print("✅ Successfully queried stored report")
                    return True
                else:
                    print("❌ Query returned no results")
                    return False
            else:
                print("❌ Failed to store test report")
                return False
                
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ ChromaDB endpoint test failed: {str(e)}")
        return False

def test_config_integration():
    """Test configuration integration for endpoint embeddings."""
    print("Testing configuration integration...")
    
    try:
        from utils.config import get_config
        
        config = get_config()
        
        print(f"✅ ChromaDB enabled: {config.use_chromadb}")
        print(f"✅ Local embeddings: {config.use_local_embeddings}")
        print(f"✅ Endpoint embeddings: {config.use_endpoint_embeddings}")
        print(f"✅ Endpoint URL: {config.embedding_endpoint_url}")
        print(f"✅ Endpoint timeout: {config.embedding_endpoint_timeout}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {str(e)}")
        return False

def test_chromadb_wrapper():
    """Test the ChromaDB wrapper with endpoint embeddings."""
    print("Testing ChromaDB wrapper...")
    
    try:
        from utils.chromadb_wrapper import get_chromadb_wrapper
        
        wrapper = get_chromadb_wrapper()
        
        if wrapper.is_enabled():
            print("✅ ChromaDB wrapper is enabled")
            
            # Test storing a simple report
            success = wrapper.store_analysis_report(
                component_name="test_wrapper",
                report_file_path="test.html",
                report_content="Test content for wrapper"
            )
            
            if success:
                print("✅ Successfully stored report via wrapper")
                return True
            else:
                print("⚠️  Report storage returned False")
                return False
        else:
            print("❌ ChromaDB wrapper is disabled")
            return False
            
    except Exception as e:
        print(f"❌ ChromaDB wrapper test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Endpoint Embeddings Integration")
    print("=" * 50)
    
    tests = [
        ("Configuration Integration", test_config_integration),
        ("Endpoint Embedding Function", test_endpoint_embedding_function),
        ("ChromaDB with Endpoints", test_chromadb_with_endpoints),
        ("ChromaDB Wrapper", test_chromadb_wrapper),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Endpoint embeddings are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("   Make sure your embedding endpoint is running on port 1234.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 