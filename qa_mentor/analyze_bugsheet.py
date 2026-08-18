"""Bug-sheet-only analysis mode.

For when there's real bug history but no written documentation to run
Stage 1 (requirement extraction) or Stage 2 (coverage mapping) against.
Runs Stage 4 (cross-client pattern matching) directly against every bug's
own description, and feeds Stage 3/6 (personal blind-spot tracking) using
each bug's "reported by" as the tester and its top-level path segment as
the category.
"""
from .bugsheet_loader import load_bug_rows
from .motif_verify import verify_matches
from .profile_store import load_profile, save_profile
from .vector_index import load_or_build_index, top_matches

RETRIEVE_K = 3
RETRIEVE_MIN_SCORE = 0.45


def analyze_bugsheet(
    xlsx_path: str,
    project: str,
    session_date: str,
    sheet_name: str = None,
    k: int = RETRIEVE_K,
    min_score: float = RETRIEVE_MIN_SCORE,
    model=None,
    verify: bool = True,
) -> tuple:
    bugs = load_bug_rows(xlsx_path, sheet_name=sheet_name)
    motifs, embeddings = load_or_build_index()

    results = []
    sections_by_tester = {}
    for bug in bugs:
        query_text = f"{bug['section']}: {bug['summary'][:500]}"
        candidates = top_matches(query_text, motifs, embeddings, k=k, min_score=min_score)
        matches = verify_matches(query_text, candidates, model=model) if verify else candidates
        results.append({**bug, "cross_client_matches": matches})
        sections_by_tester.setdefault(bug["reported_by"], set()).add(bug["section"])

    tester_reports = {}
    for tester, sections in sections_by_tester.items():
        profile = load_profile(tester)
        blindspot_counts = profile.get("blindspot_counts", {})
        recurring = sorted(s for s in sections if blindspot_counts.get(s, 0) > 0)

        for s in sections:
            blindspot_counts[s] = blindspot_counts.get(s, 0) + 1
        profile["blindspot_counts"] = blindspot_counts
        profile["sessions"].append(
            {
                "date": session_date,
                "project": project,
                "gap_count": sum(1 for b in bugs if b["reported_by"] == tester),
                "categories_missed": sorted(sections),
            }
        )
        save_profile(tester, profile)
        tester_reports[tester] = {
            "bug_count": sum(1 for b in bugs if b["reported_by"] == tester),
            "sections": sorted(sections),
            "recurring_from_prior_sessions": recurring,
        }

    return results, tester_reports
