"""
ChromaDB store using local embedding models
"""

import os
import chromadb
import uuid
from utils.local_embedding import LocalSentenceTransformerEmbedding

class LocalReportStore:
    """
    A utility class for storing and retrieving analysis reports in ChromaDB using local embedding models.
    """
    
    def __init__(self, persist_directory="./local_chroma_db", model_cache_dir="./model_cache"):
        """
        Initialize the ChromaDB client and collections with local embedding model.
        
        Args:
            persist_directory: Directory where ChromaDB will store its data
            model_cache_dir: Directory to cache the embedding model
        """
        # Create directories if they don't exist
        os.makedirs(persist_directory, exist_ok=True)
        os.makedirs(model_cache_dir, exist_ok=True)
        
        # Initialize the local embedding function
        self.embedding_function = LocalSentenceTransformerEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_dir=model_cache_dir
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collections for each report type
        self.analysis_collection = self.client.get_or_create_collection(
            name="analysis_reports",
            embedding_function=self.embedding_function
        )
        
        self.ocp_collection = self.client.get_or_create_collection(
            name="ocp_assessment_reports",
            embedding_function=self.embedding_function
        )
    
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
    # Initialize the store
    store = LocalReportStore()
    
    # Test the embedding function
    results = store.context_similarity_search(
        context_description="Python application security vulnerabilities",
        n_results=2
    )
    
    print(f"Found {len(results)} matching reports") 