#!/usr/bin/env python
"""
Main entry point for the LLM task environment.

This script provides a convenient interface to run the complete workflow:
1. Agent loop (simulates LLM attempts)
2. Failure analysis (categorizes and explains failures)
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "grader"))
sys.path.insert(0, str(project_root / "runner"))
sys.path.insert(0, str(project_root / "analysis"))

from runner.agent_loop import AgentLoop
from analysis.failure_analysis import FailureAnalyzer


def main():
    """Run the complete LLM task environment workflow."""
    
    print("\n" + "=" * 80)
    print("LLM CODING TASK ENVIRONMENT")
    print("=" * 80)
    print("\nTask: Normalize File Paths")
    print("Goal: Simulate and evaluate LLM coding performance with iterative improvement")
    print()
    
    # Create outputs directory
    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    # Step 1: Run agent loop
    print("\n" + "=" * 80)
    print("STEP 1: RUNNING AGENT LOOP (LLM Simulation)")
    print("=" * 80)
    
    agent = AgentLoop(str(outputs_dir))
    results = agent.run_agent_loop(max_iterations=3)
    
    # Step 2: Analyze failures
    print("\n" + "=" * 80)
    print("STEP 2: ANALYZING FAILURES")
    print("=" * 80)
    
    logs_file = outputs_dir / "logs.json"
    if logs_file.exists():
        print()
        analyzer = FailureAnalyzer(str(logs_file))
        report = analyzer.generate_report()
        print(report)
        
        # Save analysis
        analysis_file = outputs_dir / "failure_analysis.json"
        analyzer.save_analysis(str(analysis_file))
    
    # Final summary
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  • Submissions: {outputs_dir / 'submission_v*.py'}")
    print(f"  • Logs: {logs_file}")
    print(f"  • Analysis: {outputs_dir / 'failure_analysis.json'}")
    print()


if __name__ == "__main__":
    main()
