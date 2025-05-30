import os
import chromadb
from chromadb.utils import embedding_functions
import uuid

class ReportStore:
    """
    A utility class for storing and retrieving analysis reports in ChromaDB.
    """
    
    def __init__(self, persist_directory="./chroma_db"):
        """
        Initialize the ChromaDB client and collections.
        
        Args:
            persist_directory: Directory where ChromaDB will store its data
        """
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.persist_directory = persist_directory
        
        # Get or create collections for each report type
        self.analysis_collection = self.client.get_or_create_collection(
            name="analysis_reports",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )
        
        self.ocp_collection = self.client.get_or_create_collection(
            name="ocp_assessment_reports",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
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
    
    def find_similar_reports(self, report_id=None, report_content=None, collection_name="analysis_reports", n_results=5):
        """
        Find reports that are semantically similar to a given report.
        
        Args:
            report_id: ID of an existing report to use as the basis for similarity
            report_content: Text content to use as the basis for similarity (if report_id not provided)
            collection_name: Which collection to query ("analysis_reports" or "ocp_assessment_reports")
            n_results: Maximum number of similar reports to return
            
        Returns:
            results: List of similar reports with similarity scores
        """
        if not report_id and not report_content:
            raise ValueError("Either report_id or report_content must be provided")
            
        collection = self.analysis_collection if collection_name == "analysis_reports" else self.ocp_collection
        
        # If report_id is provided, get the document content
        if report_id:
            try:
                report_data = collection.get(ids=[report_id])
                if not report_data or not report_data["documents"]:
                    raise ValueError(f"Report with ID {report_id} not found")
                report_content = report_data["documents"][0]
            except Exception as e:
                print(f"Error retrieving report with ID {report_id}: {str(e)}")
                raise
        
        # Use the content to find similar reports
        results = collection.query(
            query_texts=[report_content],
            n_results=n_results
        )
        
        # Format the results to include similarity scores
        similar_reports = []
        if results and results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0], 
                results["metadatas"][0],
                results["distances"][0] if "distances" in results else [0] * len(results["documents"][0])
            )):
                # Convert distance to similarity score (1.0 is identical, 0.0 is completely different)
                # ChromaDB returns cosine distance, so we convert to similarity
                similarity = 1.0 - distance if distance <= 1.0 else 0.0
                
                similar_reports.append({
                    "rank": i + 1,
                    "component_name": metadata.get("component_name", "Unknown"),
                    "file_path": metadata.get("file_path", "Unknown"),
                    "similarity_score": similarity,
                    "snippet": doc[:200] + "..." if len(doc) > 200 else doc,
                    "document": doc
                })
        
        return similar_reports
    
    def context_similarity_search(self, context_description, collection_name="analysis_reports", n_results=5, min_score=0.0, 
                                 filter_criteria=None):
        """
        Find reports that are semantically similar to a given context description.
        
        Args:
            context_description: A text description of the context to search for
            collection_name: Which collection to query ("analysis_reports" or "ocp_assessment_reports")
            n_results: Maximum number of similar reports to return
            min_score: Minimum similarity score (0.0 to 1.0) to include in results
            filter_criteria: Optional dictionary of metadata criteria to filter results
                Example: {"component_name": "MyComponent"}
            
        Returns:
            results: List of semantically similar reports with similarity scores
        """
        collection = self.analysis_collection if collection_name == "analysis_reports" else self.ocp_collection
        
        # Set up the where clause if filter criteria provided
        where = filter_criteria if filter_criteria else None
        
        # Query the collection
        results = collection.query(
            query_texts=[context_description],
            n_results=n_results,
            where=where
        )
        
        # Format the results to include similarity scores
        similar_reports = []
        if results and results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0], 
                results["metadatas"][0],
                results["distances"][0] if "distances" in results else [0] * len(results["documents"][0])
            )):
                # Convert distance to similarity score (1.0 is identical, 0.0 is completely different)
                # ChromaDB returns cosine distance, so we convert to similarity
                similarity = 1.0 - distance if distance <= 1.0 else 0.0
                
                # Skip if below minimum score
                if similarity < min_score:
                    continue
                
                # Get the most relevant section from the document
                # This finds the best matching paragraph for the context
                paragraphs = [p for p in doc.split('\n\n') if p.strip()]
                best_paragraph = ""
                if paragraphs:
                    # If document has paragraphs, find the most similar one to the context
                    best_match_score = -1
                    for paragraph in paragraphs:
                        # Simple similarity heuristic - count matching words
                        # This is a simplified approach; you could use the embedding function for better results
                        context_words = set(context_description.lower().split())
                        paragraph_words = set(paragraph.lower().split())
                        match_score = len(context_words.intersection(paragraph_words)) / max(1, len(context_words))
                        
                        if match_score > best_match_score:
                            best_match_score = match_score
                            best_paragraph = paragraph
                
                # If no good paragraph match, use the beginning of the document
                if not best_paragraph and doc:
                    best_paragraph = doc[:300] + "..." if len(doc) > 300 else doc
                
                similar_reports.append({
                    "rank": i + 1,
                    "component_name": metadata.get("component_name", "Unknown"),
                    "file_path": metadata.get("file_path", "Unknown"),
                    "similarity_score": similarity,
                    "relevant_context": best_paragraph,
                    "document": doc
                })
        
        # Sort by similarity score (highest first)
        similar_reports.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return similar_reports


# Example usage
if __name__ == "__main__":
    # Use context manager to properly handle cleanup
    with ReportStore() as store:
        # Store a sample report
        store.store_analysis_report(
            "Test Component",
            "test_report.md",
            "This is a test analysis report content."
        )
        
        # Query for reports
        results = store.query_reports("analysis report")
        print(f"Query results: {results}") 