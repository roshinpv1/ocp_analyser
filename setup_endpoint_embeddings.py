#!/usr/bin/env python3
"""
Setup script to configure endpoint embeddings for OCP Analyser

This script configures the system to use endpoint embeddings instead of local models.
"""

import os
import sys

def create_env_config():
    """Create environment configuration for endpoint embeddings."""
    env_content = """# ChromaDB Configuration
USE_CHROMADB=true

# Embedding Configuration - Use endpoint embeddings instead of local models
USE_LOCAL_EMBEDDINGS=false
USE_ENDPOINT_EMBEDDINGS=true
EMBEDDING_ENDPOINT_URL=http://localhost:1234
EMBEDDING_ENDPOINT_TIMEOUT=30

# ChromaDB Storage
CHROMADB_PERSIST_DIR=./chroma_db
CHROMADB_ANALYSIS_COLLECTION=analysis_reports
CHROMADB_OCP_COLLECTION=ocp_assessments

# Local Embedding Configuration (disabled but kept for reference)
LOCAL_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
LOCAL_MODEL_CACHE_DIR=./model_cache

# Output Configuration
DEFAULT_OUTPUT_DIR=./out
DEFAULT_PROJECT_NAME=Unknown Project

# OpenAI API Key (if needed for fallback)
# OPENAI_API_KEY=your_openai_api_key_here
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with endpoint embedding configuration")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {str(e)}")
        return False

def test_endpoint_connection():
    """Test if the embedding endpoint is accessible."""
    try:
        import requests
        response = requests.get("http://localhost:1234/health", timeout=5)
        if response.status_code == 200:
            print("✅ Embedding endpoint is accessible at http://localhost:1234")
            return True
        else:
            print(f"⚠️  Embedding endpoint responded with status {response.status_code}")
            return False
    except ImportError:
        print("⚠️  requests library not available for endpoint testing")
        print("   Install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Cannot connect to embedding endpoint: {str(e)}")
        print("   Make sure your embedding service is running on port 1234")
        return False

def verify_dependencies():
    """Verify that required dependencies are available."""
    dependencies = ['chromadb', 'requests']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} is available")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} is missing")
    
    if missing:
        print(f"\nTo install missing dependencies:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def main():
    """Main setup function."""
    print("🔧 Setting up endpoint embeddings for OCP Analyser")
    print("=" * 50)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    deps_ok = verify_dependencies()
    
    # Create configuration
    print("\n2. Creating configuration...")
    config_ok = create_env_config()
    
    # Test endpoint
    print("\n3. Testing endpoint connection...")
    endpoint_ok = test_endpoint_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("Setup Summary:")
    print(f"  Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"  Configuration: {'✅' if config_ok else '❌'}")
    print(f"  Endpoint Connection: {'✅' if endpoint_ok else '⚠️'}")
    
    if config_ok:
        print("\n🎉 Endpoint embeddings configured successfully!")
        print("\nConfiguration details:")
        print("  - ChromaDB storage: Enabled")
        print("  - Local embeddings: Disabled")
        print("  - Endpoint embeddings: Enabled")
        print("  - Endpoint URL: http://localhost:1234")
        print("  - Timeout: 30 seconds")
        
        if not endpoint_ok:
            print("\n⚠️  Note: Embedding endpoint is not currently accessible.")
            print("   Make sure to start your embedding service on port 1234 before running analysis.")
            
        print("\n✨ You can now run OCP Analyser with endpoint embeddings!")
        print("   Example: python main.py --dir /path/to/code --output results")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 