#!/usr/bin/env python3
"""AI QA Mentor Agent — CLI entry point.

Usage:
    python cli.py --docs path/to/docs.md --bugsheet path/to/bugs.csv --tester alice --project "Demo Project"
"""
import argparse
import datetime
import os
import sys

from qa_mentor.llm import DEFAULT_MODEL, LLMError
from qa_mentor.pipeline import run_pipeline


def render_report(result: dict) -> str:
    lines = []
    lines.append(f"# QA Mentor Report — {result['project']}")
    lines.append(f"Tester: {result['tester']}  |  Date: {result['session_date']}")
    lines.append("")

    total = len(result["coverage"])
    tested = sum(1 for c in result["coverage"] if c["status"] == "tested")
    partial = sum(1 for c in result["coverage"] if c["status"] == "partial")
    untested = sum(1 for c in result["coverage"] if c["status"] == "untested")
    lines.append(f"**Coverage:** {tested}/{total} tested, {partial} partial, {untested} untested")
    lines.append("")

    if not result["gaps"]:
        lines.append("No gaps found — full coverage on the extracted requirements.")
        return "\n".join(lines)

    lines.append("## Gaps, test cases & coaching")
    lines.append("")
    for gap in result["gaps"]:
        flag = " 🔁 RECURRING BLIND SPOT" if gap["is_recurring_blindspot"] else ""
        lines.append(f"### {gap['id']} — {gap['area']} [{gap['status']}]{flag}")
        lines.append(f"*{gap['description']}*")
        lines.append("")
        if gap["is_recurring_blindspot"]:
            lines.append(
                f"> You've missed this category before ({gap['prior_misses_by_this_tester']} prior session(s))."
            )
            lines.append("")
        for match in gap.get("cross_client_matches", []):
            lines.append(
                f"> 🌐 Cross-client pattern match ({match['score']}): {match['root_cause']} "
                f"— triggered by {match['trigger_condition']}."
            )
            lines.append("")
        if gap["test_steps"]:
            lines.append("**Test steps:**")
            for step in gap["test_steps"]:
                lines.append(f"- {step}")
            lines.append("")
        if gap["reasoning"]:
            lines.append(f"**Why this matters:** {gap['reasoning']}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AI QA Mentor Agent")
    parser.add_argument("--docs", required=True, help="Path to product documentation (text/markdown)")
    parser.add_argument("--bugsheet", required=True, help="Path to the tester's bug sheet (text/csv/markdown)")
    parser.add_argument("--tester", required=True, help="Tester name/identifier")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--out", default=None, help="Path to write the markdown report (default: output/<project>_<tester>.md)")
    args = parser.parse_args()

    with open(args.docs) as f:
        docs_text = f.read()
    with open(args.bugsheet) as f:
        bug_sheet_text = f.read()

    session_date = datetime.date.today().isoformat()

    print(f"Running QA Mentor pipeline for {args.tester} on '{args.project}' using {args.model}...")
    try:
        result = run_pipeline(docs_text, bug_sheet_text, args.tester, args.project, session_date, model=args.model)
    except LLMError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

    report = render_report(result)
    print("\n" + report)

    out_path = args.out or os.path.join(
        "output", f"{args.project.replace(' ', '_')}_{args.tester.replace(' ', '_')}.md"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to {out_path}")


if __name__ == "__main__":
    main()
