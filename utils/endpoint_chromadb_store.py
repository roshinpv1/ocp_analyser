"""
ChromaDB store implementation using endpoint-based embeddings
"""

import os
import chromadb
import uuid
from utils.endpoint_embedding import EndpointEmbeddingFunction

class EndpointReportStore:
    """
    A utility class for storing and retrieving analysis reports in ChromaDB using endpoint embeddings.
    """
    
    def __init__(self, persist_directory="./chroma_db", endpoint_url="http://localhost:1234", timeout=30):
        """
        Initialize the ChromaDB client and collections with endpoint embeddings.
        
        Args:
            persist_directory: Directory where ChromaDB will store its data
            endpoint_url: URL of the embedding endpoint
            timeout: Timeout for embedding requests in seconds
        """
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.persist_directory = persist_directory
        
        # Initialize endpoint embedding function
        self.embedding_function = EndpointEmbeddingFunction(
            endpoint_url=endpoint_url,
            timeout=timeout
        )
        
        # Get or create collections for each report type
        self.analysis_collection = self.client.get_or_create_collection(
            name="analysis_reports",
            embedding_function=self.embedding_function
        )
        
        self.ocp_collection = self.client.get_or_create_collection(
            name="ocp_assessment_reports",
            embedding_function=self.embedding_function
        )
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.close()
    
    def close(self):
        """Properly close ChromaDB client to prevent context leaks"""
        try:
            if hasattr(self, 'client') and self.client:
                # Reset the client
                self.client.reset()
                self.client = None
                self.analysis_collection = None
                self.ocp_collection = None
                self.embedding_function = None
        except Exception as e:
            # Suppress cleanup errors but log them
            print(f"Warning: Error during ChromaDB cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.close()
    
    def store_analysis_report(self, component_name, report_file_path, report_content=None):
        """
        Store an analysis report in ChromaDB.
        
        Args:
            component_name: Name of the component being analyzed
            report_file_path: Path to the report file
            report_content: Optional content of the report (if None, will read from file_path)
        
        Returns:
            report_id: The ID of the stored report
        """
        # If content not provided, read from file
        if report_content is None:
            try:
                with open(report_file_path, 'r', encoding='utf-8') as file:
                    report_content = file.read()
            except Exception as e:
                print(f"Error reading report file {report_file_path}: {str(e)}")
                return None
        
        # Create a unique ID for this report
        report_id = str(uuid.uuid4())
        
        # Store in ChromaDB
        self.analysis_collection.add(
            documents=[report_content],
            metadatas=[{
                "component_name": component_name,
                "file_path": report_file_path,
                "report_type": "analysis"
            }],
            ids=[report_id]
        )
        
        print(f"Stored analysis report for component '{component_name}' with ID: {report_id}")
        return report_id
    
    def store_ocp_assessment(self, component_name, report_file_path, report_content=None):
        """
        Store an OpenShift assessment report in ChromaDB.
        
        Args:
            component_name: Name of the component being assessed
            report_file_path: Path to the report file
            report_content: Optional content of the report (if None, will read from file_path)
        
        Returns:
            report_id: The ID of the stored report
        """
        # If content not provided, read from file
        if report_content is None:
            try:
                with open(report_file_path, 'r', encoding='utf-8') as file:
                    report_content = file.read()
            except Exception as e:
                print(f"Error reading report file {report_file_path}: {str(e)}")
                return None
        
        # Create a unique ID for this report
        report_id = str(uuid.uuid4())
        
        # Store in ChromaDB
        self.ocp_collection.add(
            documents=[report_content],
            metadatas=[{
                "component_name": component_name,
                "file_path": report_file_path,
                "report_type": "ocp_assessment"
            }],
            ids=[report_id]
        )
        
        print(f"Stored OCP assessment for component '{component_name}' with ID: {report_id}")
        return report_id
    
    def query_reports(self, query_text, collection_name="analysis_reports", n_results=5):
        """
        Query reports based on similarity to the query text.
        
        Args:
            query_text: The text to search for
            collection_name: Which collection to query ("analysis_reports" or "ocp_assessment_reports")
            n_results: Maximum number of results to return
            
        Returns:
            results: List of matching reports with their metadata
        """
        collection = self.analysis_collection if collection_name == "analysis_reports" else self.ocp_collection
        
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        return results
    
    def get_report_by_component(self, component_name, collection_name="analysis_reports"):
        """
        Retrieve reports for a specific component.
        
        Args:
            component_name: Name of the component to retrieve reports for
            collection_name: Which collection to query ("analysis_reports" or "ocp_assessment_reports")
            
        Returns:
            results: Reports for the specified component
        """
        collection = self.analysis_collection if collection_name == "analysis_reports" else self.ocp_collection
        
        results = collection.get(
            where={"component_name": component_name}
        )
        
        return results
    
    def list_components(self, collection_name="analysis_reports"):
        """
        List all unique component names in the specified collection.
        
        Args:
            collection_name: Which collection to query ("analysis_reports" or "ocp_assessment_reports")
            
        Returns:
            components: List of unique component names
        """
        collection = self.analysis_collection if collection_name == "analysis_reports" else self.ocp_collection
        
        # Get all items in the collection
        all_items = collection.get()
        
        # Extract unique component names
        components = set()
        if all_items and 'metadatas' in all_items and all_items['metadatas']:
            for metadata in all_items['metadatas']:
                if 'component_name' in metadata:
                    components.add(metadata['component_name'])
        
        return list(components)
    
    def context_similarity_search(self, context_description, collection_name="analysis_reports", n_results=5, min_score=0.0, 
                                 filter_criteria=None):
        """
        Perform similarity search based on context description.
        
        Args:
            context_description: Description of the context to search for
            collection_name: Which collection to search ("analysis_reports" or "ocp_assessment_reports")
            n_results: Maximum number of results to return
            min_score: Minimum similarity score to include in results
            filter_criteria: Additional metadata filters
            
        Returns:
            results: List of matching reports with scores
        """
        collection = self.analysis_collection if collection_name == "analysis_reports" else self.ocp_collection
        
        # Build where clause
        where_clause = {}
        if filter_criteria:
            where_clause.update(filter_criteria)
        
        results = collection.query(
            query_texts=[context_description],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Filter by minimum score if specified
        if min_score > 0.0 and results and 'distances' in results:
            filtered_results = {
                'ids': [],
                'distances': [],
                'metadatas': [],
                'documents': []
            }
            
            for i, distance in enumerate(results['distances'][0]):
                # Convert distance to similarity score (lower distance = higher similarity)
                similarity = 1.0 - distance
                if similarity >= min_score:
                    filtered_results['ids'].append(results['ids'][0][i])
                    filtered_results['distances'].append(distance)
                    filtered_results['metadatas'].append(results['metadatas'][0][i])
                    filtered_results['documents'].append(results['documents'][0][i])
            
            # Wrap in the expected structure
            results = {
                'ids': [filtered_results['ids']],
                'distances': [filtered_results['distances']],
                'metadatas': [filtered_results['metadatas']],
                'documents': [filtered_results['documents']]
            }
        
        return results 