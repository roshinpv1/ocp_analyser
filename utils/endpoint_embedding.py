"""
Endpoint-based embedding function for ChromaDB using HTTP API
"""

import requests
import json
from typing import List, Any
from chromadb.api.types import Documents, EmbeddingFunction

class EndpointEmbeddingFunction(EmbeddingFunction):
    """
    A custom embedding function that uses an HTTP endpoint for generating embeddings.
    """
    
    def __init__(self, endpoint_url: str = "http://localhost:1234", timeout: int = 30):
        """
        Initialize the embedding function with an endpoint URL.
        
        Args:
            endpoint_url: The URL of the embedding service endpoint
            timeout: Request timeout in seconds
        """
        self.endpoint_url = endpoint_url.rstrip('/')
        self.timeout = timeout
        
        # Test the endpoint during initialization
        try:
            self._test_endpoint()
            print(f"Endpoint embedding function initialized successfully: {self.endpoint_url}")
        except Exception as e:
            print(f"Warning: Could not connect to embedding endpoint {self.endpoint_url}: {str(e)}")
            print("Embeddings may fail until the service is available")
    
    def _test_endpoint(self):
        """Test if the endpoint is reachable and working."""
        test_response = requests.get(f"{self.endpoint_url}/health", timeout=5)
        if test_response.status_code != 200:
            # If health endpoint doesn't exist, try a simple embedding test
            test_embedding = self._generate_embedding("test")
            if test_embedding is None:
                raise Exception("Endpoint test failed")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text using the endpoint.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        try:
            # Try different common API formats for embedding endpoints
            
            # Format 1: Simple JSON POST with text field
            try:
                response = requests.post(
                    f"{self.endpoint_url}/embeddings",
                    json={"text": text},
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list):
                        return result
                    elif "embedding" in result:
                        return result["embedding"]
                    elif "data" in result and len(result["data"]) > 0:
                        return result["data"][0].get("embedding", result["data"][0])
            except:
                pass
            
            # Format 2: OpenAI-style API
            try:
                response = requests.post(
                    f"{self.endpoint_url}/v1/embeddings",
                    json={
                        "input": text,
                        "model": "text-embedding-ada-002"
                    },
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and len(result["data"]) > 0:
                        return result["data"][0]["embedding"]
            except:
                pass
            
            # Format 3: Simple GET with query parameter
            try:
                response = requests.get(
                    f"{self.endpoint_url}/embed",
                    params={"text": text},
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list):
                        return result
                    elif "embedding" in result:
                        return result["embedding"]
            except:
                pass
            
            # Format 4: Sentence-transformers style
            try:
                response = requests.post(
                    f"{self.endpoint_url}/encode",
                    json={"sentences": [text]},
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0]
                    elif "embeddings" in result and len(result["embeddings"]) > 0:
                        return result["embeddings"][0]
            except:
                pass
                
            print(f"Warning: Could not get embedding from endpoint {self.endpoint_url}")
            return None
            
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None
    
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
        
        embeddings = []
        
        # Try batch processing first
        try:
            # Format 1: Batch embeddings endpoint
            response = requests.post(
                f"{self.endpoint_url}/embeddings",
                json={"texts": texts},
                timeout=self.timeout * len(texts),  # Scale timeout with number of texts
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) == len(texts):
                    return result
                elif "embeddings" in result and len(result["embeddings"]) == len(texts):
                    return result["embeddings"]
        except:
            pass
        
        # Try OpenAI-style batch processing
        try:
            response = requests.post(
                f"{self.endpoint_url}/v1/embeddings",
                json={
                    "input": texts,
                    "model": "text-embedding-ada-002"
                },
                timeout=self.timeout * len(texts),
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                if "data" in result and len(result["data"]) == len(texts):
                    return [item["embedding"] for item in result["data"]]
        except:
            pass
        
        # Try sentence-transformers batch style
        try:
            response = requests.post(
                f"{self.endpoint_url}/encode",
                json={"sentences": texts},
                timeout=self.timeout * len(texts),
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) == len(texts):
                    return result
                elif "embeddings" in result and len(result["embeddings"]) == len(texts):
                    return result["embeddings"]
        except:
            pass
        
        # Fallback to individual requests
        print(f"Batch processing failed, falling back to individual requests for {len(texts)} texts")
        for text in texts:
            embedding = self._generate_embedding(text)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                # Use a zero vector as fallback
                print(f"Warning: Failed to get embedding for text, using zero vector")
                embeddings.append([0.0] * 384)  # Common embedding dimension
        
        return embeddings

# Example usage
if __name__ == "__main__":
    # Test the embedding function
    embedding_function = EndpointEmbeddingFunction("http://localhost:1234")
    texts = ["Hello, world!", "This is a test."]
    embeddings = embedding_function(texts)
    print(f"Generated {len(embeddings)} embeddings, each with dimension {len(embeddings[0])}") 