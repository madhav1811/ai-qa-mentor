"""Stage 1 — Requirement extraction.

Reads product documentation and produces a structured list of every feature,
user flow, state, and business rule the app is supposed to support.
"""
from .llm import chat_json

SYSTEM_PROMPT = """You are a senior QA analyst extracting testable requirements from product documentation.

Read the documentation and produce a structured list of every feature, user flow, state, and business rule the application is supposed to support.

Return ONLY a JSON object of this exact shape:
{
  "requirements": [
    {
      "id": "R1",
      "category": "feature | user_flow | state | business_rule",
      "area": "short component/feature area name, e.g. 'checkout', 'login'",
      "description": "one clear sentence describing what must work"
    }
  ]
}

Rules:
- Be exhaustive: include edge cases, error states, and validation rules explicitly mentioned or clearly implied by the docs.
- Each requirement must be independently testable.
- IDs are sequential: R1, R2, R3, ...
- Do not invent features not supported by the documentation.
"""


def extract_requirements(docs_text: str, model=None) -> list:
    kwargs = {"model": model} if model else {}
    result = chat_json(SYSTEM_PROMPT, f"DOCUMENTATION:\n\n{docs_text}", **kwargs)
    return result.get("requirements", [])
