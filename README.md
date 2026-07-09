# AI Response Evaluation Rubric

A small Python framework for scoring AI/LLM responses against structured, rule-based rubrics. It turns subjective review ("is this answer good?") into a deterministic, auditable process: each rubric is a list of independent, weighted criteria, and every criterion is either clearly passed or clearly failed.

## Why rubric-based evaluation

When you are reviewing model outputs at scale - grading responses, checking instruction-following, or building QA pipelines for AI training data - ad-hoc judgments do not scale and are hard to justify. A rubric-based approach fixes that:

- Every criterion is a small, independently testable rule (a plain Python function)
- Every criterion has an explicit weight, so the final score reflects priorities, not vibes
- The same response and rubric always produce the same report - fully reproducible
- Results are structured JSON, so they can be logged, diffed, and reviewed later

## Installation

No dependencies beyond the Python standard library.

```bash
git clone https://github.com/triskelionz/ai-response-evaluation-rubric.git
cd ai-response-evaluation-rubric
```

## Quick start

```python
from rubric_evaluator import Criterion, Rubric, evaluate

rubric = (
    Rubric("instruction-following")
    .add(Criterion(
        id="has_greeting",
        description="Response starts with a greeting",
        weight=1,
        check=lambda r: r.strip().lower().startswith(("hello", "hi")),
    ))
    .add(Criterion(
        id="under_word_limit",
        description="Response is 50 words or fewer",
        weight=2,
        check=lambda r: len(r.split()) <= 50,
    ))
    .add(Criterion(
        id="no_placeholder_text",
        description="Response does not contain leftover placeholder text",
        weight=1,
        check=lambda r: "[insert" not in r.lower() and "TODO" not in r,
    ))
)

response = "Hello! Thanks for reaching out - here is a short, complete answer."

report = evaluate(response, rubric)
print(report.to_json())
```

Output:

```json
{
  "rubric": "instruction-following",
  "score": 4.0,
  "max_score": 4.0,
  "percentage": 100.0,
  "results": [
    {"id": "has_greeting", "description": "Response starts with a greeting", "weight": 1, "passed": true},
    {"id": "under_word_limit", "description": "Response is 50 words or fewer", "weight": 2, "passed": true},
    {"id": "no_placeholder_text", "description": "Response does not contain leftover placeholder text", "weight": 1, "passed": true}
  ]
}
```

Run the full example (multiple sample responses against the same rubric):

```bash
python example.py
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Project structure

- `rubric_evaluator.py` - core library: `Criterion`, `Rubric`, `evaluate`, `EvaluationReport`
- `example.py` - a runnable example rubric evaluated against several sample responses
- `tests/test_rubric_evaluator.py` - unit tests covering scoring, weighting, and edge cases

## Why this matters

This project mirrors the core skill behind structured AI evaluation and rule-based QA work: breaking a fuzzy judgment call into explicit, independently verifiable criteria, applying them consistently, and producing a result that someone else can audit and reproduce - rather than a one-off opinion.

## License

MIT
