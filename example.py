"""Runnable example: score several sample responses against one rubric.

This mirrors a realistic AI-training QA task: given a prompt and a set of
candidate responses, apply a fixed set of rules and report which
responses pass, which fail, and why.
"""

from rubric_evaluator import Criterion, Rubric, evaluate


def build_rubric() -> Rubric:
    rubric = Rubric("instruction-following")

    rubric.add(
        Criterion(
            id="has_greeting",
            description="Response starts with a greeting",
            weight=1,
            check=lambda r: r.strip().lower().startswith(("hello", "hi")),
        )
    )
    rubric.add(
        Criterion(
            id="under_word_limit",
            description="Response is 50 words or fewer",
            weight=2,
            check=lambda r: len(r.split()) <= 50,
        )
    )
    rubric.add(
        Criterion(
            id="no_placeholder_text",
            description="Response does not contain leftover placeholder text",
            weight=1,
            check=lambda r: "[insert" not in r.lower() and "TODO" not in r,
        )
    )
    rubric.add(
        Criterion(
            id="answers_the_question",
            description="Response contains a question mark being answered (no unresolved question)",
            weight=1,
            check=lambda r: not r.strip().endswith("?"),
        )
    )

    return rubric


SAMPLE_RESPONSES = [
    "Hello! Thanks for reaching out - here is a short, complete answer.",
    "Hi there, [insert personalized message here]. Let me know if you need anything else.",
    (
        "Hello, thank you for your patience. To summarize the situation in full detail, "
        "here is a very long response that goes far beyond what is needed to answer the "
        "original question, repeating itself several times just to pad out the word count "
        "well past the fifty word limit that this rubric is checking for in this example."
    ),
    "Not sure what you mean, could you clarify?",
]


def main() -> None:
    rubric = build_rubric()

    for i, response in enumerate(SAMPLE_RESPONSES, start=1):
        report = evaluate(response, rubric)
        print(f"--- Response {i} ---")
        print(response)
        print(report.to_json())
        print()


if __name__ == "__main__":
    main()
