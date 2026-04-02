"""
Attempt 3: Correct stack-based implementation.
This properly handles all edge cases.
"""

def normalize_path(path: str) -> str:
    """
    Normalize an absolute Unix-style file path.
    
    Uses a stack-based approach to properly handle all edge cases:
    - Removes redundant slashes
    - Resolves . and .. references
    - Prevents going above root
    """
    # Stack to store valid directory names
    stack = []
    
    # Split path by '/' to get components
    components = path.split('/')
    
    # Process each component
    for component in components:
        # Skip empty strings and current directory references
        if component == '' or component == '.':
            continue
        
        # Handle parent directory reference
        if component == '..':
            # Only pop if we're not at root
            if len(stack) > 0:
                stack.pop()
        else:
            # Valid directory name - add to stack
            stack.append(component)
    
    # Reconstruct path from stack
    result = '/' + '/'.join(stack)
    
    return result
