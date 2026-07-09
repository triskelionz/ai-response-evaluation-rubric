import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rubric_evaluator import Criterion, Rubric, evaluate


def make_rubric() -> Rubric:
    rubric = Rubric("sample")
    rubric.add(
        Criterion(
            id="starts_hello",
            description="Starts with hello",
            weight=1,
            check=lambda r: r.strip().lower().startswith("hello"),
        )
    )
    rubric.add(
        Criterion(
            id="under_5_words",
            description="Response is under 5 words",
            weight=2,
            check=lambda r: len(r.split()) < 5,
        )
    )
    return rubric


class TestCriterion(unittest.TestCase):
    def test_evaluate_returns_bool(self):
        criterion = Criterion(
            id="c1", description="d", weight=1, check=lambda r: "x" in r
        )
        self.assertTrue(criterion.evaluate("xyz"))
        self.assertFalse(criterion.evaluate("abc"))


class TestRubric(unittest.TestCase):
    def test_total_weight(self):
        rubric = make_rubric()
        self.assertEqual(rubric.total_weight, 3)

    def test_add_returns_self_for_chaining(self):
        rubric = Rubric("chain")
        result = rubric.add(
            Criterion(id="a", description="a", weight=1, check=lambda r: True)
        )
        self.assertIs(result, rubric)


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.rubric = make_rubric()

    def test_full_pass(self):
        report = evaluate("Hello there", self.rubric)
        self.assertEqual(report.score, 3)
        self.assertEqual(report.max_score, 3)
        self.assertEqual(report.percentage, 100.0)
        self.assertTrue(all(r.passed for r in report.results))

    def test_partial_pass(self):
        report = evaluate("Hello, this response has way more than five words", self.rubric)
        self.assertEqual(report.score, 1)
        self.assertEqual(report.max_score, 3)
        self.assertAlmostEqual(report.percentage, 33.33, places=1)

    def test_full_fail(self):
        report = evaluate(
            "This response does not start with a greeting and is also quite long",
            self.rubric,
        )
        self.assertEqual(report.score, 0)
        self.assertEqual(len(report.failed_criteria), 2)

    def test_empty_rubric_has_zero_percentage(self):
        empty_rubric = Rubric("empty")
        report = evaluate("anything", empty_rubric)
        self.assertEqual(report.max_score, 0)
        self.assertEqual(report.percentage, 0.0)

    def test_report_round_trips_through_json(self):
        report = evaluate("Hello there", self.rubric)
        payload = report.to_json()
        self.assertIn("sample", payload)
        self.assertIn("starts_hello", payload)

    def test_deterministic_results(self):
        first = evaluate("Hello there", self.rubric).to_dict()
        second = evaluate("Hello there", self.rubric).to_dict()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
