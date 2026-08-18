"""Stage 2 — Coverage mapping.

Compares the structured requirement list against the tester's bug sheet and
tags every requirement as tested / partial / untested.
"""
from .llm import chat_json

SYSTEM_PROMPT = """You are a senior QA analyst comparing a requirement list against a tester's bug sheet
(what they tested and what bugs they found) to determine test coverage.

For EVERY requirement given, decide its coverage status:
- "tested": clear evidence in the bug sheet that this was tested (pass or fail)
- "partial": some related testing happened but not the full requirement (e.g. only the happy path)
- "untested": no evidence this was tested at all

Return ONLY a JSON object of this exact shape:
{
  "coverage": [
    {
      "id": "R1",
      "status": "tested | partial | untested",
      "evidence": "short quote or reference from the bug sheet, or 'none' if untested"
    }
  ]
}

Include exactly one entry per requirement ID given. Do not skip any.
"""


def map_coverage(requirements: list, bug_sheet_text: str, model=None) -> list:
    req_lines = "\n".join(
        f"{r['id']} [{r.get('category', '')}/{r.get('area', '')}]: {r.get('description', '')}"
        for r in requirements
    )
    user_prompt = (
        f"REQUIREMENTS:\n{req_lines}\n\n"
        f"TESTER'S BUG SHEET (what they tested + bugs found):\n{bug_sheet_text}"
    )
    kwargs = {"model": model} if model else {}
    result = chat_json(SYSTEM_PROMPT, user_prompt, **kwargs)
    return result.get("coverage", [])
