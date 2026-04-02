"""
Attempt 1: Naive split and rejoin without proper state management.
This fails on edge cases and produces incorrect results.
"""

def normalize_path(path: str) -> str:
    """
    Normalize a Unix-style file path using simple string operations.
    
    This is a naive first attempt that fails to handle parent directory
    references correctly in edge cases.
    """
    # Split and filter empty parts
    parts = path.split("/")
    result = []
    
    for part in parts:
        if part == "" or part == ".":
            continue
        elif part == "..":
            # Naive: always remove the previous part
            # But this breaks at root because we remove leading "/"
            if result:
                result.pop()
            else:
                # BUG: This allows us to go above root
                result.append("..")
        else:
            result.append(part)
    
    # Reconstruct - but this produces wrong results
    if not result:
        return "/"
    
    # BUG: If we have ".." in result, we produce invalid paths
    path_str = "/".join(result)
    if path_str.startswith(".."):
        return "/" + path_str
    
    return "/" + path_str
