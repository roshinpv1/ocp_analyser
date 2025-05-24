"""
Local embedding function for ChromaDB using sentence-transformers
"""

import os
from typing import List, Any
from chromadb.api.types import Documents, EmbeddingFunction

class LocalSentenceTransformerEmbedding(EmbeddingFunction):
    """
    A custom embedding function that uses a local sentence-transformer model.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", cache_dir: str = None):
        """
        Initialize the embedding function with a local model.
        
        Args:
            model_name: The name of the sentence-transformer model to use
            cache_dir: Directory to store the downloaded model (if not already downloaded)
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "The sentence_transformers python package is not installed. "
                "Please install it with `pip install sentence-transformers`"
            )
        
        # Set the cache directory if provided
        if cache_dir:
            os.environ["SENTENCE_TRANSFORMERS_HOME"] = cache_dir
            os.makedirs(cache_dir, exist_ok=True)
            
        # Load the model
        print(f"Loading sentence-transformer model: {model_name}")
        self._model = SentenceTransformer(model_name)
        print(f"Model loaded successfully with embedding dimension: {self._model.get_sentence_embedding_dimension()}")
        
    def __call__(self, texts: Documents) -> List[List[float]]:
        """
        Generate embeddings for the given texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings
        """
        # Convert any non-string inputs to strings
        texts = [str(text) for text in texts]
        
        # Generate embeddings
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        
        # Convert numpy arrays to lists
        return embeddings.tolist()

# Example usage
if __name__ == "__main__":
    # Test the embedding function
    embedding_function = LocalSentenceTransformerEmbedding()
    texts = ["Hello, world!", "This is a test."]
    embeddings = embedding_function(texts)
    print(f"Generated {len(embeddings)} embeddings, each with dimension {len(embeddings[0])}") 