import os
import re
import json

def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): The path to the directory to check/create
        
    Returns:
        str: The normalized directory path
    """
    directory_path = os.path.normpath(directory_path)
    os.makedirs(directory_path, exist_ok=True)
    return directory_path

def format_file_size(size_in_bytes):
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        size_in_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "2.5 MB")
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

def truncate_text(text, max_length=100, ellipsis="..."):
    """
    Truncate text to a specified maximum length.
    
    Args:
        text (str): The text to truncate
        max_length (int): Maximum length of the returned string
        ellipsis (str): String to append to truncated text
        
    Returns:
        str: Truncated text
    """
    if text is None:
        return ""
    
    text = str(text)
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(ellipsis)] + ellipsis

def extract_json_from_llm_response(response):
    """
    Extract JSON from an LLM response that might contain extra text.
    
    Args:
        response (str): The raw response from an LLM
        
    Returns:
        dict: Parsed JSON dictionary or None if parsing fails
    """
    response = response.strip()
    
    # Find JSON within code blocks
    code_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    code_matches = re.findall(code_block_pattern, response)
    
    # If we found JSON in code blocks, use the first one
    if code_matches:
        json_str = code_matches[0].strip()
    else:
        # Otherwise, try to find JSON within the response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return None
            
        json_str = response[start_idx:end_idx]
    
    # Try to parse the JSON
    try:
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError:
        return None

def is_valid_github_url(url):
    """
    Check if a URL is a valid GitHub repository URL.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if valid GitHub URL, False otherwise
    """
    if not url:
        return False
    
    # Common GitHub URL patterns
    patterns = [
        r'^https?://(?:www\.)?github\.com/[\w-]+/[\w-]+(?:\.git)?$',
        r'^git@github\.com:[\w-]+/[\w-]+(?:\.git)?$'
    ]
    
    return any(re.match(pattern, url.strip()) for pattern in patterns)

def find_component_in_text(component_name, text):
    """
    Check if a component name appears in text.
    
    Args:
        component_name (str): Name of component to search for
        text (str): Text to search within
        
    Returns:
        bool: True if component name found, False otherwise
    """
    if not component_name or not text:
        return False
    
    component_name = component_name.lower()
    text = text.lower()
    
    # Check for exact match
    if component_name in text:
        return True
    
    # Check for word boundaries
    words = re.findall(r'\b' + re.escape(component_name) + r'\b', text)
    if words:
        return True
    
    # Check for similar words (e.g., plural forms)
    if component_name.endswith('s') and component_name[:-1] in text:
        return True
    if not component_name.endswith('s') and component_name + 's' in text:
        return True
    
    return False 