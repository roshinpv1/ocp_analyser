#!/bin/bash
# Local LLM Setup Script for hardgates integration

echo "Setting up local LLM environment variables..."

# Configure for your local LLM on port 1234
export OPENAI_BASE_URL="http://localhost:1234/v1"
export OPENAI_API_KEY="local-llm-key"

# Replace with your actual model name (e.g., "llama-2-7b-chat", "codellama", etc.)
export OPENAI_MODEL="your-model-name"

echo "✅ Environment variables set:"
echo "  OPENAI_BASE_URL: $OPENAI_BASE_URL"
echo "  OPENAI_API_KEY: $OPENAI_API_KEY"
echo "  OPENAI_MODEL: $OPENAI_MODEL"
echo ""
echo "To use these settings, run: source local_llm_setup.sh"
echo "Or set them manually in your shell." 