#!/usr/bin/env python3

if __name__ == "__main__":
    print("Running test script")
    # Create a temporary output directory
    import os
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Import the module directly
    import nodes
    
    # Test the sample story generation
    fetch_jira = nodes.FetchJiraStories()
    stories = fetch_jira._generate_sample_stories("TEST", output_dir)
    
    # Print the stories for debugging
    import json
    print(json.dumps(stories[0], indent=2))

