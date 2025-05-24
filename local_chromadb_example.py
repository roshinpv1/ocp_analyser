#!/usr/bin/env python3
"""
Example script demonstrating how to use the local embedding model with ChromaDB
"""

import argparse
import os
from utils.local_chromadb_store import LocalReportStore

def store_sample_reports(store, sample_dir="sample_reports"):
    """Store some sample reports for demonstration"""
    os.makedirs(sample_dir, exist_ok=True)
    
    # Create a sample analysis report
    analysis_content = """
    # Component Analysis Report: Sample Application
    
    ## Overview
    This is a sample Python application with several modules.
    
    ## Security Analysis
    - Found 3 potential security vulnerabilities
    - SQL injection risk in database module
    - Outdated dependency with CVE-2023-12345
    
    ## Performance Analysis
    The application performs well under normal load but may experience
    slowdowns with concurrent users exceeding 500.
    """
    
    analysis_file = os.path.join(sample_dir, "sample_analysis.md")
    with open(analysis_file, "w") as f:
        f.write(analysis_content)
    
    # Create a sample OCP assessment
    ocp_content = """
    # OpenShift Migration Assessment: Sample Application
    
    ## Containerization Assessment
    This application can be containerized with minimal changes.
    
    ## OpenShift Compatibility
    - Compatible with OpenShift 4.x
    - Requires persistent volume for data storage
    - Environment variables need to be configured
    
    ## Recommendations
    1. Create a Dockerfile with Python 3.9 base
    2. Configure persistent volume claims
    3. Set up CI/CD pipeline with Jenkins
    """
    
    ocp_file = os.path.join(sample_dir, "sample_ocp.md")
    with open(ocp_file, "w") as f:
        f.write(ocp_content)
    
    # Store the reports
    store.store_analysis_report("SampleApp", analysis_file, analysis_content)
    store.store_ocp_assessment("SampleApp", ocp_file, ocp_content)
    
    print(f"Stored sample reports in {sample_dir}")
    return [analysis_file, ocp_file]

def main():
    parser = argparse.ArgumentParser(description='ChromaDB with Local Embedding Example')
    parser.add_argument('--db-dir', default='./local_chroma_db',
                        help='Directory to store ChromaDB data')
    parser.add_argument('--model-cache', default='./model_cache',
                        help='Directory to cache the embedding model')
    parser.add_argument('--query', default='security vulnerabilities in Python',
                        help='Query text to search for')
    parser.add_argument('--collection', default='analysis_reports',
                        choices=['analysis_reports', 'ocp_assessment_reports'],
                        help='Collection to search in')
    parser.add_argument('--results', type=int, default=3,
                        help='Number of results to return')
    
    args = parser.parse_args()
    
    print("Initializing local ChromaDB with sentence-transformers/all-MiniLM-L6-v2...")
    store = LocalReportStore(
        persist_directory=args.db_dir,
        model_cache_dir=args.model_cache
    )
    
    # Store sample reports if the DB is empty
    components = store.list_components(args.collection)
    if not components:
        print("No reports found in the database. Adding sample reports...")
        store_sample_reports(store)
    else:
        print(f"Found existing reports for components: {components}")
    
    # Perform a semantic search
    print(f"\nPerforming semantic search for: '{args.query}'")
    print(f"Using collection: {args.collection}")
    print(f"Max results: {args.results}")
    
    results = store.context_similarity_search(
        context_description=args.query,
        collection_name=args.collection,
        n_results=args.results,
        min_score=0.1
    )
    
    print(f"\nFound {len(results)} similar reports:")
    for i, result in enumerate(results):
        print(f"\n{i+1}. Component: {result['component_name']}")
        print(f"   Similarity Score: {result['similarity_score']:.4f}")
        print(f"   File: {result['file_path']}")
        print(f"   Relevant Section: {result['relevant_context'][:150]}...")

if __name__ == "__main__":
    main() 