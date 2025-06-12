# Local LLM Integration Guide

## Setup for Local LLM (Port 1234)

Your local LLM running on port 1234 with OpenAI compatibility can now be integrated with the hardgates tool.

### 1. Environment Configuration

Set these environment variables to use your local LLM:

```bash
# Required: Set base URL to your local LLM endpoint
export OPENAI_BASE_URL="http://localhost:1234/v1"

# Required: API key (can be any value for most local LLMs)
export OPENAI_API_KEY="local-llm-key"

# Optional: Specify the model name your local LLM uses
export OPENAI_MODEL="llama-2-7b-chat"  # Replace with your model name
```

### 2. Common Local LLM Setups

**LM Studio:**
```bash
export OPENAI_BASE_URL="http://localhost:1234/v1"
export OPENAI_API_KEY="lm-studio"
export OPENAI_MODEL="llama-2-7b-chat"  # Or whatever model you're running
```

**Ollama with OpenAI compatibility:**
```bash
export OPENAI_BASE_URL="http://localhost:11434/v1"  # Default Ollama port
export OPENAI_API_KEY="ollama"
export OPENAI_MODEL="llama2"  # Or your Ollama model
```

**LocalAI:**
```bash
export OPENAI_BASE_URL="http://localhost:8080/v1"  # Default LocalAI port
export OPENAI_API_KEY="localai"
export OPENAI_MODEL="gpt-3.5-turbo"  # LocalAI model alias
```

### 3. Testing Your Setup

Test the connection with:
```bash
cd hardgates
python3 test_local_llm.py
```

### 4. Running Hard Gates Assessment

Once configured, run the assessment normally:
```bash
python3 main.py --repo https://github.com/user/repo --verbose
```

The tool will automatically detect and use your local LLM based on the environment variables.

### 5. Troubleshooting

**Common Issues:**

1. **Connection refused**: Make sure your local LLM is running on the specified port
2. **Model not found**: Verify the model name matches what's loaded in your local LLM
3. **API format**: Ensure your local LLM supports OpenAI-compatible chat completions

**Debug steps:**
- Check if your LLM is accessible: `curl http://localhost:1234/v1/models`
- Verify the endpoint format matches OpenAI's API
- Use `--verbose` flag when running assessments to see detailed output 