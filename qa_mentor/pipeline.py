"""Ties all stages together in order, matching the flow:

0. Input intake (handled by the caller: docs + bug sheet + tester profile)
1. Requirement extraction
2. Coverage mapping
3. Blind-spot matching (personal only in this build)
4. Test case + coaching generation
5. Memory update
"""
from .stage1_requirements import extract_requirements
from .stage2_coverage import map_coverage
from .stage3_blindspots import find_blindspot_matches
from .stage4_cross_client import find_cross_client_matches
from .stage5_coaching import generate_coaching
from .stage6_memory_update import update_memory
from .profile_store import load_profile


def run_pipeline(docs_text: str, bug_sheet_text: str, tester: str, project: str, session_date: str, model=None) -> dict:
    profile = load_profile(tester)

    requirements = extract_requirements(docs_text, model=model)
    coverage = map_coverage(requirements, bug_sheet_text, model=model)
    annotated_coverage = find_blindspot_matches(coverage, requirements, profile)
    annotated_coverage = find_cross_client_matches(annotated_coverage, requirements)
    coaching = generate_coaching(annotated_coverage, requirements, model=model)
    updated_profile = update_memory(tester, project, annotated_coverage, session_date)

    coaching_by_id = {c["id"]: c for c in coaching}
    req_by_id = {r["id"]: r for r in requirements}

    gaps = []
    for c in annotated_coverage:
        if c["status"] == "tested":
            continue
        coach = coaching_by_id.get(c["id"], {})
        gaps.append(
            {
                "id": c["id"],
                "description": req_by_id.get(c["id"], {}).get("description", ""),
                "category": c["category"],
                "area": c["area"],
                "status": c["status"],
                "evidence": c.get("evidence", "none"),
                "is_recurring_blindspot": c["is_recurring_blindspot"],
                "prior_misses_by_this_tester": c["prior_misses_by_this_tester"],
                "cross_client_matches": c.get("cross_client_matches", []),
                "test_steps": coach.get("test_steps", []),
                "reasoning": coach.get("reasoning", ""),
            }
        )

    return {
        "tester": tester,
        "project": project,
        "session_date": session_date,
        "requirements": requirements,
        "coverage": annotated_coverage,
        "gaps": gaps,
        "profile_after": updated_profile,
    }
