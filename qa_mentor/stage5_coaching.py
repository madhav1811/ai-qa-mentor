"""Stage 5 — Test case + coaching generation.

For every real gap, produces the exact test steps to run plus a
plain-language explanation of the general reasoning pattern behind it.
"""
from .llm import chat_json

SYSTEM_PROMPT = """You are an AI QA mentor. For each coverage gap given (status "partial" or "untested"),
produce concrete guidance so the tester both closes the gap AND learns something reusable.

For gaps flagged is_recurring_blindspot=true, explicitly name in the reasoning that this is a pattern
this tester has missed before, so they notice the recurring habit.

Return ONLY a JSON object of this exact shape:
{
  "coaching": [
    {
      "id": "R1",
      "test_steps": ["Step 1: ...", "Step 2: ...", "..."],
      "reasoning": "plain-language explanation of the general testing principle behind this gap"
    }
  ]
}

Include one entry per gap given. Be specific and actionable in test_steps — exact actions/inputs, not vague advice.
"""


def generate_coaching(annotated_coverage: list, requirements: list, model=None) -> list:
    req_by_id = {r["id"]: r for r in requirements}
    gaps = [c for c in annotated_coverage if c["status"] != "tested"]
    if not gaps:
        return []

    gap_lines = "\n".join(
        f"{g['id']} [{g['category']}/{g['area']}] status={g['status']} "
        f"prior_misses_by_this_tester={g['prior_misses_by_this_tester']} "
        f"is_recurring_blindspot={g['is_recurring_blindspot']}: "
        f"{req_by_id.get(g['id'], {}).get('description', '')}"
        for g in gaps
    )
    kwargs = {"model": model} if model else {}
    result = chat_json(SYSTEM_PROMPT, f"GAPS:\n{gap_lines}", **kwargs)
    return result.get("coaching", [])
