"""
Main runner for executing grading on a submission.

This module provides CLI access to the grading system and generates reports.
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path to import grader module
sys.path.insert(0, str(Path(__file__).parent.parent / "grader"))

from grade import SubmissionGrader


def grade_submission_file(
    submission_path: str,
    verbose: bool = True,
    save_json: Optional[str] = None
) -> dict:
    """
    Grade a single submission file.
    
    Args:
        submission_path: Path to the submission Python file
        verbose: Whether to print detailed output
        save_json: Optional path to save JSON results
    
    Returns:
        Grading results dictionary
    """
    submission_path = Path(submission_path)
    
    if not submission_path.exists():
        print(f"ERROR: Submission file not found: {submission_path}")
        return {"error": "File not found"}
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"GRADING SUBMISSION: {submission_path.name}")
        print(f"{'='*70}\n")
    
    # Create grader and grade submission
    grader = SubmissionGrader(str(submission_path))
    results = grader.grade(test_filter="all")
    
    # Print formatted results
    if verbose:
        print(grader.format_results_text(results))
    
    # Save JSON if requested
    if save_json:
        grader.save_results_json(save_json, results)
        if verbose:
            print(f"\nResults saved to: {save_json}\n")
    
    return results


def grade_submission_with_categories(
    submission_path: str,
    verbose: bool = True,
    save_json: Optional[str] = None
) -> dict:
    """
    Grade a submission against all test categories.
    
    Args:
        submission_path: Path to the submission Python file
        verbose: Whether to print detailed output
        save_json: Optional path to save JSON results
    
    Returns:
        Overall results dictionary
    """
    submission_path = Path(submission_path)
    
    if not submission_path.exists():
        print(f"ERROR: Submission file not found: {submission_path}")
        return {"error": "File not found"}
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"COMPREHENSIVE GRADING: {submission_path.name}")
        print(f"{'='*70}\n")
    
    grader = SubmissionGrader(str(submission_path))
    overall = grader.grade_all_categories()
    
    # Print category results
    if verbose:
        for category, results in overall["categories"].items():
            print(f"\n{category.upper()} TESTS:")
            print(f"  Score: {results['score']:.2%}")
            print(f"  Passed: {results['passed']}/{results['total']}")
            print(f"  Failed: {results['failed']}/{results['total']}")
            print(f"  Errors: {results['errors']}/{results['total']}")
        
        print(f"\n{'='*70}")
        print(f"OVERALL SCORE: {overall['overall_score']:.2%}")
        print(f"Total Passed: {overall['total_passed']}/{overall['total_tests']}")
        print(f"{'='*70}\n")
    
    if save_json:
        with open(save_json, 'w') as f:
            json.dump(overall, f, indent=2)
        if verbose:
            print(f"Results saved to: {save_json}\n")
    
    return overall


def main():
    """CLI entry point for the grader runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_task.py <submission_file> [--json <output.json>] [--detailed]")
        print("\nExamples:")
        print("  python run_task.py submission.py")
        print("  python run_task.py submission.py --json results.json")
        print("  python run_task.py submission.py --detailed")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    output_json = None
    detailed = False
    
    # Parse optional arguments
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == "--json" and i + 1 < len(sys.argv):
            output_json = sys.argv[i + 1]
        elif arg == "--detailed":
            detailed = True
    
    # Grade the submission
    if detailed:
        results = grade_submission_with_categories(
            submission_file,
            verbose=True,
            save_json=output_json
        )
    else:
        results = grade_submission_file(
            submission_file,
            verbose=True,
            save_json=output_json
        )
    
    return results


if __name__ == "__main__":
    main()
