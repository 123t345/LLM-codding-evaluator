"""
Robust grader for the file path normalization task.

This module:
- Dynamically loads submission modules
- Runs all tests safely with exception handling
- Captures detailed results and failure information
- Returns structured scoring information
"""

import sys
import os
import json
import importlib.util
import traceback
import signal
from pathlib import Path
from typing import Dict, List, Any
from functools import wraps

from tests import (
    get_all_tests,
    run_single_test,
    get_basic_tests,
    get_edge_tests,
    get_adversarial_tests
)


def timeout_handler(signum, frame):
    """Handle timeout by raising an exception."""
    raise TimeoutError("Test execution exceeded time limit")


def with_timeout(seconds):
    """Decorator to add timeout to a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set up signal handler (Unix/Linux only)
            old_handler = None
            try:
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
            except (AttributeError, ValueError):
                # Windows or signal.SIGALRM not available
                pass
            
            try:
                result = func(*args, **kwargs)
                # Cancel the alarm
                try:
                    signal.alarm(0)
                except (AttributeError, ValueError):
                    pass
                return result
            finally:
                # Restore old handler
                if old_handler is not None:
                    try:
                        signal.signal(signal.SIGALRM, old_handler)
                    except (AttributeError, ValueError):
                        pass
        
        return wrapper
    return decorator


class GradingError(Exception):
    """Custom exception for grading errors."""
    pass


class SubmissionGrader:
    """
    Robust grader for submissions to the normalize_path task.
    """
    
    def __init__(self, submission_path: str):
        """
        Initialize the grader with a submission file.
        
        Args:
            submission_path: Path to the submission Python file
        """
        self.submission_path = Path(submission_path)
        self.normalize_func = None
        self.load_errors = []
    
    def load_submission(self) -> bool:
        """
        Dynamically load the submission module and extract normalize_path function.
        
        Returns:
            True if loading succeeded, False otherwise
        """
        try:
            if not self.submission_path.exists():
                self.load_errors.append(f"File not found: {self.submission_path}")
                return False
            
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(
                "submission_module",
                self.submission_path
            )
            
            if spec is None or spec.loader is None:
                self.load_errors.append("Could not create module spec")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["submission_module"] = module
            spec.loader.exec_module(module)
            
            # Extract the normalize_path function
            if not hasattr(module, 'normalize_path'):
                self.load_errors.append(
                    "Module does not contain 'normalize_path' function"
                )
                return False
            
            self.normalize_func = module.normalize_path
            return True
        
        except SyntaxError as exc:
            self.load_errors.append(f"Syntax error in submission: {str(exc)}")
            return False
        except Exception as exc:
            self.load_errors.append(f"Error loading submission: {str(exc)}")
            self.load_errors.append(traceback.format_exc())
            return False
    
    def grade(self, test_filter: str = "all") -> Dict[str, Any]:
        """
        Grade the submission against all test cases.
        
        Args:
            test_filter: Which test subset to use
                - "all": All tests
                - "basic": Basic tests only
                - "edge": Edge cases only
                - "adversarial": Adversarial tests only
        
        Returns:
            Dictionary with detailed grading results
        """
        result = {
            "submission_path": str(self.submission_path),
            "loaded": False,
            "load_errors": self.load_errors,
            "score": 0.0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total": 0,
            "test_results": [],
            "failure_breakdown": {
                "incorrect_results": [],
                "exceptions": [],
                "timeout_or_crash": []
            },
            "category_breakdown": {}
        }
        
        # Check if we need to load the submission
        if self.normalize_func is None:
            if not self.load_submission():
                result["loaded"] = False
                return result
        
        result["loaded"] = True
        
        # Select test set
        if test_filter == "basic":
            tests = get_basic_tests()
        elif test_filter == "edge":
            tests = get_edge_tests()
        elif test_filter == "adversarial":
            tests = get_adversarial_tests()
        else:
            tests = get_all_tests()
        
        result["total"] = len(tests)
        
        # Run each test
        for test_case in tests:
            test_result = run_single_test(self.normalize_func, test_case)
            result["test_results"].append(test_result)
            
            # Update counts
            if test_result["error"] is not None:
                result["errors"] += 1
                result["failure_breakdown"]["exceptions"].append({
                    "test": test_case.get("description", ""),
                    "error": test_result["error"],
                    "type": test_result.get("exception_type", "Unknown")
                })
            elif test_result["passed"]:
                result["passed"] += 1
            else:
                result["failed"] += 1
                result["failure_breakdown"]["incorrect_results"].append({
                    "test": test_case.get("description", ""),
                    "input": test_case["input"],
                    "expected": test_case["expected"],
                    "actual": test_result["actual"]
                })
        
        # Calculate score
        if result["total"] > 0:
            result["score"] = result["passed"] / result["total"]
        
        return result
    
    def grade_all_categories(self) -> Dict[str, Any]:
        """
        Grade the submission against all test categories separately.
        
        Returns:
            Dictionary with results for each category
        """
        categories = ["basic", "edge", "adversarial"]
        results = {}
        
        for category in categories:
            results[category] = self.grade(test_filter=category)
        
        # Create overall summary
        overall = {
            "categories": results,
            "overall_score": 0.0,
            "total_passed": 0,
            "total_failed": 0,
            "total_errors": 0,
            "total_tests": 0
        }
        
        for category_results in results.values():
            overall["total_passed"] += category_results["passed"]
            overall["total_failed"] += category_results["failed"]
            overall["total_errors"] += category_results["errors"]
            overall["total_tests"] += category_results["total"]
        
        if overall["total_tests"] > 0:
            overall["overall_score"] = (
                overall["total_passed"] / overall["total_tests"]
            )
        
        return overall
    
    def save_results_json(self, output_path: str, results: Dict[str, Any]) -> None:
        """
        Save grading results to a JSON file.
        
        Args:
            output_path: Path where to save the results
            results: Results dictionary from grade() or grade_all_categories()
        """
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    def format_results_text(self, results: Dict[str, Any]) -> str:
        """
        Format grading results as human-readable text.
        
        Args:
            results: Results dictionary from grade()
        
        Returns:
            Formatted string representation
        """
        lines = []
        lines.append("=" * 70)
        lines.append("GRADING RESULTS")
        lines.append("=" * 70)
        
        if not results["loaded"]:
            lines.append("LOAD FAILED")
            for error in results["load_errors"]:
                lines.append(f"  ERROR: {error}")
            return "\n".join(lines)
        
        lines.append(f"Submission: {results['submission_path']}")
        lines.append("")
        lines.append(f"Score: {results['score']:.2%}")
        lines.append(f"Passed: {results['passed']}/{results['total']}")
        lines.append(f"Failed: {results['failed']}/{results['total']}")
        lines.append(f"Errors: {results['errors']}/{results['total']}")
        lines.append("")
        
        # Show incorrect results
        if results["failure_breakdown"]["incorrect_results"]:
            lines.append("INCORRECT RESULTS:")
            for failure in results["failure_breakdown"]["incorrect_results"]:
                lines.append(f"  • {failure['test']}")
                lines.append(f"    Input:    {failure['input']}")
                lines.append(f"    Expected: {failure['expected']}")
                lines.append(f"    Got:      {failure['actual']}")
        
        # Show exceptions
        if results["failure_breakdown"]["exceptions"]:
            lines.append("")
            lines.append("EXCEPTIONS:")
            for exception in results["failure_breakdown"]["exceptions"]:
                lines.append(f"  • {exception['test']}")
                lines.append(f"    Type: {exception['type']}")
                lines.append(f"    Message: {exception['error']}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)


def grade_submission(submission_path: str, output_json: str = None) -> Dict[str, Any]:
    """
    Standalone function to grade a submission.
    
    Args:
        submission_path: Path to the submission file
        output_json: Optional path to save results as JSON
    
    Returns:
        Grading results dictionary
    """
    grader = SubmissionGrader(submission_path)
    results = grader.grade(test_filter="all")
    
    if output_json:
        grader.save_results_json(output_json, results)
    
    return results
