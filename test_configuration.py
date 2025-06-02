#!/usr/bin/env python3
"""
Test script for the configurable ChromaDB system
"""

import os
import sys

def test_config_loading():
    """Test configuration loading and display current settings."""
    print("=== Testing OCP Analyser Configuration ===\n")
    
    try:
        from utils.config import get_config
        
        config = get_config()
        print("Configuration loaded successfully!")
        print(config)
        print()
        
        return config
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        return None

def test_chromadb_wrapper():
    """Test ChromaDB wrapper functionality."""
    print("=== Testing ChromaDB Wrapper ===\n")
    
    try:
        from utils.chromadb_wrapper import get_chromadb_wrapper
        
        wrapper = get_chromadb_wrapper()
        
        print(f"ChromaDB Enabled: {wrapper.is_enabled()}")
        
        if wrapper.is_enabled():
            print("✓ ChromaDB storage is enabled and available")
            
            # Test storing a sample report
            test_metadata = {
                'project_name': 'Test Project',
                'file_path': '/test/path',
                'type': 'test_report',
                'timestamp': 'test_timestamp'
            }
            
            test_content = "This is a test analysis report content for configuration testing."
            
            print("\nTesting report storage...")
            success = wrapper.store_analysis_report(test_content, test_metadata)
            
            if success:
                print("✓ Successfully stored test analysis report")
                
                # Test searching
                print("\nTesting report search...")
                results = wrapper.search_analysis_reports("test analysis", n_results=1)
                
                if results:
                    print(f"✓ Successfully found {len(results)} test reports")
                    print(f"  First result project: {results[0].get('metadata', {}).get('project_name', 'Unknown')}")
                else:
                    print("⚠ No reports found in search")
            else:
                print("⚠ Failed to store test report")
        else:
            print("ℹ ChromaDB storage is disabled")
            print("  - Reports will be generated as HTML/PDF only")
            print("  - Vector search and agent features will be unavailable")
            print("  - This is normal if USE_CHROMADB=false")
        
    except Exception as e:
        print(f"Error testing ChromaDB wrapper: {str(e)}")

def test_environment_variables():
    """Test different environment variable configurations."""
    print("\n=== Testing Environment Variable Configuration ===\n")
    
    # Show current environment variables
    relevant_vars = [
        'USE_CHROMADB',
        'CHROMADB_PERSIST_DIR',
        'CHROMADB_ANALYSIS_COLLECTION',
        'CHROMADB_OCP_COLLECTION',
        'DEFAULT_OUTPUT_DIR',
        'DEFAULT_PROJECT_NAME'
    ]
    
    print("Current environment variables:")
    for var in relevant_vars:
        value = os.getenv(var, 'Not set')
        print(f"  {var}: {value}")
    
    print("\nTo change configuration:")
    print("1. Edit the .env file in the project root")
    print("2. Or set environment variables directly:")
    print("   export USE_CHROMADB=false")
    print("   export CHROMADB_PERSIST_DIR=./my_custom_db")

def demo_disable_chromadb():
    """Demonstrate how to disable ChromaDB dynamically."""
    print("\n=== Demonstrating ChromaDB Disable ===\n")
    
    # Temporarily set environment variable
    original_value = os.getenv('USE_CHROMADB')
    os.environ['USE_CHROMADB'] = 'false'
    
    try:
        # Import after setting environment variable
        import importlib
        import utils.config
        import utils.chromadb_wrapper
        
        # Reload modules to pick up new environment variable
        importlib.reload(utils.config)
        importlib.reload(utils.chromadb_wrapper)
        
        from utils.chromadb_wrapper import get_chromadb_wrapper
        
        wrapper = get_chromadb_wrapper()
        print(f"With USE_CHROMADB=false: {wrapper.is_enabled()}")
        
        # Test that storage operations return gracefully
        result = wrapper.store_analysis_report("test", {"test": "metadata"})
        print(f"Storage operation result: {result} (should be False)")
        
        results = wrapper.search_analysis_reports("test")
        print(f"Search operation result: {len(results)} results (should be 0)")
        
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['USE_CHROMADB'] = original_value
        else:
            os.environ.pop('USE_CHROMADB', None)

def main():
    """Run all configuration tests."""
    print("OCP Analyser Configuration Test\n")
    
    # Test 1: Configuration loading
    config = test_config_loading()
    
    if config:
        # Test 2: ChromaDB wrapper
        test_chromadb_wrapper()
        
        # Test 3: Environment variables
        test_environment_variables()
        
        # Test 4: Demonstrate disable functionality
        demo_disable_chromadb()
        
        print("\n=== Configuration Test Complete ===")
        print("\nNext steps:")
        print("1. Copy config.env.example to .env")
        print("2. Edit .env with your settings")
        print("3. Run the main analysis: python main.py")
        print("4. Use query tools: python query_reports.py list")
    else:
        print("Configuration test failed. Please check your setup.")

if __name__ == "__main__":
    main() 