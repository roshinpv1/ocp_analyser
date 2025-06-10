# Endpoint Embeddings Integration

This document explains how to configure and use endpoint embeddings instead of local embedding models in the OCP Analyser.

## Overview

The OCP Analyser now supports three embedding options:

1. **Local Embeddings** - Uses sentence-transformers models locally
2. **API Embeddings** - Uses OpenAI's embedding API  
3. **Endpoint Embeddings** ⭐ - Uses your own embedding service endpoint

## Quick Setup

### 1. Run the Setup Script

```bash
python setup_endpoint_embeddings.py
```

This will:
- ✅ Configure the system to use endpoint embeddings
- ✅ Set the default endpoint to `http://localhost:1234`
- ✅ Test the endpoint connection
- ✅ Verify all dependencies are installed

### 2. Manual Configuration (Alternative)

Create a `.env` file with:

```bash
# Use endpoint embeddings
USE_CHROMADB=true
USE_LOCAL_EMBEDDINGS=false
USE_ENDPOINT_EMBEDDINGS=true
EMBEDDING_ENDPOINT_URL=http://localhost:1234
EMBEDDING_ENDPOINT_TIMEOUT=30
```

### 3. Test the Setup

```bash
python test_endpoint_embeddings.py
```

## Endpoint Requirements

Your embedding service on port 1234 should support one of these API formats:

### Format 1: Simple JSON (Recommended)
```bash
POST /embeddings
Content-Type: application/json

{
  "text": "text to embed"              # Single text
}
# OR
{
  "texts": ["text1", "text2", ...]    # Batch processing
}
```

Response:
```json
{
  "embedding": [0.1, 0.2, ...]        # Single embedding
}
# OR
{
  "embeddings": [[0.1, 0.2], ...]     # Batch embeddings
}
```

### Format 2: OpenAI-style API
```bash
POST /v1/embeddings
Content-Type: application/json

{
  "input": "text to embed",
  "model": "text-embedding-ada-002"
}
```

### Format 3: Sentence-transformers style
```bash
POST /encode
Content-Type: application/json

{
  "sentences": ["text1", "text2", ...]
}
```

### Format 4: Simple GET
```bash
GET /embed?text=your+text+here
```

## Benefits of Endpoint Embeddings

✅ **Performance** - Use optimized embedding services  
✅ **Scalability** - Handle large batch processing  
✅ **Flexibility** - Use any embedding model you want  
✅ **Control** - Full control over the embedding process  
✅ **No Dependencies** - No need to download large local models  

## Configuration Options

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `USE_ENDPOINT_EMBEDDINGS` | `false` | Enable endpoint embeddings |
| `EMBEDDING_ENDPOINT_URL` | `http://localhost:1234` | Endpoint URL |
| `EMBEDDING_ENDPOINT_TIMEOUT` | `30` | Request timeout (seconds) |

## Troubleshooting

### Connection Issues

**Problem**: `Cannot connect to embedding endpoint`

**Solutions**:
1. Make sure your embedding service is running on port 1234
2. Check if the endpoint URL is correct
3. Verify firewall settings allow connections to port 1234
4. Test the endpoint manually:
   ```bash
   curl -X POST http://localhost:1234/embeddings \
        -H "Content-Type: application/json" \
        -d '{"text": "test"}'
   ```

### Timeout Issues

**Problem**: Requests timing out

**Solutions**:
1. Increase the timeout value:
   ```bash
   EMBEDDING_ENDPOINT_TIMEOUT=60
   ```
2. Optimize your embedding service for faster response
3. Reduce batch sizes if using batch processing

### API Format Issues

**Problem**: `Warning: Could not get embedding from endpoint`

**Solutions**:
1. Check your API response format matches one of the supported formats
2. Verify your endpoint returns valid JSON
3. Check the response status code (should be 200)
4. Test with the debugging script:
   ```bash
   python test_endpoint_embeddings.py
   ```

## Example Embedding Service

Here's a simple Flask server example that works with the endpoint embedding function:

```python
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/embeddings', methods=['POST'])
def embeddings():
    data = request.json
    
    if 'text' in data:
        # Single text
        text = data['text']
        # Replace with your actual embedding logic
        embedding = np.random.rand(384).tolist()  # Mock embedding
        return jsonify({"embedding": embedding})
    
    elif 'texts' in data:
        # Batch texts
        texts = data['texts']
        # Replace with your actual embedding logic
        embeddings = [np.random.rand(384).tolist() for _ in texts]
        return jsonify({"embeddings": embeddings})
    
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)
```

## Migration from Local Embeddings

If you're switching from local embeddings:

1. **Backup your ChromaDB data** (optional):
   ```bash
   cp -r ./chroma_db ./chroma_db_backup
   ```

2. **Run the setup script**:
   ```bash
   python setup_endpoint_embeddings.py
   ```

3. **Test the new setup**:
   ```bash
   python test_endpoint_embeddings.py
   ```

4. **Run your analysis as usual**:
   ```bash
   python main.py --dir /path/to/code --output results
   ```

The system will automatically use endpoint embeddings instead of local models.

## Performance Tips

1. **Batch Processing**: The endpoint embedding function supports batch processing for better performance
2. **Connection Pooling**: Use connection pooling in your embedding service
3. **Caching**: Consider caching embeddings for frequently used texts
4. **Async Processing**: Use async endpoints for better concurrency

## Integration Status

✅ **ChromaDB Integration** - Full support for endpoint embeddings  
✅ **Report Storage** - All report types supported  
✅ **Query/Search** - Similarity search working  
✅ **Error Handling** - Graceful fallbacks and error messages  
✅ **Configuration** - Environment variable configuration  
✅ **Testing** - Comprehensive test suite  

## Support

If you encounter any issues:

1. Run the test script: `python test_endpoint_embeddings.py`
2. Check the configuration: `python -c "from utils.config import get_config; print(get_config())"`
3. Verify your embedding service is working correctly
4. Check the logs for detailed error messages

The endpoint embedding integration maintains full compatibility with all existing OCP Analyser features while providing the flexibility to use your own embedding services. 