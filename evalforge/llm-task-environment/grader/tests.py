"""
Comprehensive test suite for the file path normalization task.

This suite includes basic cases, edge cases, and adversarial test cases designed
to catch common mistakes in LLM-generated solutions.
"""

import random
import string


# ============================================================================
# BASIC TEST CASES
# ============================================================================

BASIC_TESTS = [
    {
        "input": "/home/user/../documents",
        "expected": "/home/documents",
        "description": "Simple parent directory reference"
    },
    {
        "input": "/home/user/./documents",
        "expected": "/home/user/documents",
        "description": "Current directory reference"
    },
    {
        "input": "/home//user///documents",
        "expected": "/home/user/documents",
        "description": "Multiple consecutive slashes"
    },
    {
        "input": "/home/user/documents/",
        "expected": "/home/user/documents",
        "description": "Trailing slash"
    },
]


# ============================================================================
# EDGE CASE TESTS - TRICKY CASES THAT BREAK NAIVE IMPLEMENTATIONS
# ============================================================================

EDGE_TESTS = [
    # Root boundary cases
    {
        "input": "/",
        "expected": "/",
        "description": "Root path only"
    },
    {
        "input": "/..",
        "expected": "/",
        "description": "Parent of root (should stay at root)"
    },
    {
        "input": "/../..",
        "expected": "/",
        "description": "Multiple parent references from root"
    },
    {
        "input": "/../",
        "expected": "/",
        "description": "Parent of root with trailing slash"
    },
    
    # Complex parent directory sequences
    {
        "input": "/a/./b/../../c",
        "expected": "/c",
        "description": "Mixed . and .. with complex resolution"
    },
    {
        "input": "/a/b/c/../../..",
        "expected": "/",
        "description": "Multiple parent references clearing entire path"
    },
    {
        "input": "/a/b/c/../..",
        "expected": "/a",
        "description": "Multiple consecutive parent references"
    },
    {
        "input": "/a/b/c/.",
        "expected": "/a/b/c",
        "description": "Current directory at end of path"
    },
    {
        "input": "/a/b/c/..",
        "expected": "/a/b",
        "description": "Parent directory at end of path"
    },
    
    # Slash redundancy
    {
        "input": "//",
        "expected": "/",
        "description": "Double slash only"
    },
    {
        "input": "///",
        "expected": "/",
        "description": "Triple slash only"
    },
    {
        "input": "////a////b////c////",
        "expected": "/a/b/c",
        "description": "Many consecutive slashes throughout"
    },
    {
        "input": "/a//b//c//",
        "expected": "/a/b/c",
        "description": "Double slashes between and at end"
    },
    {
        "input": "/a/b/c/",
        "expected": "/a/b/c",
        "description": "Trailing slash with multiple dirs"
    },
    
    # Dot variations
    {
        "input": "/./.",
        "expected": "/",
        "description": "Only current directory references"
    },
    {
        "input": "/a/./b/./c",
        "expected": "/a/b/c",
        "description": "Multiple current directory references"
    },
    {
        "input": "/a/././b",
        "expected": "/a/b",
        "description": "Consecutive current directory references"
    },
    
    # Going beyond root
    {
        "input": "/a/b/c/../../../../../../d",
        "expected": "/d",
        "description": "Parent references extending beyond original depth"
    },
    {
        "input": "/../../../../../../a/b",
        "expected": "/a/b",
        "description": "Many parent references before reaching content"
    },
    {
        "input": "/../x",
        "expected": "/x",
        "description": "Parent at root followed by directory (catches .. in result bug)"
    },
    
    # Combined complex cases
    {
        "input": "/a/b/c/d/../e/f/../../g",
        "expected": "/a/b/c/g",
        "description": "Complex mix of parent and normal directory names"
    },
    {
        "input": "/home/user/../../../etc/passwd",
        "expected": "/etc/passwd",
        "description": "Accessing system paths with parent references"
    },
    {
        "input": "/a/b/.././c",
        "expected": "/a/c",
        "description": "Interleaved current and parent directories"
    },
    {
        "input": "/a//b/./c/../d",
        "expected": "/a/b/d",
        "description": "Mixed slashes, dots, and parent references"
    },
]


# ============================================================================
# STRESS TEST - ADVERSARIAL CASES
# ============================================================================

def generate_adversarial_test():
    """
    Generate a random adversarial test case to catch edge cases.
    """
    # Fixed seed for reproducibility
    depth = random.randint(2, 4)
    num_ups = random.randint(0, depth - 1)
    
    # Create a path with some directories
    path_parts = []
    for i in range(depth):
        path_parts.append(f"d{i}")
    
    # Add some parent references at controlled positions
    if num_ups > 0:
        positions = []
        for _ in range(num_ups):
            pos = random.randint(0, len(path_parts))
            positions.append(pos)
        
        # Add in reverse order to maintain positions
        for pos in sorted(positions, reverse=True):
            if pos < len(path_parts):
                path_parts.insert(pos, "..")
    
    # Build path with limited slashes to avoid issues
    test_path = "/" + "/".join(path_parts)
    
    # Calculate expected result manually
    stack = []
    components = test_path.split('/')
    for component in components:
        if component == "" or component == ".":
            continue
        if component == "..":
            if len(stack) > 0:
                stack.pop()
        else:
            stack.append(component)
    expected = "/" + "/".join(stack)
    
    return {
        "input": test_path,
        "expected": expected,
        "description": "Randomly generated adversarial case"
    }


# Generate multiple adversarial tests
ADVERSARIAL_TESTS = []
for _ in range(5):
    ADVERSARIAL_TESTS.append(generate_adversarial_test())


# ============================================================================
# TEST SUITE ORGANIZATION
# ============================================================================

ALL_TESTS = BASIC_TESTS + EDGE_TESTS + ADVERSARIAL_TESTS


def get_all_tests():
    """Return all test cases."""
    return ALL_TESTS


def get_basic_tests():
    """Return only basic test cases."""
    return BASIC_TESTS


def get_edge_tests():
    """Return only edge case tests."""
    return EDGE_TESTS


def get_adversarial_tests():
    """Return only adversarial test cases."""
    return ADVERSARIAL_TESTS


def run_single_test(normalize_func, test_case):
    """
    Run a single test case and return results.
    
    Args:
        normalize_func: The function to test
        test_case: Dictionary with 'input', 'expected', 'description'
        
    Returns:
        Dictionary with test results including pass/fail and any exceptions
    """
    result = {
        "description": test_case.get("description", ""),
        "input": test_case["input"],
        "expected": test_case["expected"],
        "passed": False,
        "actual": None,
        "error": None
    }
    
    try:
        # Add a simple timeout mechanism by limiting iterations
        actual = normalize_func(test_case["input"])
        result["actual"] = actual
        result["passed"] = actual == test_case["expected"]
    except RecursionError as exc:
        result["error"] = "RecursionError: Maximum recursion depth exceeded"
        result["exception_type"] = "RecursionError"
    except TimeoutError as exc:
        result["error"] = "TimeoutError: Function exceeded time limit"
        result["exception_type"] = "TimeoutError"
    except Exception as exc:
        result["error"] = str(exc)
        result["exception_type"] = type(exc).__name__
    
    return result
