#!/usr/bin/env python3
"""CLI for docs-less bug-sheet analysis: cross-client pattern matching +
personal blind-spot tracking run directly against a real bug sheet.

Usage:
    python analyze_bugsheet_cli.py --xlsx path/to/sheet.xlsx --project "My Project"
"""
import argparse
import datetime
import os
from collections import Counter

from qa_mentor.analyze_bugsheet import analyze_bugsheet
from qa_mentor.llm import DEFAULT_MODEL, LLMError


def render_report(results: list, tester_reports: dict, project: str, min_score: float) -> str:
    matched = [r for r in results if r["cross_client_matches"]]
    lines = [
        f"# Cross-client pattern matches — {project}",
        f"{len(matched)} / {len(results)} bugs matched a known motif (min score {min_score})",
        "",
    ]

    for r in matched:
        lines.append(f"## {r['path'] or '(no path)'}")
        lines.append(f"Reported by: {r['reported_by']} | Status: {r['status']}")
        lines.append(f"> {r['summary'][:300]}")
        for m in r["cross_client_matches"]:
            lines.append(f"- 🌐 ({m['score']}) {m['root_cause']} — triggered by {m['trigger_condition']}")
            if m.get("verify_reason"):
                lines.append(f"  - verified: {m['verify_reason']}")
        lines.append("")

    lines.append("## Motif hit frequency")
    counts = Counter(m["id"] for r in matched for m in r["cross_client_matches"])
    motif_desc = {m["id"]: m["root_cause"] for r in matched for m in r["cross_client_matches"]}
    for motif_id, count in counts.most_common():
        lines.append(f"- {motif_id} ({motif_desc[motif_id]}): {count} matches")
    lines.append("")

    lines.append("## Per-tester summary")
    for tester, report in sorted(tester_reports.items()):
        lines.append(f"- **{tester}**: {report['bug_count']} bugs across {len(report['sections'])} section(s): {', '.join(report['sections'])}")
        if report["recurring_from_prior_sessions"]:
            lines.append(f"  - 🔁 recurring from prior sessions: {', '.join(report['recurring_from_prior_sessions'])}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Docs-less bug-sheet cross-client analysis")
    parser.add_argument("--xlsx", required=True, help="Path to the bug-sheet .xlsx file")
    parser.add_argument("--sheet", default=None, help="Sheet name (default: first sheet)")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--min-score", type=float, default=0.45, help="Minimum cosine similarity for a retrieval candidate")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Ollama model to use for verification (default: {DEFAULT_MODEL})")
    parser.add_argument("--no-verify", action="store_true", help="Skip the LLM verification pass (raw embedding matches only)")
    parser.add_argument("--out", default=None, help="Path to write the markdown report")
    args = parser.parse_args()

    session_date = datetime.date.today().isoformat()

    mode = "raw embedding matches" if args.no_verify else f"embedding retrieval + LLM verification ({args.model})"
    print(f"Analyzing {args.xlsx} for cross-client patterns using {mode}...")
    try:
        results, tester_reports = analyze_bugsheet(
            args.xlsx,
            args.project,
            session_date,
            sheet_name=args.sheet,
            min_score=args.min_score,
            model=args.model,
            verify=not args.no_verify,
        )
    except LLMError as e:
        print(f"\nError: {e}")
        return

    report = render_report(results, tester_reports, args.project, args.min_score)
    matched_count = sum(1 for r in results if r["cross_client_matches"])
    print(f"\n{matched_count}/{len(results)} bugs matched a known cross-client pattern.")

    out_path = args.out or os.path.join("output", f"{args.project.replace(' ', '_')}_cross_client.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(report)
    print(f"Report saved to {out_path}")


if __name__ == "__main__":
    main()
