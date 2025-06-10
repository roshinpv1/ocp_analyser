"""
Configuration utility for OCP Analyser

Handles environment variables and application settings.
"""
import os
from typing import Optional

class Config:
    """Configuration class that handles environment variables and defaults."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        self._load_env_file()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        env_file = '.env'
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ.setdefault(key.strip(), value.strip())
                print(f"Loaded configuration from {env_file}")
            except Exception as e:
                print(f"Warning: Could not load .env file: {str(e)}")
    
    @property
    def use_chromadb(self) -> bool:
        """Whether to use ChromaDB storage."""
        value = os.getenv('USE_CHROMADB', 'true').lower()
        return value in ('true', '1', 'yes', 'on')
    
    @property
    def use_local_embeddings(self) -> bool:
        """Whether to use local embedding models."""
        value = os.getenv('USE_LOCAL_EMBEDDINGS', 'false').lower()
        return value in ('true', '1', 'yes', 'on')
    
    @property
    def use_endpoint_embeddings(self) -> bool:
        """Whether to use endpoint-based embedding models."""
        value = os.getenv('USE_ENDPOINT_EMBEDDINGS', 'false').lower()
        return value in ('true', '1', 'yes', 'on')
    
    @property
    def local_model_name(self) -> str:
        """Local embedding model name."""
        return os.getenv('LOCAL_MODEL_NAME', 'sentence-transformers/all-MiniLM-L6-v2')
    
    @property
    def local_model_cache_dir(self) -> str:
        """Local model cache directory."""
        return os.getenv('LOCAL_MODEL_CACHE_DIR', './model_cache')
    
    @property
    def chromadb_persist_dir(self) -> str:
        """ChromaDB persistence directory."""
        return os.getenv('CHROMADB_PERSIST_DIR', './chroma_db')
    
    @property
    def chromadb_analysis_collection(self) -> str:
        """ChromaDB analysis reports collection name."""
        return os.getenv('CHROMADB_ANALYSIS_COLLECTION', 'analysis_reports')
    
    @property
    def chromadb_ocp_collection(self) -> str:
        """ChromaDB OCP assessments collection name."""
        return os.getenv('CHROMADB_OCP_COLLECTION', 'ocp_assessments')
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """OpenAI API key."""
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def default_output_dir(self) -> str:
        """Default output directory for reports."""
        return os.getenv('DEFAULT_OUTPUT_DIR', './out')
    
    @property
    def default_project_name(self) -> str:
        """Default project name."""
        return os.getenv('DEFAULT_PROJECT_NAME', 'Unknown Project')
    
    @property
    def embedding_endpoint_url(self) -> str:
        """Embedding endpoint URL."""
        return os.getenv('EMBEDDING_ENDPOINT_URL', 'http://localhost:1234')
    
    @property
    def embedding_endpoint_timeout(self) -> int:
        """Embedding endpoint timeout in seconds."""
        try:
            return int(os.getenv('EMBEDDING_ENDPOINT_TIMEOUT', '30'))
        except ValueError:
            return 30
    
    def get_chromadb_enabled_message(self) -> str:
        """Get a message indicating ChromaDB status."""
        if self.use_chromadb:
            if self.use_local_embeddings:
                embedding_type = "local embeddings"
            elif self.use_endpoint_embeddings:
                embedding_type = f"endpoint embeddings ({self.embedding_endpoint_url})"
            else:
                embedding_type = "API embeddings"
            return f"ChromaDB storage enabled with {embedding_type} (directory: {self.chromadb_persist_dir})"
        else:
            return "ChromaDB storage disabled"
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"""OCP Analyser Configuration:
  ChromaDB Enabled: {self.use_chromadb}
  Local Embeddings: {self.use_local_embeddings}
  Endpoint Embeddings: {self.use_endpoint_embeddings}
  Embedding Endpoint URL: {self.embedding_endpoint_url}
  Embedding Endpoint Timeout: {self.embedding_endpoint_timeout}s
  ChromaDB Directory: {self.chromadb_persist_dir}
  Local Model: {self.local_model_name}
  Model Cache Dir: {self.local_model_cache_dir}
  Analysis Collection: {self.chromadb_analysis_collection}
  OCP Collection: {self.chromadb_ocp_collection}
  Default Output: {self.default_output_dir}
  Default Project: {self.default_project_name}"""

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance."""
    return config 

# Enhanced configuration for local embeddings
