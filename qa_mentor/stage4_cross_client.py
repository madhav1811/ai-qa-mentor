"""Stage 4 — Cross-client pattern matching (the unique step).

Separately from the personal blind-spot lookup, checks whether any
untested/partial area structurally resembles a bug motif seen in other,
unrelated client projects. Motifs are abstracted (root cause + trigger
condition, stripped of client-specific detail) — see data/bug_motifs.json.
"""
from .vector_index import load_or_build_index, top_matches

K = 2
MIN_SCORE = 0.55


def find_cross_client_matches(annotated_coverage: list, requirements: list, k: int = K, min_score: float = MIN_SCORE) -> list:
    motifs, embeddings = load_or_build_index()
    req_by_id = {r["id"]: r for r in requirements}

    enriched = []
    for c in annotated_coverage:
        if c["status"] == "tested":
            enriched.append({**c, "cross_client_matches": []})
            continue

        req = req_by_id.get(c["id"], {})
        query_text = f"{c['category']}: {c['area']}. {req.get('description', '')}"
        matches = top_matches(query_text, motifs, embeddings, k=k, min_score=min_score)
        enriched.append({**c, "cross_client_matches": matches})
    return enriched
