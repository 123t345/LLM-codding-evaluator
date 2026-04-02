# LLM Coding Task Environment: Path Normalization Evaluator

A production-grade system for simulating and evaluating large language model (LLM) performance on coding tasks. This project demonstrates the methodologies used in AI evaluation platforms like Mechanize to assess code generation capabilities.

**Project Status:** ⭐ Research-Grade | Production-Ready

---

## Overview

This environment presents a deceptively simple coding task—**normalizing Unix-style file paths**—that contains numerous edge cases designed to catch common mistakes in LLM-generated code. The system simulates an LLM agent iteratively attempting to solve the task, learning from failures, and improving its solution over multiple iterations.

### Why This Task?

The file path normalization problem appears straightforward but exposes critical weaknesses in LLM reasoning:

1. **Conceptual Understanding**: Requires grasping the stack-based resolution algorithm
2. **Edge Case Handling**: Demands careful attention to boundary conditions (root directory)
3. **State Management**: Necessitates tracking directory depth and parent references
4. **Attention to Detail**: Multiple consecutive operations must be handled correctly

These are precisely the challenges that differentiate top-tier LLM implementations from mediocre ones.

---

## Project Structure

```
llm-task-environment/
│
├── task/                          # Task definition and reference implementation
│   ├── prompt.md                  # Complete task specification
│   ├── starter_code.py            # Incomplete starter function
│   └── solution.py                # Reference solution (stack-based)
│
├── grader/                        # Automated grading system
│   ├── grade.py                   # Robust grader with exception handling
│   ├── tests.py                   # 31+ comprehensive test cases
│   └── create_init.py             # Utility scripts
│
├── runner/                        # Execution and evaluation framework
│   ├── run_task.py                # CLI grader for single submissions
│   └── agent_loop.py              # LLM agent simulation with iteration
│
├── outputs/                       # Generated submissions and logs
│   ├── submission_v1.py           # First agent attempt (string replacement)
│   ├── submission_v2.py           # Second attempt (incomplete stack)
│   ├── submission_v3.py           # Final attempt (correct solution)
│   └── logs.json                  # Structured iteration log
│
├── analysis/                      # Failure analysis and insights
│   └── failure_analysis.py        # Categorizes and explains failures
│
└── README.md                      # This file
```

---

## Architecture & Design

### 1. **Task Design Phase**

The `task/` directory contains three components:

- **prompt.md**: Formal specification with examples and hidden complexity indicators
- **starter_code.py**: Incomplete function to scaffold student/LLM attempts
- **solution.py**: Reference implementation demonstrating the correct approach

The task specification intentionally highlights difficulty signals—edge cases, complexity indicators—to make it clear that naive approaches will fail.

### 2. **Grading System (Production-Grade)**

The `grader/` module delivers robust automated evaluation:

```python
# Key features of grade.py:

class SubmissionGrader:
    - Dynamic module loading (safe import of user submissions)
    - Comprehensive exception handling (catches crashes gracefully)
    - Detailed failure categorization
    - Multi-category test filtering (basic, edge, adversarial)
    - JSON reporting for downstream analysis
```

**Test Suite (`tests.py`)**: 31+ test cases organized in three tiers:

| Tier | Count | Focus |
|------|-------|-------|
| **Basic** | 4 | Simple cases (warm-up) |
| **Edge Cases** | 22 | Tricky boundaries and combinations |
| **Adversarial** | 5 | Randomly generated stress cases |

Example edge cases:
- Root boundary: `/../` should return `/` (not error)
- Statefulness: `/a/b/c/../../..` must resolve correctly
- Trailing slash: `/a/b/c/` must remove the slash
- Redundancy: `////a////b////` must normalize to `/a/b`

### 3. **Agent Loop (Iteration Simulation)**

The `runner/agent_loop.py` module simulates an LLM solving the task iteratively:

```
Iteration 1 (v1)
├─ Generate attempt (naive string replacement)
├─ Grade: 45% (fails on complex cases)
├─ Analyze: "Need state management, not string replacement"
└─ Log results

Iteration 2 (v2)
├─ Generate attempt (stack-based, incomplete)
├─ Grade: 87% (better, but boundary issues)
├─ Analyze: "Stack is good, but missing root protection"
└─ Log results

Iteration 3 (v3)
├─ Generate attempt (correct full solution)
├─ Grade: 100% (all tests pass!)
├─ Analyze: "Fixed root boundary checking"
└─ Log results
```

Each version is saved as `submission_vN.py` and graded independently.

### 4. **Failure Analysis**

The `analysis/failure_analysis.py` module performs forensic analysis on failures:

**Failure Categories**:
- **parent_directory_handling**: Issues with `..` resolution
- **root_boundary**: Problems at `/` boundary
- **slash_handling**: Multiple/trailing slash bugs
- **current_directory**: `.` reference errors
- **complex_mixed_operations**: Combinations of multiple operations

**Output**: Structured JSON with:
- Failure counts per category
- Exception types encountered
- Common wrong answers
- Improvement trajectory over iterations

---

## How It Works

### Running a Single Submission

```bash
# Basic grading
python runner/run_task.py outputs/submission_v1.py

# With detailed category breakdown
python runner/run_task.py outputs/submission_v1.py --detailed

# Save results to JSON
python runner/run_task.py outputs/submission_v1.py --json results.json
```

**Output**:
```
======================================================================
GRADING RESULTS
======================================================================
Submission: outputs/submission_v1.py

Score: 45.16%
Passed: 14/31
Failed: 14/31
Errors: 3/31

INCORRECT RESULTS:
  • Multiple parent references from root
    Input:    /../..
    Expected: /
    Got:      /..

EXCEPTIONS:
  • Complex mix of parent and normal directory names
    Type: IndexError
    Message: string index out of range
```

### Running the Agent Loop

```bash
# Simulate full LLM iteration process
python runner/agent_loop.py
```

**Output**:
```
======================================================================
AGENT LOOP: Simulating LLM Iterative Problem Solving
======================================================================

--- Iteration 1/3 (v1) ---

Description: Naive string replacement (will fail on complex cases)
Saved to: outputs/submission_v1.py
Grading...

Results:
  Score: 45.16%
  Passed: 14/31
  Failed: 14/31
  Errors: 3/31

  Top failures:
    • Multiple parent references from root
      Input:    /../..
      Expected: /
      Got:      /..

[... iterations 2 and 3 ...]

OVERALL PROGRESS
Iteration 1 (v1): 45.16% - 14/31 passed
Iteration 2 (v2): 87.10% - 27/31 passed
Iteration 3 (v3): 100.00% - 31/31 passed

Best version: v3 with 100.00%

Logs saved to: outputs/logs.json
```

### Analyzing Failures

```bash
python analysis/failure_analysis.py outputs/logs.json
```

**Output**:
```
================================================================================
FAILURE ANALYSIS REPORT
================================================================================

SUMMARY
────────────────────────────────────────────────────────────────────────────────
Total Versions Analyzed: 3
Best Version: v3 (100.00%)
Improvement from first to last: +54.84%

IMPROVEMENT TRAJECTORY
────────────────────────────────────────────────────────────────────────────────
  v1      :  45.16% (14/31 passed)
  v2      :  87.10% (27/31 passed)
  v3      : 100.00% (31/31 passed)

FAILURE CATEGORIES
────────────────────────────────────────────────────────────────────────────────
  • root_boundary: 8 failures
    - v1: Parent of root (should stay at root)
    - v1: Multiple parent references from root
  • parent_directory_handling: 6 failures
    - v1: Multiple consecutive parent references
  • complex_mixed_operations: 5 failures
    - v1: Complex mix of parent and normal directory names

MOST COMMON WRONG ANSWERS
────────────────────────────────────────────────────────────────────────────────
  • /.. : 3 times
  • /../.. : 2 times
```

---

## Observed Failure Modes in LLM Solutions

### ❌ Failure Pattern #1: Incorrect Parent Directory Handling

**Symptom**: LLM doesn't properly track directory depth

```python
# WRONG: String-based approach
while "/../" in path:
    path = path.replace("/../", "/")

# Problem: Doesn't handle beginning of path correctly
# "/../file" -> tries to find previous "/" but there are none!
```

**Fix**: Use a stack to explicitly track directory hierarchy

### ❌ Failure Pattern #2: Root Boundary Violations

**Symptom**: Going above root directory

```python
# WRONG: No bounds checking
if component == "..":
    stack.pop()  # What if stack is empty? We're at root!

# This allows representing impossible states like "//.."
```

**Fix**: Guard against popping from empty stack

```python
if component == "..":
    if len(stack) > 0:  # Only pop if not at root
        stack.pop()
```

### ❌ Failure Pattern #3: Trailing Slash Inconsistencies

**Symptom**: Incorrect handling of `/` at end of path

```python
# WRONG: Naive replacement
path = path.rstrip("/")  # Removes ALL trailing slashes
# "//" becomes "" instead of "/"

# Correct: Only remove if not root
if path != "/" and path.endswith("/"):
    path = path[:-1]
```

### ❌ Failure Pattern #4: Off-by-One Errors in Indexing

**Symptom**: Incorrect string slicing when removing parent references

```python
# WRONG: String manipulation
idx = path.find("/../")
path = path[:idx] + path[idx+3:]  # Off by one!
# Should be idx+4 (length of "/../")
```

### ✅ Why Stack-Based Solutions Win

The correct pattern uses **explicit state management**:

```python
def normalize_path(path: str) -> str:
    stack = []
    
    for component in path.split('/'):
        if component == '' or component == '.':
            continue
        elif component == '..':
            if stack:  # Bounds check
                stack.pop()
        else:
            stack.append(component)
    
    return '/' + '/'.join(stack)
```

**Why this works**:
1.  Stack maintains invariant: depth >= 0
2.  No string manipulation → no off-by-one errors
3.  Clear logic flow → easy to reason about
4.  Handles all edge cases by construction

---

## Key Features

### 🎯 Comprehensive Test Suite (31+ Cases)

- Basic functionality tests (4 cases)
- Edge cases with boundary conditions (22 cases)
- Adversarial/random stress tests (5+ cases)
- Randomized test generation for robustness

### 🔒 Robust Grading System

```python
# Safe isolation of submissions
spec = importlib.util.spec_from_file_location(...)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Exception handling
try:
    result = normalize_func(test_input)
except Exception as exc:
    # Captured, not fatal
    record_error(exc)

# Detailed failure reporting
{
    "score": 0.87,
    "passed": 27,
    "failed": 3,
    "errors": 1,
    "failure_breakdown": {
        "incorrect_results": [...],
        "exceptions": [...]
    }
}
```

### 📊 Agent-Style Iteration

- Simulates multiple solution attempts
- Tracks improvement over iterations
- Saves each version for inspection
- Logs results for forensic analysis

### 📈 Sophisticated Failure Analysis

- Categorizes failures by type
- Tracks exception patterns
- Identifies most common errors
- Computes improvement trajectory
- Generates actionable insights

### 📝 Production-Grade Code Quality

- Type hints throughout
- Comprehensive docstrings
- Clear error messages
- Structured logging
- Professional architecture

---

## Usage Examples

### Example 1: Evaluate a Custom Solution

```bash
# Create your own submission
cat > my_solution.py << 'EOF'
def normalize_path(path: str) -> str:
    # Your implementation here
    pass
EOF

# Grade it
python runner/run_task.py my_solution.py --json my_results.json
```

### Example 2: Run Full Agent Loop

```bash
cd runner
python agent_loop.py
```

This will:
1. Generate 3 simulation attempts (v1, v2, v3)
2. Grade each attempt
3. Save results to `outputs/logs.json`
4. Print iteration-by-iteration progress

### Example 3: Deep Failure Analysis

```bash
python analysis/failure_analysis.py outputs/logs.json
```

This will:
1. Load all iteration results
2. Categorize failures by type
3. Identify failure patterns
4. Generate improvement metrics
5. Save detailed analysis to `outputs/failure_analysis.json`

---

## Research Applications

This project demonstrates techniques used in:

- **LLM Evaluation Platforms** (Mechanize, HumanEval++, etc.)
- **Code Generation Benchmarks** (testing AI coding capabilities)
- **Automated Grading Systems** (robust evaluation without human intervention)
- **Educational Platforms** (scalable assessment of programming skills)
- **AI Safety Research** (understanding failure modes of code-generating models)

### Why This Approach Matters

1. **Reproducibility**: All tests are deterministic; results are repeatable
2. **Scalability**: Can evaluate thousands of submissions automatically
3. **Detailed Metrics**: Goes beyond pass/fail to categorize failure types
4. **Iterative Learning**: Simulates how LLMs improve through feedback
5. **Transparency**: All grading logic is explicit and inspectable

---

## Technical Details

### Dependencies

- Python 3.8+
- Standard library only (no external dependencies)

### How It Avoids False Negatives

1. **Robust Loading**: Handles syntax errors, missing functions, import issues
2. **Exception Isolation**: Crashes in submissions don't crash grader
3. **Type Flexibility**: Doesn't assume Python version specifics
4. **Multiple Test Tiers**: Catches failures at different abstraction levels

### Scalability Considerations

- **Per-submission**: Single submission grades in < 100ms
- **Batch processing**: Can grade 1000+ submissions efficiently
- **Parallel execution**: Design supports task parallelization
- **Memory efficient**: Tests are lightweight; no memory leaks

---

## Extending the System

### Adding New Test Cases

Edit `grader/tests.py` and add to the appropriate test list:

```python
EDGE_TESTS.append({
    "input": "/your/test/case",
    "expected": "/your/expected/result",
    "description": "Your test description"
})
```

### Adding New Simulation Attempts

Edit `runner/agent_loop.py` and add versions:

```python
ATTEMPT_V4 = '''
def normalize_path(path: str) -> str:
    # Your simulated LLM attempt
    pass
'''

ATTEMPTS["v4"] = {
    "code": ATTEMPT_V4,
    "description": "Description of this attempt"
}
```

### Customizing Failure Analysis

Extend `analysis/failure_analysis.py` with new categorization logic in `categorize_failure()`.

---

## Performance Metrics

Typical results from the agent loop simulation:

| Version | Approach | Score | Notes |
|---------|----------|-------|-------|
| **v1** | String manipulation | 45% | Fails on boundaries and complex cases |
| **v2** | Partial stack implementation | 87% | Incomplete edge case handling |
| **v3** | Correct stack-based solution | 100% | Handles all test cases correctly |

**Improvement**: +55% from naive to correct approach

---

## Files Overview

| File | Purpose | LOC |
|------|---------|-----|
| `task/prompt.md` | Task specification | 50 |
| `task/solution.py` | Reference solution | 50 |
| `grader/tests.py` | Test suite (31+ cases) | 200+ |
| `grader/grade.py` | Grading engine | 300+ |
| `runner/run_task.py` | CLI submission grader | 150 |
| `runner/agent_loop.py` | Agent simulation | 250 |
| `analysis/failure_analysis.py` | Failure categorization | 250 |

**Total**: ~1,300 lines of production-grade Python

---

## Future Enhancements

- [ ] Support for multiple programming languages (Java, JavaScript, C++)
- [ ] Real LLM API integration (GPT-4, Claude, etc.)
- [ ] Web UI for results visualization
- [ ] Distributed grading across multiple workers
- [ ] Historical tracking and benchmarking
- [ ] Custom scoring rubrics and weighting
- [ ] Time and memory profiling per submission

---

## License

This project is released as-is for research and educational purposes.

---

## Author Notes

This project simulates the kind of rigorous evaluation infrastructure used at leading AI companies to assess code generation capabilities. The deliberately tricky file path normalization task demonstrates how apparently simple problems can reveal significant weaknesses in LLM reasoning.

**Key Insight**: The value of comprehensive test suites lies not just in catching bugs, but in the categories of bugs they reveal about model reasoning patterns.

---

## Questions or Contributions?

This project demonstrates production-grade evaluation infrastructure for LLM coding tasks. For questions about methodology, evaluation techniques, or extending the system, refer to the detailed code comments and docstrings throughout.

---

**Last Updated**: April 2026  
**Status**: Production Ready 
