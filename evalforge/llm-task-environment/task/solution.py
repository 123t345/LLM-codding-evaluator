"""
Reference solution for the file path normalization task.

This implementation correctly handles all edge cases using a stack-based approach.
"""


def normalize_path(path: str) -> str:
    """
    Normalize an absolute Unix-style file path.
    
    This solution uses a stack to track directory names:
    - Splits the path by '/' to get components
    - For each component: 
        * Skip empty strings and '.' (current directory)
        * Pop from stack for '..' (parent directory)
        * Push valid directory names
    - Join stack components with '/' and prepend with '/'
    
    Args:
        path: An absolute Unix-style file path string
        
    Returns:
        The normalized/canonical path
    """
    # Stack to store valid directory names
    stack = []
    
    # Split path by '/' to get components
    # This creates empty strings for consecutive slashes
    components = path.split('/')
    
    # Process each component
    for component in components:
        # Skip empty strings (from leading slash, trailing slash, or multiple slashes)
        if component == '':
            continue
        
        # Skip current directory reference
        if component == '.':
            continue
        
        # Parent directory reference
        if component == '..':
            # Only pop if we're not at root
            if len(stack) > 0:
                stack.pop()
        else:
            # Valid directory name - add to stack
            stack.append(component)
    
    # Reconstruct path from stack
    # Always start with '/' for absolute path
    result = '/' + '/'.join(stack)
    
    return result
