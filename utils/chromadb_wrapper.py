"""
ChromaDB wrapper with configurable enable/disable functionality

This module provides a wrapper around ChromaDB storage that can be
conditionally enabled or disabled based on environment configuration.
"""

from typing import Optional, List, Dict, Any
from utils.config import get_config

class ChromaDBWrapper:
    """
    Wrapper for ChromaDB that can be conditionally enabled or disabled.
    
    When disabled, all operations return gracefully without doing anything.
    When enabled, delegates to the actual ChromaDB store implementation.
    """
    
    def __init__(self):
        """Initialize the wrapper with configuration settings."""
        self.config = get_config()
        self._store = None
        self._initialized = False
        
        print(f"ChromaDB Wrapper: {self.config.get_chromadb_enabled_message()}")
    
    def _ensure_initialized(self):
        """Ensure the ChromaDB store is initialized if enabled."""
        if self._initialized:
            return
            
        if self.config.use_chromadb:
            try:
                if self.config.use_local_embeddings:
                    print("Using local embedding models for ChromaDB")
                    from utils.local_chromadb_store import LocalReportStore
                    self._store = LocalReportStore(
                        persist_directory=self.config.chromadb_persist_dir,
                        model_cache_dir=self.config.local_model_cache_dir
                    )
                    # Override the model if specified in config
                    if self.config.local_model_name != "sentence-transformers/all-MiniLM-L6-v2":
                        from utils.local_embedding import LocalSentenceTransformerEmbedding
                        self._store.embedding_function = LocalSentenceTransformerEmbedding(
                            model_name=self.config.local_model_name,
                            cache_dir=self.config.local_model_cache_dir
                        )
                        # Update the collections with the new embedding function
                        self._store.analysis_collection = self._store.client.get_or_create_collection(
                            name=self.config.chromadb_analysis_collection,
                            embedding_function=self._store.embedding_function
                        )
                        self._store.ocp_collection = self._store.client.get_or_create_collection(
                            name=self.config.chromadb_ocp_collection,
                            embedding_function=self._store.embedding_function
                        )
                else:
                    print("Using API-based embeddings for ChromaDB")
                    from utils.chromadb_store import ReportStore
                    self._store = ReportStore(persist_directory=self.config.chromadb_persist_dir)
                
                print("ChromaDB store initialized successfully")
            except ImportError as e:
                print(f"Warning: ChromaDB or embedding dependencies not available: {str(e)}")
                if self.config.use_local_embeddings:
                    print("Hint: Install sentence-transformers for local embeddings: pip install sentence-transformers")
                print("ChromaDB storage will be disabled")
                self._store = None
            except Exception as e:
                print(f"Warning: Failed to initialize ChromaDB: {str(e)}")
                print("ChromaDB storage will be disabled")
                self._store = None
        else:
            print("ChromaDB storage disabled by configuration")
            self._store = None
            
        self._initialized = True
    
    def is_enabled(self) -> bool:
        """Check if ChromaDB storage is enabled and available."""
        self._ensure_initialized()
        return self._store is not None
    
    def store_analysis_report(self, component_name: str, report_file_path: str, report_content: str = None) -> bool:
        """
        Store an analysis report in ChromaDB.
        
        Args:
            component_name: Name of the component/project
            report_file_path: Path to the report file
            report_content: Optional report content (if None, will read from file)
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - skipping analysis report storage")
            return False
            
        try:
            self._store.store_analysis_report(component_name, report_file_path, report_content)
            return True
        except Exception as e:
            print(f"Warning: Failed to store analysis report in ChromaDB: {str(e)}")
            return False
    
    def store_ocp_assessment(self, component_name: str, report_file_path: str, report_content: str = None) -> bool:
        """
        Store an OCP assessment in ChromaDB.
        
        Args:
            component_name: Name of the component/project
            report_file_path: Path to the assessment file
            report_content: Optional assessment content (if None, will read from file)
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - skipping OCP assessment storage")
            return False
            
        try:
            self._store.store_ocp_assessment(component_name, report_file_path, report_content)
            return True
        except Exception as e:
            print(f"Warning: Failed to store OCP assessment in ChromaDB: {str(e)}")
            return False
    
    def query_reports(self, query_text: str, collection_name: str = "analysis_reports", n_results: int = 5) -> Dict[str, Any]:
        """
        Query reports based on similarity to the query text.
        
        Args:
            query_text: The text to search for
            collection_name: Which collection to query
            n_results: Number of results to return
            
        Returns:
            Query results or empty dict if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty search results")
            return {}
            
        try:
            return self._store.query_reports(query_text, collection_name, n_results)
        except Exception as e:
            print(f"Warning: Failed to query reports in ChromaDB: {str(e)}")
            return {}
    
    def search_analysis_reports(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search analysis reports in ChromaDB.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results, empty list if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty search results")
            return []
            
        try:
            results = self._store.query_reports(query, "analysis_reports", n_results)
            # Convert ChromaDB format to standardized format
            formatted_results = []
            if results and results.get('documents') and results['documents'][0]:
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    formatted_results.append({
                        'document': doc,
                        'metadata': metadata,
                        'rank': i + 1
                    })
            return formatted_results
        except Exception as e:
            print(f"Warning: Failed to search analysis reports in ChromaDB: {str(e)}")
            return []
    
    def search_ocp_assessments(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search OCP assessments in ChromaDB.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results, empty list if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty search results")
            return []
            
        try:
            results = self._store.query_reports(query, "ocp_assessment_reports", n_results)
            # Convert ChromaDB format to standardized format
            formatted_results = []
            if results and results.get('documents') and results['documents'][0]:
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    formatted_results.append({
                        'document': doc,
                        'metadata': metadata,
                        'rank': i + 1
                    })
            return formatted_results
        except Exception as e:
            print(f"Warning: Failed to search OCP assessments in ChromaDB: {str(e)}")
            return []
    
    def get_all_analysis_reports(self) -> List[Dict[str, Any]]:
        """
        Get all analysis reports from ChromaDB.
        
        Returns:
            List of all reports, empty list if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty results")
            return []
            
        try:
            results = self._store.analysis_collection.get()
            formatted_results = []
            if results and results.get('documents'):
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    formatted_results.append({
                        'document': doc,
                        'metadata': metadata,
                        'rank': i + 1
                    })
            return formatted_results
        except Exception as e:
            print(f"Warning: Failed to get analysis reports from ChromaDB: {str(e)}")
            return []
    
    def get_all_ocp_assessments(self) -> List[Dict[str, Any]]:
        """
        Get all OCP assessments from ChromaDB.
        
        Returns:
            List of all assessments, empty list if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty results")
            return []
            
        try:
            results = self._store.ocp_collection.get()
            formatted_results = []
            if results and results.get('documents'):
                for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                    formatted_results.append({
                        'document': doc,
                        'metadata': metadata,
                        'rank': i + 1
                    })
            return formatted_results
        except Exception as e:
            print(f"Warning: Failed to get OCP assessments from ChromaDB: {str(e)}")
            return []
    
    def get_report_by_component(self, component_name: str, collection_name: str = "analysis_reports") -> Dict[str, Any]:
        """
        Retrieve reports for a specific component.
        
        Args:
            component_name: Name of the component to retrieve reports for
            collection_name: Which collection to query
            
        Returns:
            Reports for the specified component, empty dict if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty results")
            return {}
            
        try:
            return self._store.get_report_by_component(component_name, collection_name)
        except Exception as e:
            print(f"Warning: Failed to get component report from ChromaDB: {str(e)}")
            return {}
    
    def list_components(self, collection_name: str = "analysis_reports") -> List[str]:
        """
        List all unique component names in the specified collection.
        
        Args:
            collection_name: Which collection to query
            
        Returns:
            List of unique component names, empty list if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty component list")
            return []
            
        try:
            return self._store.list_components(collection_name)
        except Exception as e:
            print(f"Warning: Failed to list components from ChromaDB: {str(e)}")
            return []
    
    def context_similarity_search(self, context_description: str, collection_name: str = "analysis_reports", 
                                n_results: int = 5, min_score: float = 0.0, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find reports that are semantically similar to a given context description.
        
        Args:
            context_description: A text description of the context to search for
            collection_name: Which collection to query
            n_results: Maximum number of similar reports to return
            min_score: Minimum similarity score to include in results
            filter_criteria: Optional dictionary of metadata criteria to filter results
            
        Returns:
            List of semantically similar reports, empty list if disabled
        """
        if not self.is_enabled():
            print("ChromaDB storage is disabled - returning empty search results")
            return []
            
        try:
            return self._store.context_similarity_search(context_description, collection_name, n_results, min_score, filter_criteria)
        except Exception as e:
            print(f"Warning: Failed to perform context similarity search in ChromaDB: {str(e)}")
            return []
    
    def __enter__(self):
        """Context manager entry."""
        self._ensure_initialized()
        if self._store:
            return self._store.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._store:
            return self._store.__exit__(exc_type, exc_val, exc_tb)

# Global wrapper instance
chromadb_wrapper = ChromaDBWrapper()

def get_chromadb_wrapper() -> ChromaDBWrapper:
    """Get the global ChromaDB wrapper instance."""
    return chromadb_wrapper 