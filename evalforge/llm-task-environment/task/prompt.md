# Task: Normalize File Paths

## Objective
Implement a function that normalizes absolute Unix-style file paths by resolving `..` (parent directory) and `.` (current directory) references, and removing redundant slashes.

## Problem Statement
Given an absolute Unix-style file path as a string, return the simplified/normalized canonical path. 

### Key Rules:
1. A single dot `.` refers to the current directory
2. Double dots `..` refer to the parent directory
3. Multiple consecutive slashes `/` should be treated as a single slash
4. Trailing slashes should be removed (except for the root path `/`)
5. Invalid references to parent directory (going above root) should be ignored
6. The path always starts with `/` (it's an absolute path)

## Examples

### Basic Examples:
```python
normalize_path("/home/user/../documents") → "/home/documents"
normalize_path("/home/user/./documents") → "/home/user/documents"
normalize_path("/home//user///documents") → "/home/user/documents"
normalize_path("/home/user/documents/") → "/home/user/documents"
```

### Edge Cases:
```python
normalize_path("/") → "/"
normalize_path("/../") → "/"
normalize_path("/../../home") → "/home"
normalize_path("/a/./b/../../c") → "/c"
normalize_path("/a//b") → "/a/b"
normalize_path("/a/b/.") → "/a/b"
normalize_path("/a/b/c/..") → "/a/b"
normalize_path("/a/b/c/../../..") → "/"
```

## Function Signature
```python
def normalize_path(path: str) -> str:
    """
    Normalize an absolute Unix-style file path.
    
    Args:
        path: An absolute Unix-style file path string
        
    Returns:
        The normalized/canonical path
    """
    pass
```

## Constraints
- Input is always an absolute path (starts with `/`)
- Time complexity should be O(n) where n is the length of the path
- Space complexity should be O(n) in the worst case
- Handle invalid parent directory references gracefully (ignore them)
- The function should NOT raise exceptions for malformed input; instead, handle edge cases robustly

## Difficulty Indicators
This task appears simple at first but contains several **hidden tricky cases**:
- **Boundary conditions:** What happens at the root?
- **Redundancy:** Multiple consecutive slashes and mixed `.` and `..`
- **Statefulness:** Order of operations matters
- **Off-by-one errors:** Trailing slashes and empty tokens
- **Stack management:** Tracking directory depth

Naive string manipulation approaches often fail on combinations of these cases.
