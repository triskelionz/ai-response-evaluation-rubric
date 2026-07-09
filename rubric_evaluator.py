"""Rule-based rubric evaluator for scoring AI/LLM responses.

Given a rubric (a set of weighted, independently checkable criteria), this
module scores a text response against the rubric and produces a
reproducible, auditable report. The same response and rubric will always
produce the same score - there is no hidden state or randomness.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Criterion:
    """A single, independently checkable rule in a rubric."""

    id: str
    description: str
    weight: float
    check: Callable[[str], bool]

    def evaluate(self, response: str) -> bool:
        return bool(self.check(response))


@dataclass
class Rubric:
    """An ordered collection of weighted criteria."""

    name: str
    criteria: List[Criterion] = field(default_factory=list)

    @property
    def total_weight(self) -> float:
        return sum(c.weight for c in self.criteria)

    def add(self, criterion: Criterion) -> "Rubric":
        self.criteria.append(criterion)
        return self


@dataclass
class CriterionResult:
    id: str
    description: str
    weight: float
    passed: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "weight": self.weight,
            "passed": self.passed,
        }


@dataclass
class EvaluationReport:
    rubric_name: str
    score: float
    max_score: float
    percentage: float
    results: List[CriterionResult]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rubric": self.rubric_name,
            "score": round(self.score, 4),
            "max_score": round(self.max_score, 4),
            "percentage": round(self.percentage, 2),
            "results": [r.to_dict() for r in self.results],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @property
    def failed_criteria(self) -> List[CriterionResult]:
        return [r for r in self.results if not r.passed]


def evaluate(response: str, rubric: Rubric) -> EvaluationReport:
    """Evaluate a single response against a rubric.

    Every criterion is checked independently, in order, so the result is
    deterministic: the same response and rubric always produce the same
    report. This is what makes rubric-based grading auditable - anyone can
    re-run the same check and get the same answer.
    """

    results: List[CriterionResult] = []
    score = 0.0

    for criterion in rubric.criteria:
        passed = criterion.evaluate(response)
        if passed:
            score += criterion.weight
        results.append(
            CriterionResult(
                id=criterion.id,
                description=criterion.description,
                weight=criterion.weight,
                passed=passed,
            )
        )

    max_score = rubric.total_weight
    percentage = (score / max_score * 100) if max_score else 0.0

    return EvaluationReport(
        rubric_name=rubric.name,
        score=score,
        max_score=max_score,
        percentage=percentage,
        results=results,
    )
