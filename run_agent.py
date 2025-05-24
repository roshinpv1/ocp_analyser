#!/usr/bin/env python3
"""
Script to run the OCP Flow agent
"""

import os
import sys

# Make sure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from agent.ocp_flow.agent import root_agent
    
    print("OCP Flow Agent started. Press Ctrl+C to exit.")
    print("="*50)
    print("Ask questions about the reports stored in ChromaDB.")
    print("Example: 'What security vulnerabilities were found in the Python application?'")
    print("="*50)
    
    # Start the agent
    root_agent.run()
    
except ImportError as e:
    print(f"Error importing agent modules: {str(e)}")
    print("\nDependency installation instructions:")
    print("1. Install required packages:")
    print("   pip install google-adk chromadb")
    print("2. Make sure you have the utils/chromadb_store.py file in your project")
    sys.exit(1)
except Exception as e:
    print(f"Error starting agent: {str(e)}")
    sys.exit(1) 