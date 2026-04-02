"""
Agent loop that simulates an LLM iteratively solving the task.

This module demonstrates:
- Generating initial (flawed) attempts at the task
- Grading each attempt
- Learning from failures
- Iteratively improving the solution
- Tracking progress over iterations
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "grader"))

from grade import SubmissionGrader


# ============================================================================
# SIMULATED LLM ATTEMPTS - Different levels of correctness
# ============================================================================

ATTEMPT_V1 = '''"""
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
'''

ATTEMPT_V2 = '''"""
Attempt 2: Stack-based approach but with incomplete handling of slashes.
This handles parent directory references but fails on slash normalization edge cases.
"""

def normalize_path(path: str) -> str:
    """
    Normalize using a stack approach but with incomplete edge case handling.
    
    This version correctly uses a stack for directory management but
    fails to properly handle certain slash edge cases.
    """
    # Stack to store valid directory names
    stack = []
    
    # Split path by '/' to get components
    # This creates empty strings from consecutive slashes
    components = path.split('/')
    
    # Process each component
    for component in components:
        # Skip empty strings and current directory references
        if component == '' or component == '.':
            continue
        
        # Handle parent directory reference
        if component == '..':
            # Correctly only pop if we're not at root
            if len(stack) > 0:
                stack.pop()
            # BUG: If stack is empty, we silently ignore it
            # But we should ensure we stay at root
        else:
            # Valid directory name - add to stack
            stack.append(component)
    
    # Reconstruct path from stack
    # BUG: This doesn't properly handle some edge cases with empty stacks
    result = '/' + '/'.join(stack)
    
    # Another BUG: Trailing slash handling is missing
    if path.endswith('/') and result != '/' and len(stack) > 0:
        result = result + '/'
    
    return result
'''

ATTEMPT_V3 = '''"""
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
'''

# ============================================================================
# ATTEMPT REGISTRY
# ============================================================================

ATTEMPTS = {
    "v1": {
        "code": ATTEMPT_V1,
        "description": "Naive string replacement (will fail on complex cases)"
    },
    "v2": {
        "code": ATTEMPT_V2,
        "description": "Stack-based with incomplete edge case handling"
    },
    "v3": {
        "code": ATTEMPT_V3,
        "description": "Correct stack-based implementation"
    }
}


# ============================================================================
# AGENT LOOP Implementation
# ============================================================================

class AgentLoop:
    """
    Simulates an LLM agent iteratively solving the normalization task.
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the agent loop.
        
        Args:
            output_dir: Directory to save submissions and logs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.submission_files = []
        self.results_log = []
        self.iteration = 0
    
    def save_attempt(self, version: str, code: str) -> str:
        """
        Save an attempt to a Python file.
        
        Args:
            version: Version identifier (e.g., "v1", "v2")
            code: Python code for the attempt
        
        Returns:
            Path to the saved file
        """
        filename = f"submission_{version}.py"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return str(filepath)
    
    def grade_attempt(self, submission_path: str, version: str) -> Dict[str, Any]:
        """
        Grade a single attempt.
        
        Args:
            submission_path: Path to the submission file
            version: Version identifier
        
        Returns:
            Grading results
        """
        grader = SubmissionGrader(submission_path)
        results = grader.grade(test_filter="all")
        results["version"] = version
        results["timestamp"] = datetime.now().isoformat()
        
        return results
    
    def run_agent_loop(self, max_iterations: int = 3) -> List[Dict[str, Any]]:
        """
        Run the agent loop, attempting multiple versions of the solution.
        
        Args:
            max_iterations: Maximum number of iterations to run
        
        Returns:
            List of results for each iteration
        """
        print(f"\n{'='*70}")
        print("AGENT LOOP: Simulating LLM Iterative Problem Solving")
        print(f"{'='*70}\n")
        
        all_results = []
        versions_to_try = ["v1", "v2", "v3"]
        
        for i, version in enumerate(versions_to_try[:max_iterations], 1):
            print(f"\n--- Iteration {i}/{max_iterations} ({version}) ---\n")
            
            attempt_info = ATTEMPTS[version]
            
            # Save the attempt
            print(f"Description: {attempt_info['description']}")
            filepath = self.save_attempt(version, attempt_info['code'])
            print(f"Saved to: {filepath}")
            
            # Grade the attempt
            print("Grading...")
            results = self.grade_attempt(filepath, version)
            all_results.append(results)
            
            # Print summary
            print(f"\nResults:")
            print(f"  Score: {results['score']:.2%}")
            print(f"  Passed: {results['passed']}/{results['total']}")
            print(f"  Failed: {results['failed']}/{results['total']}")
            print(f"  Errors: {results['errors']}/{results['total']}")
            
            # Show key failures
            if results['failed'] > 0:
                print(f"\n  Top failures:")
                for failure in results['failure_breakdown']['incorrect_results'][:3]:
                    print(f"    • {failure['test']}")
                    print(f"      Input:    {failure['input']}")
                    print(f"      Expected: {failure['expected']}")
                    print(f"      Got:      {failure['actual']}")
            
            if results['errors'] > 0:
                print(f"\n  Exceptions encountered:")
                for exc in results['failure_breakdown']['exceptions'][:2]:
                    print(f"    • {exc['test']}: {exc['type']}")
        
        # Save overall log
        self.save_logs(all_results)
        
        # Print progress summary
        print(f"\n{'='*70}")
        print("OVERALL PROGRESS")
        print(f"{'='*70}\n")
        
        for i, results in enumerate(all_results, 1):
            version = results['version']
            score = results['score']
            print(f"Iteration {i} ({version}): {score:.2%} - {results['passed']}/{results['total']} passed")
        
        best_result = max(all_results, key=lambda r: r['score'])
        print(f"\nBest version: {best_result['version']} with {best_result['score']:.2%}")
        
        return all_results
    
    def save_logs(self, results: List[Dict[str, Any]]) -> str:
        """
        Save detailed logs to JSON file.
        
        Args:
            results: List of grading results
        
        Returns:
            Path to the logs file
        """
        logs_file = self.output_dir / "logs.json"
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "total_iterations": len(results),
            "results": results,
            "summary": {
                "best_score": max(r['score'] for r in results) if results else 0,
                "best_version": max(results, key=lambda r: r['score'])['version'] if results else None,
                "improvement": results[-1]['score'] - results[0]['score'] if len(results) > 1 else 0
            }
        }
        
        with open(logs_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\nLogs saved to: {logs_file}")
        return str(logs_file)


def main():
    """Main entry point for the agent loop."""
    # Create output directory
    outputs_dir = Path(__file__).parent.parent / "outputs"
    
    # Run the agent loop
    agent = AgentLoop(str(outputs_dir))
    results = agent.run_agent_loop(max_iterations=3)
    
    return results


if __name__ == "__main__":
    main()
