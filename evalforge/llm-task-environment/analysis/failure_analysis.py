"""
Failure analysis tool for understanding what went wrong.

This module analyzes grading results and logs to categorize and understand
failure modes, providing insights into why LLM solutions fail.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class FailureAnalyzer:
    """
    Analyzes failure patterns in LLM code submissions.
    """
    
    def __init__(self, logs_path: str):
        """
        Initialize the analyzer with logs file.
        
        Args:
            logs_path: Path to the logs.json file
        """
        self.logs_path = Path(logs_path)
        self.logs_data = None
        self.load_logs()
    
    def load_logs(self) -> None:
        """Load and parse the logs JSON file."""
        if not self.logs_path.exists():
            raise FileNotFoundError(f"Logs file not found: {self.logs_path}")
        
        with open(self.logs_path, 'r') as f:
            self.logs_data = json.load(f)
    
    def categorize_failure(self, test_description: str, failure_type: str) -> str:
        """
        Categorize a failure based on test description and type.
        
        Args:
            test_description: Description of the test case
            failure_type: Type of failure ("incorrect", "exception", "timeout")
        
        Returns:
            Category string
        """
        desc_lower = test_description.lower()
        
        # Logic errors related to parent directory handling
        if ".." in desc_lower or "parent" in desc_lower:
            return "parent_directory_handling"
        
        # Root boundary issues
        if "root" in desc_lower or "boundary" in desc_lower:
            return "root_boundary"
        
        # Slash/delimiter issues
        if "slash" in desc_lower or "slash" in desc_lower or "delimiter" in desc_lower:
            return "slash_handling"
        
        # Current directory (dot) handling
        if "current" in desc_lower or "." in desc_lower and "dot" not in desc_lower.lower():
            return "current_directory"
        
        # Trailing slash issues
        if "trailing" in desc_lower:
            return "trailing_slash"
        
        # Complex/adversarial cases
        if "complex" in desc_lower or "mixed" in desc_lower or "adversarial" in desc_lower:
            return "complex_mixed_operations"
        
        # Default category
        return "other"
    
    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze all results and categorize failures.
        
        Returns:
            Dictionary with detailed failure analysis
        """
        analysis = {
            "total_versions": len(self.logs_data.get("results", [])),
            "summary": self.logs_data.get("summary", {}),
            "by_version": {},
            "failure_categories": defaultdict(lambda: {"count": 0, "tests": []}),
            "exception_types": defaultdict(int),
            "common_wrong_answers": defaultdict(int),
            "improvement_trajectory": []
        }
        
        # Analyze each version's results
        for result in self.logs_data.get("results", []):
            version = result["version"]
            score = result["score"]
            
            analysis["improvement_trajectory"].append({
                "version": version,
                "score": score,
                "passed": result["passed"],
                "failed": result["failed"],
                "errors": result["errors"]
            })
            
            version_analysis = {
                "score": score,
                "passed": result["passed"],
                "failed": result["failed"],
                "errors": result["errors"],
                "top_failures": [],
                "exception_summary": []
            }
            
            # Categorize incorrect results
            for failure in result["failure_breakdown"].get("incorrect_results", []):
                category = self.categorize_failure(failure["test"], "incorrect")
                analysis["failure_categories"][category]["count"] += 1
                analysis["failure_categories"][category]["tests"].append({
                    "version": version,
                    "test": failure["test"],
                    "input": failure["input"],
                    "expected": failure["expected"],
                    "actual": failure["actual"]
                })
                analysis["common_wrong_answers"][failure["actual"]] += 1
                
                version_analysis["top_failures"].append({
                    "test": failure["test"],
                    "category": category
                })
            
            # Categorize exceptions
            for exception in result["failure_breakdown"].get("exceptions", []):
                exc_type = exception.get("type", "Unknown")
                analysis["exception_types"][exc_type] += 1
                version_analysis["exception_summary"].append({
                    "test": exception["test"],
                    "type": exc_type
                })
            
            analysis["by_version"][version] = version_analysis
        
        return analysis
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive failure analysis report.
        
        Returns:
            Formatted report string
        """
        analysis = self.analyze_results()
        lines = []
        
        lines.append("=" * 80)
        lines.append("FAILURE ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Versions Analyzed: {analysis['total_versions']}")
        summary = analysis["summary"]
        if summary:
            lines.append(f"Best Version: {summary.get('best_version')} ({summary.get('best_score', 0):.2%})")
            improvement = summary.get('improvement', 0)
            lines.append(f"Improvement from first to last: {improvement:+.2%}")
        lines.append("")
        
        # Improvement trajectory
        lines.append("IMPROVEMENT TRAJECTORY")
        lines.append("-" * 80)
        for entry in analysis["improvement_trajectory"]:
            version = entry["version"]
            score = entry["score"]
            passed = entry["passed"]
            total = passed + entry["failed"] + entry["errors"]
            lines.append(f"  {version:8s}: {score:6.2%} ({passed}/{total} passed)")
        lines.append("")
        
        # Failure categories
        lines.append("FAILURE CATEGORIES")
        lines.append("-" * 80)
        
        # Sort by frequency
        sorted_categories = sorted(
            analysis["failure_categories"].items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        for category, data in sorted_categories:
            count = data["count"]
            lines.append(f"  • {category}: {count} failures")
            
            # Show example tests from this category (from different versions)
            shown_tests = set()
            for test_info in data["tests"][:2]:
                test_name = test_info["test"]
                if test_name not in shown_tests:
                    lines.append(f"    - {test_info['version']}: {test_name}")
                    shown_tests.add(test_name)
        
        lines.append("")
        
        # Exception types
        if analysis["exception_types"]:
            lines.append("EXCEPTION TYPES ENCOUNTERED")
            lines.append("-" * 80)
            for exc_type, count in sorted(
                analysis["exception_types"].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                lines.append(f"  • {exc_type}: {count} occurrences")
            lines.append("")
        
        # Common wrong answers
        if analysis["common_wrong_answers"]:
            lines.append("MOST COMMON WRONG ANSWERS")
            lines.append("-" * 80)
            sorted_wrong = sorted(
                analysis["common_wrong_answers"].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for answer, count in sorted_wrong[:5]:
                lines.append(f"  • {answer}: {count} times")
            lines.append("")
        
        # Per-version details
        lines.append("DETAILED VERSION ANALYSIS")
        lines.append("-" * 80)
        for version in sorted(analysis["by_version"].keys()):
            v_analysis = analysis["by_version"][version]
            lines.append(f"\n{version}:")
            lines.append(f"  Score: {v_analysis['score']:.2%}")
            lines.append(f"  Results: {v_analysis['passed']} passed, "
                        f"{v_analysis['failed']} failed, "
                        f"{v_analysis['errors']} errors")
            
            if v_analysis["top_failures"]:
                lines.append(f"  Top failure categories:")
                categories_seen = set()
                for failure in v_analysis["top_failures"][:3]:
                    cat = failure["category"]
                    if cat not in categories_seen:
                        lines.append(f"    - {cat}")
                        categories_seen.add(cat)
            
            if v_analysis["exception_summary"]:
                lines.append(f"  Exception types:")
                for exc in v_analysis["exception_summary"][:2]:
                    lines.append(f"    - {exc['type']}: {exc['test']}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def save_analysis(self, output_path: str) -> None:
        """
        Save detailed analysis to JSON file.
        
        Args:
            output_path: Path to save analysis JSON
        """
        analysis = self.analyze_results()
        
        # Convert defaultdict to regular dict for JSON serialization
        analysis_json = {
            "total_versions": analysis["total_versions"],
            "summary": analysis["summary"],
            "by_version": dict(analysis["by_version"]),
            "failure_categories": {
                k: {
                    "count": v["count"],
                    "tests": v["tests"]
                }
                for k, v in analysis["failure_categories"].items()
            },
            "exception_types": dict(analysis["exception_types"]),
            "common_wrong_answers": dict(analysis["common_wrong_answers"]),
            "improvement_trajectory": analysis["improvement_trajectory"]
        }
        
        with open(output_path, 'w') as f:
            json.dump(analysis_json, f, indent=2)


def analyze_logs_file(logs_path: str) -> None:
    """
    Main function to analyze logs and print report.
    
    Args:
        logs_path: Path to the logs.json file
    """
    try:
        analyzer = FailureAnalyzer(logs_path)
        report = analyzer.generate_report()
        print(report)
        
        # Also save analysis to JSON
        analysis_path = Path(logs_path).parent / "failure_analysis.json"
        analyzer.save_analysis(str(analysis_path))
        print(f"\nDetailed analysis saved to: {analysis_path}")
    
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python failure_analysis.py <logs.json>")
        print("\nExample:")
        print("  python failure_analysis.py outputs/logs.json")
        sys.exit(1)
    
    logs_file = sys.argv[1]
    analyze_logs_file(logs_file)


if __name__ == "__main__":
    main()
