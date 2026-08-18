"""Stage 6 — Memory update.

Saves this session's findings to the tester's profile so future sessions can
reference their history and track whether they've improved.
"""
from .profile_store import load_profile, save_profile


def update_memory(tester: str, project: str, annotated_coverage: list, session_date: str) -> dict:
    profile = load_profile(tester)

    gaps = [c for c in annotated_coverage if c["status"] != "tested"]
    categories_missed = sorted({f"{g['category']}:{g['area']}" for g in gaps})

    for key in categories_missed:
        profile["blindspot_counts"][key] = profile["blindspot_counts"].get(key, 0) + 1

    profile["sessions"].append(
        {
            "date": session_date,
            "project": project,
            "gap_count": len(gaps),
            "categories_missed": categories_missed,
        }
    )

    save_profile(tester, profile)
    return profile
