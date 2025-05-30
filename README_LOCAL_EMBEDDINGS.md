# Using Local Embeddings with MiniLM-L6-v2

This guide explains how to use the local MiniLM-L6-v2 model for embeddings with ChromaDB in the code analysis tool.

## Prerequisites

Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- `pip` - For local embedding generation
- `chromadb` - For vector storage and retrieval

## How It Works

The implementation uses the `sentence-transformers/all-MiniLM-L6-v2` model which:
- Is a lightweight model (80MB)
- Produces 384-dimensional embeddings
- Works well for semantic similarity of code reports
- Runs efficiently on CPU

The model will be downloaded automatically on first use and cached locally.

## Usage

### Basic Example

```python
from utils.local_embedding import LocalSentenceTransformerEmbedding
from utils.local_chromadb_store import LocalReportStore

# Initialize with custom directories
store = LocalReportStore(
    persist_directory="./my_chroma_db",  # Where ChromaDB stores data
    model_cache_dir="./my_model_cache"   # Where the model is cached
)

# Store an analysis report
store.store_analysis_report(
    component_name="MyComponent", 
    report_file_path="reports/my_component_analysis.md"
)

# Search for semantically similar reports
results = store.context_similarity_search(
    context_description="Python security vulnerabilities in web applications",
    n_results=3,
    min_score=0.7  # Only return results with at least 70% similarity
)

# Print results
for result in results:
    print(f"Component: {result['component_name']}")
    print(f"Similarity: {result['similarity_score']:.2f}")
    print(f"Relevant context: {result['relevant_context'][:200]}...")
    print()
```

### Command-Line Example

For a quick demonstration, run the example script:

```bash
python local_chromadb_example.py --query "Python security issues" --results 5
```

Available options:
- `--db-dir`: Directory to store ChromaDB data (default: ./local_chroma_db)
- `--model-cache`: Directory to cache the embedding model (default: ./model_cache)
- `--query`: Query text to search for (default: "security vulnerabilities in Python")
- `--collection`: Collection to search in (choices: analysis_reports, ocp_assessment_reports)
- `--results`: Number of results to return (default: 3)

## Integration with Report Generators

To use local embeddings with the existing report generators:

1. Import the LocalReportStore:
   ```python
   from utils.local_chromadb_store import LocalReportStore
   ```

2. Initialize it instead of the regular ReportStore:
   ```python
   # Instead of: store = ReportStore()
   store = LocalReportStore(
       persist_directory="./local_chroma_db",
       model_cache_dir="./model_cache"
   )
   ```

3. Use it exactly the same way as the regular ReportStore.

## Benefits of Local Embeddings

1. **Privacy**: All data stays on your machine
2. **Offline Usage**: Works without internet connection
3. **Cost Efficiency**: No API costs for embeddings
4. **Performance**: Low latency for embedding generation
5. **Customization**: Option to fine-tune on your specific data

## Changing Models

To use a different sentence-transformers model:

```python
store = LocalReportStore(
    model_cache_dir="./model_cache"
)
store.embedding_function = LocalSentenceTransformerEmbedding(
    model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",  # Smaller, faster model
    cache_dir="./model_cache"
)
```

Some alternative models to consider:
- `sentence-transformers/paraphrase-MiniLM-L3-v2` - Smaller (33MB), faster, 384d embeddings
- `sentence-transformers/all-mpnet-base-v2` - Larger (420MB), more accurate, 768d embeddings
- `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` - Optimized for question-answering, 384d 