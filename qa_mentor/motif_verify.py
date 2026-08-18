"""LLM verification pass over embedding-retrieved cross-client motif candidates.

Embedding similarity alone is good at recall but poor at precision here: on
a real 862-bug sheet, 861 bugs "matched" something at cosine >= 0.5, with a
tight, unstructured score distribution (median 0.647, max 0.771) — no
threshold cleanly separates real matches from coincidental topical overlap.
This module asks the chat model to confirm each candidate genuinely shares
the motif's root cause before it's accepted.
"""
from .llm import chat_json

SYSTEM_PROMPT = """You are a skeptical QA analyst checking whether a proposed "bug motif" (an abstracted
root cause + trigger condition pattern) genuinely applies to a specific bug, or whether it's just a
coincidental surface-level text match.

For each candidate given, decide if the bug ACTUALLY shares the motif's root cause and trigger mechanism —
not just similar wording or general topic (e.g. both happen to mention "search" or "state" or "expire").

Default to false unless the match is genuinely structural. Superficial topical overlap is NOT enough.

Return ONLY a JSON object of this exact shape:
{
  "verdicts": [
    {"motif_id": "M01", "verified": true or false, "reason": "one short sentence"}
  ]
}

Include one entry per candidate given.
"""


def verify_matches(bug_text: str, candidates: list, model=None) -> list:
    """Filters candidates down to those the LLM confirms are a genuine structural match."""
    if not candidates:
        return []

    candidate_lines = "\n".join(
        f"{c['id']}: root_cause=\"{c['root_cause']}\" trigger_condition=\"{c['trigger_condition']}\""
        for c in candidates
    )
    user_prompt = f"BUG:\n{bug_text}\n\nCANDIDATE MOTIFS:\n{candidate_lines}"
    kwargs = {"model": model} if model else {}
    result = chat_json(SYSTEM_PROMPT, user_prompt, **kwargs)
    verdicts = {v["motif_id"]: v for v in result.get("verdicts", [])}

    verified = []
    for c in candidates:
        v = verdicts.get(c["id"])
        if v and v.get("verified"):
            verified.append({**c, "verify_reason": v.get("reason", "")})
    return verified
