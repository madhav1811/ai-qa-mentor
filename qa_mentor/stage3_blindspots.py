"""Stage 3 — Personal blind-spot matching.

Looks up this tester's own history of what they've missed before and flags
whether any current gap structurally repeats a pattern they've missed
previously. (Cross-client pattern matching is a later phase — see the
implementation plan — and is intentionally not built here yet.)
"""


def find_blindspot_matches(coverage: list, requirements: list, profile: dict) -> list:
    req_by_id = {r["id"]: r for r in requirements}
    blindspot_counts = profile.get("blindspot_counts", {})

    annotated = []
    for c in coverage:
        req = req_by_id.get(c["id"], {})
        area = req.get("area", "")
        category = req.get("category", "")
        key = f"{category}:{area}"
        prior_misses = blindspot_counts.get(key, 0)
        annotated.append(
            {
                **c,
                "area": area,
                "category": category,
                "prior_misses_by_this_tester": prior_misses,
                "is_recurring_blindspot": c["status"] != "tested" and prior_misses > 0,
            }
        )
    return annotated
