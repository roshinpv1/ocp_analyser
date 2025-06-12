#!/usr/bin/env python3
"""
Setup script for Hard Gate Assessment Tool

This script helps set up the cleaned hard gate assessment project.
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False

def check_environment_variables():
    """Check for required environment variables"""
    print("\n🔧 Checking environment configuration...")
    
    # Check for LLM API keys
    llm_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    llm_configured = any(os.getenv(key) for key in llm_keys)
    
    if llm_configured:
        configured_providers = [key.replace("_API_KEY", "") for key in llm_keys if os.getenv(key)]
        print(f"✅ LLM provider(s) configured: {', '.join(configured_providers)}")
    else:
        print("⚠️  No LLM API key found. Set one of:")
        for key in llm_keys:
            print(f"   export {key}='your-key-here'")
    
    # Check for GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if github_token:
        print("✅ GitHub token configured")
    else:
        print("⚠️  GitHub token not found. For private repositories, set:")
        print("   export GITHUB_TOKEN='your-token-here'")
    
    return llm_configured

def setup_vscode_extension():
    """Help set up VS Code extension"""
    print("\n🔧 VS Code Extension Setup:")
    extension_dir = os.path.join(os.getcwd(), "extension")
    
    if os.path.exists(extension_dir):
        print("📁 Extension files found in ./extension/")
        print("📋 To develop the extension:")
        print("   1. cd extension/")
        print("   2. npm install")
        print("   3. Open extension/ folder in VS Code")
        print("   4. Press F5 to launch extension development host")
        print()
        print("📋 To install the extension:")
        print("   1. Package: vsce package")
        print("   2. Install: code --install-extension hard-gate-assessment-1.0.0.vsix")
    else:
        print("❌ Extension directory not found")

def create_sample_config():
    """Create sample configuration files"""
    print("\n📄 Creating sample configuration...")
    
    # Create .env.example
    env_example = """# LLM API Configuration (choose one)
OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key
# GOOGLE_API_KEY=your-google-key

# GitHub Configuration
GITHUB_TOKEN=your-github-token

# API Server Configuration (for VS Code extension)
API_HOST=localhost
API_PORT=8000
"""
    
    with open(".env.example", "w") as f:
        f.write(env_example)
    print("✅ Created .env.example")
    
    # Create VS Code settings example
    vscode_settings = """{
  "hardgates.apiUrl": "http://localhost:8000",
  "hardgates.githubToken": "${env:GITHUB_TOKEN}",
  "hardgates.defaultBranch": "main"
}"""
    
    os.makedirs(".vscode", exist_ok=True)
    with open(".vscode/settings.json.example", "w") as f:
        f.write(vscode_settings)
    print("✅ Created .vscode/settings.json.example")

def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running basic tests...")
    
    # Test imports
    try:
        from core.flow import Node, Flow
        from utils.github_client import fetch_github_repo
        from utils.llm_client import call_llm
        print("✅ Core modules import successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test CLI script
    if os.path.exists("main.py"):
        print("✅ CLI script found")
    else:
        print("❌ CLI script not found")
        return False
    
    # Test API script
    if os.path.exists("api.py"):
        print("✅ API script found")
    else:
        print("❌ API script not found")
        return False
    
    return True

def show_usage_examples():
    """Show usage examples"""
    print("\n🚀 Usage Examples:")
    print()
    print("📋 CLI Usage:")
    print("   python main.py --repo https://github.com/user/repo --token $GITHUB_TOKEN")
    print()
    print("🔧 API Server:")
    print("   python api.py")
    print("   # Then visit http://localhost:8000/docs")
    print()
    print("💻 VS Code Extension:")
    print("   1. Start API server: python api.py")
    print("   2. Open VS Code")
    print("   3. Cmd/Ctrl+Shift+P → 'Hard Gate Assessment: Analyze Repository'")
    print()

def main():
    """Main setup function"""
    print("🔧 Hard Gate Assessment Tool Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check environment
    llm_configured = check_environment_variables()
    
    # Create sample configs
    create_sample_config()
    
    # Setup VS Code extension info
    setup_vscode_extension()
    
    # Run tests
    if not run_tests():
        print("\n❌ Setup verification failed")
        sys.exit(1)
    
    # Show usage examples
    show_usage_examples()
    
    print("\n🎉 Setup completed successfully!")
    
    if not llm_configured:
        print("\n⚠️  Remember to configure an LLM API key before using the tool")
        print("   Choose one: OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY")

if __name__ == "__main__":
    main() 