# OCP Analyser Configuration Guide

The OCP Analyser supports configurable settings through environment variables. This allows you to customize the behavior of the application, including enabling/disabling ChromaDB storage.

## Configuration Setup

### 1. Environment File Setup

1. Copy the example configuration file:
   ```bash
   cp config.env.example .env
   ```

2. Edit the `.env` file with your settings:
   ```bash
   nano .env
   ```

### 2. Available Configuration Options

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| `USE_CHROMADB` | `true` | Enable/disable ChromaDB storage (`true`/`false`) |
| `CHROMADB_PERSIST_DIR` | `./chroma_db` | Directory where ChromaDB stores data |
| `CHROMADB_ANALYSIS_COLLECTION` | `analysis_reports` | Collection name for analysis reports |
| `CHROMADB_OCP_COLLECTION` | `ocp_assessments` | Collection name for OCP assessments |
| `OPENAI_API_KEY` | *None* | Your OpenAI API key |
| `DEFAULT_OUTPUT_DIR` | `./out` | Default output directory for reports |
| `DEFAULT_PROJECT_NAME` | `Unknown Project` | Default project name |

## ChromaDB Configuration

### Enabling ChromaDB Storage

To enable ChromaDB storage (default):
```env
USE_CHROMADB=true
CHROMADB_PERSIST_DIR=./chroma_db
```

When enabled, the system will:
- Store analysis reports and OCP assessments in ChromaDB
- Enable vector search capabilities
- Allow querying reports using the CLI tools

### Disabling ChromaDB Storage

To disable ChromaDB storage:
```env
USE_CHROMADB=false
```

When disabled, the system will:
- Skip ChromaDB storage operations gracefully
- Still generate HTML and Markdown reports
- Print informational messages about disabled storage
- Continue functioning normally without vector storage

## Usage Examples

### Basic Configuration (ChromaDB Enabled)
```env
# .env file
USE_CHROMADB=true
CHROMADB_PERSIST_DIR=./my_reports_db
OPENAI_API_KEY=sk-your-key-here
DEFAULT_OUTPUT_DIR=./reports
```

### Minimal Configuration (ChromaDB Disabled)
```env
# .env file
USE_CHROMADB=false
OPENAI_API_KEY=sk-your-key-here
DEFAULT_OUTPUT_DIR=./reports
```

### Custom ChromaDB Setup
```env
# .env file
USE_CHROMADB=true
CHROMADB_PERSIST_DIR=/path/to/shared/storage
CHROMADB_ANALYSIS_COLLECTION=my_analysis_reports
CHROMADB_OCP_COLLECTION=my_ocp_assessments
```

## Environment Variable Sources

The configuration system checks for environment variables in this order:

1. **Environment variables** set in your shell
2. **`.env` file** in the project root directory
3. **Default values** built into the application

Example of setting via shell:
```bash
export USE_CHROMADB=false
python main.py
```

## Configuration Validation

The system will:
- Automatically validate boolean values for `USE_CHROMADB`
- Accept various boolean formats: `true`/`false`, `1`/`0`, `yes`/`no`, `on`/`off`
- Display configuration status at startup
- Gracefully handle missing ChromaDB dependencies when disabled

## Troubleshooting

### ChromaDB Issues
If you encounter ChromaDB-related errors:

1. **Disable ChromaDB temporarily**:
   ```env
   USE_CHROMADB=false
   ```

2. **Check ChromaDB installation**:
   ```bash
   pip install chromadb>=0.4.18
   ```

3. **Verify storage directory permissions**:
   ```bash
   mkdir -p ./chroma_db
   chmod 755 ./chroma_db
   ```

### Configuration Not Loading
If your configuration isn't being applied:

1. **Check file name**: Ensure the file is named `.env` (not `env.txt` or similar)
2. **Check file location**: The `.env` file should be in the project root directory
3. **Check syntax**: Ensure no spaces around the `=` sign and no quotes around values

### Viewing Current Configuration
To see your current configuration, the system prints status messages at startup:
```
Loaded configuration from .env
ChromaDB Wrapper: ChromaDB storage enabled (directory: ./chroma_db)
ChromaDB store initialized successfully
```

Or if disabled:
```
ChromaDB Wrapper: ChromaDB storage disabled
ChromaDB storage disabled by configuration
```

## Security Notes

- **Never commit your `.env` file** to version control
- **Keep your API keys secure** and rotate them regularly
- **Use environment variables** for production deployments
- **Restrict file permissions** on your `.env` file: `chmod 600 .env`

## Integration with Existing Tools

All existing tools respect the configuration:

- **Main analysis**: `python main.py` (uses configured settings)
- **Query CLI**: `python query_reports.py` (works with/without ChromaDB)
- **Agent interface**: `python run_agent.py` (adapts to storage availability)
- **Batch processing**: All batch scripts respect configuration

## Production Deployment

For production deployments, consider:

1. **Use environment variables** instead of `.env` files
2. **Use external ChromaDB server** for scalability
3. **Set up proper backup** for ChromaDB data directory
4. **Monitor storage usage** and implement cleanup policies
5. **Use separate collections** for different environments (dev/staging/prod) 