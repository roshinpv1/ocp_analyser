#!/usr/bin/env python3
"""
Query Reports CLI - A utility for searching and retrieving reports from ChromaDB
"""

import os
import sys
import argparse
from utils.chromadb_store import ReportStore

def list_components(store, report_type):
    """List all components with stored reports."""
    collection_name = "analysis_reports" if report_type == "analysis" else "ocp_assessment_reports"
    components = store.list_components(collection_name)
    
    if not components:
        print(f"No {report_type} reports found in the database.")
        return
    
    print(f"\nComponents with {report_type} reports:")
    for i, component in enumerate(sorted(components), 1):
        print(f"{i}. {component}")

def search_reports(store, query, report_type, limit=5):
    """Search for reports matching the query."""
    collection_name = "analysis_reports" if report_type == "analysis" else "ocp_assessment_reports"
    results = store.query_reports(query, collection_name, limit)
    
    if not results or not results['documents'][0]:
        print(f"No matching {report_type} reports found for query: '{query}'")
        return
    
    print(f"\nSearch results for query: '{query}'")
    print(f"Found {len(results['documents'][0])} matches\n")
    
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        component = metadata.get('component_name', 'Unknown')
        file_path = metadata.get('file_path', 'Unknown')
        
        print(f"Result {i}:")
        print(f"Component: {component}")
        print(f"File: {file_path}")
        
        # Show a snippet of the document (first 200 chars)
        snippet = doc[:200] + "..." if len(doc) > 200 else doc
        print(f"Snippet: {snippet}")
        print("-" * 80)

def get_component_report(store, component_name, report_type):
    """Get reports for a specific component."""
    collection_name = "analysis_reports" if report_type == "analysis" else "ocp_assessment_reports"
    results = store.get_report_by_component(component_name, collection_name)
    
    if not results or not results['documents']:
        print(f"No {report_type} reports found for component: '{component_name}'")
        return
    
    print(f"\nReports for component: '{component_name}'")
    
    for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas']), 1):
        file_path = metadata.get('file_path', 'Unknown')
        report_id = metadata.get('id', 'Unknown')
        
        print(f"Report {i}:")
        print(f"ID: {report_id}")
        print(f"File: {file_path}")
        
        # Ask if user wants to view the full report
        view_full = input("View full report? (y/n): ").strip().lower() == 'y'
        if view_full:
            print("\n" + "=" * 80)
            print(doc)
            print("=" * 80 + "\n")
        else:
            # Show a snippet of the document (first 200 chars)
            snippet = doc[:200] + "..." if len(doc) > 200 else doc
            print(f"Snippet: {snippet}")
        
        print("-" * 80)

def find_similar_reports(store, file_path=None, report_id=None, report_type="analysis", limit=5):
    """Find reports similar to the given report."""
    collection_name = "analysis_reports" if report_type == "analysis" else "ocp_assessment_reports"
    
    # If file path is provided, read the content
    report_content = None
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return
    
    try:
        # Find similar reports
        similar_reports = store.find_similar_reports(
            report_id=report_id,
            report_content=report_content,
            collection_name=collection_name,
            n_results=limit
        )
        
        if not similar_reports:
            print(f"No similar {report_type} reports found.")
            return
        
        print(f"\nFound {len(similar_reports)} similar reports:\n")
        
        for report in similar_reports:
            similarity_percentage = report['similarity_score'] * 100
            print(f"Rank {report['rank']} - Similarity: {similarity_percentage:.1f}%")
            print(f"Component: {report['component_name']}")
            print(f"File: {report['file_path']}")
            print(f"Snippet: {report['snippet']}")
            
            # Ask if user wants to view the full report
            if len(similar_reports) <= 3 or report['rank'] <= 3:  # Auto-ask only for top 3 when more than 3 results
                view_full = input("View full report? (y/n): ").strip().lower() == 'y'
                if view_full:
                    print("\n" + "=" * 80)
                    print(report['document'])
                    print("=" * 80 + "\n")
            
            print("-" * 80)
    
    except Exception as e:
        print(f"Error finding similar reports: {str(e)}")

def context_search(store, context_description, report_type="analysis", limit=5, min_score=0.0, component=None):
    """Search for reports matching a context description."""
    collection_name = "analysis_reports" if report_type == "analysis" else "ocp_assessment_reports"
    
    # Set up filter criteria if component name is provided
    filter_criteria = {"component_name": component} if component else None
    
    try:
        # Perform the context similarity search
        similar_reports = store.context_similarity_search(
            context_description=context_description,
            collection_name=collection_name,
            n_results=limit,
            min_score=min_score,
            filter_criteria=filter_criteria
        )
        
        if not similar_reports:
            print(f"No matching {report_type} reports found for the given context.")
            return
        
        print(f"\nFound {len(similar_reports)} reports matching the context description:\n")
        
        for report in similar_reports:
            similarity_percentage = report['similarity_score'] * 100
            print(f"Rank {report['rank']} - Similarity: {similarity_percentage:.1f}%")
            print(f"Component: {report['component_name']}")
            print(f"File: {report['file_path']}")
            print(f"Relevant Context:")
            print("-" * 40)
            print(report['relevant_context'])
            print("-" * 40)
            
            # Ask if user wants to view the full report
            if len(similar_reports) <= 3 or report['rank'] <= 3:  # Auto-ask only for top 3 when more than 3 results
                view_full = input("View full report? (y/n): ").strip().lower() == 'y'
                if view_full:
                    print("\n" + "=" * 80)
                    print(report['document'])
                    print("=" * 80 + "\n")
            
            print("-" * 80)
    
    except Exception as e:
        print(f"Error performing context search: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Query and search reports stored in ChromaDB")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all components with reports")
    list_parser.add_argument("--type", choices=["analysis", "ocp"], default="analysis",
                            help="Type of reports to list (analysis or ocp)")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for reports matching a query")
    search_parser.add_argument("query", help="Text to search for in reports")
    search_parser.add_argument("--type", choices=["analysis", "ocp"], default="analysis",
                              help="Type of reports to search (analysis or ocp)")
    search_parser.add_argument("--limit", type=int, default=5,
                               help="Maximum number of results to return")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get reports for a specific component")
    get_parser.add_argument("component", help="Name of the component to get reports for")
    get_parser.add_argument("--type", choices=["analysis", "ocp"], default="analysis",
                           help="Type of reports to get (analysis or ocp)")
    
    # Similar command
    similar_parser = subparsers.add_parser("similar", help="Find reports similar to a given report")
    similar_group = similar_parser.add_mutually_exclusive_group(required=True)
    similar_group.add_argument("--file", help="Path to a report file to find similar reports")
    similar_group.add_argument("--id", help="ID of a report to find similar reports")
    similar_parser.add_argument("--type", choices=["analysis", "ocp"], default="analysis",
                              help="Type of reports to search (analysis or ocp)")
    similar_parser.add_argument("--limit", type=int, default=5,
                              help="Maximum number of results to return")
    
    # Context command
    context_parser = subparsers.add_parser("context", help="Find reports matching a context description")
    context_parser.add_argument("description", help="Context description to search for")
    context_parser.add_argument("--type", choices=["analysis", "ocp"], default="analysis",
                              help="Type of reports to search (analysis or ocp)")
    context_parser.add_argument("--limit", type=int, default=5,
                              help="Maximum number of results to return")
    context_parser.add_argument("--min-score", type=float, default=0.0,
                              help="Minimum similarity score (0.0-1.0) to include in results")
    context_parser.add_argument("--component", help="Optional component name to filter results")
    
    args = parser.parse_args()
    
    # Use context manager to prevent context leaks
    with ReportStore() as store:
        # Execute the appropriate command
        if args.command == "list":
            list_components(store, "analysis" if args.type == "analysis" else "ocp")
        elif args.command == "search":
            search_reports(store, args.query, "analysis" if args.type == "analysis" else "ocp", args.limit)
        elif args.command == "get":
            get_component_report(store, args.component, "analysis" if args.type == "analysis" else "ocp")
        elif args.command == "similar":
            find_similar_reports(
                store, 
                file_path=args.file, 
                report_id=args.id, 
                report_type="analysis" if args.type == "analysis" else "ocp",
                limit=args.limit
            )
        elif args.command == "context":
            context_search(
                store,
                context_description=args.description,
                report_type="analysis" if args.type == "analysis" else "ocp",
                limit=args.limit,
                min_score=args.min_score,
                component=args.component
            )
        else:
            parser.print_help()

if __name__ == "__main__":
    main()    