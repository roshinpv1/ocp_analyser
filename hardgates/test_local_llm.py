#!/usr/bin/env python3
"""
Test script for local LLM integration with hardgates tool.
"""

import os
import sys
import json

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip

from utils.llm_client import call_llm

def test_local_llm():
    """Test local LLM connection and basic functionality"""
    
    print("🔧 Testing Local LLM Integration")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Configuration:")
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    print(f"Base URL: {base_url or 'Not set (will use OpenAI API)'}")
    print(f"API Key: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"Model: {model}")
    
    if not api_key:
        print("\n❌ OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    if not base_url:
        print("\n⚠️  OPENAI_BASE_URL not set - will use OpenAI API instead of local LLM")
        print("For local LLM, set: export OPENAI_BASE_URL='http://localhost:1234/v1'")
    
    # Test basic connectivity
    print("\n🔌 Testing LLM Connection...")
    
    test_prompt = """
    Please analyze this simple Python function and return a JSON response:
    
    def greet(name):
        return f"Hello, {name}!"
    
    Return JSON with the following structure:
    {
        "technology_stack": {
            "languages": ["Python"],
            "frameworks": []
        },
        "findings": [],
        "component_analysis": {
            "simple_function": "Basic greeting function"
        },
        "security_quality_analysis": {
            "testing": {
                "unit_testing": {
                    "implemented": "no",
                    "evidence": "No test cases found",
                    "recommendation": "Add unit tests for the greet function"
                }
            }
        }
    }
    """
    
    try:
        print("Sending test prompt to LLM...")
        result = call_llm(test_prompt)
        
        print("✅ LLM responded successfully!")
        print("\n📄 Response Summary:")
        
        # Check if response has expected structure
        if isinstance(result, dict):
            if "technology_stack" in result:
                print(f"  - Technology Stack: {result.get('technology_stack', {})}")
            if "findings" in result:
                print(f"  - Findings Count: {len(result.get('findings', []))}")
            if "component_analysis" in result:
                print(f"  - Component Analysis: {'✓' if result.get('component_analysis') else '✗'}")
            if "security_quality_analysis" in result:
                print(f"  - Security Analysis: {'✓' if result.get('security_quality_analysis') else '✗'}")
        else:
            print(f"  - Response Type: {type(result)}")
        
        print(f"\n📋 Full Response:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to LLM: {str(e)}")
        print("\n🔍 Troubleshooting suggestions:")
        print("1. Make sure your local LLM is running")
        print("2. Verify the OPENAI_BASE_URL is correct")
        print("3. Check if the model name is correct")
        print("4. Test direct access: curl http://localhost:1234/v1/models")
        return False

def test_model_availability():
    """Test if we can list available models"""
    base_url = os.getenv("OPENAI_BASE_URL")
    if not base_url:
        print("\n⚠️  Skipping model availability test (no base URL set)")
        return
    
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "test"),
            base_url=base_url
        )
        
        print("\n🤖 Available Models:")
        models = client.models.list()
        for model in models.data:
            print(f"  - {model.id}")
            
    except Exception as e:
        print(f"\n⚠️  Could not list models: {str(e)}")
        print("This is not necessarily a problem - your LLM might not support model listing")

if __name__ == "__main__":
    print("Hard Gates Local LLM Test")
    print("=" * 30)
    
    # Test basic connection
    success = test_local_llm()
    
    # Test model availability
    test_model_availability()
    
    # Final summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 Local LLM integration test PASSED!")
        print("\nYou can now run hard gates assessments with:")
        print("python3 main.py --repo https://github.com/user/repo --verbose")
    else:
        print("❌ Local LLM integration test FAILED!")
        print("\nPlease check your local LLM setup and try again.")
    
    sys.exit(0 if success else 1) 