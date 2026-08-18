"""A small local vector index over the bug-motif corpus.

Deliberately avoids a heavyweight vector-database dependency: the corpus is
tiny (tens to low hundreds of motifs), so plain cosine similarity in Python
is both simpler and fast enough. Embeddings are cached on disk and rebuilt
only when the corpus changes.
"""
import hashlib
import json
import math
import os

from .embeddings import embed

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTIFS_PATH = os.path.join(BASE_DIR, "data", "bug_motifs.json")
INDEX_CACHE_PATH = os.path.join(BASE_DIR, "data", "motif_embeddings.json")


def _corpus_hash(motifs: list) -> str:
    raw = json.dumps(motifs, sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _load_motifs() -> list:
    with open(MOTIFS_PATH) as f:
        return json.load(f)


def _motif_text(motif: dict) -> str:
    return (
        f"{motif['category']}: {motif['root_cause']} "
        f"— triggered by {motif['trigger_condition']}. {motif['description']}"
    )


def load_or_build_index() -> tuple:
    """Returns (motifs, embeddings_by_id), rebuilding the embedding cache
    only if the motif corpus has changed since it was last built."""
    motifs = _load_motifs()
    current_hash = _corpus_hash(motifs)

    if os.path.exists(INDEX_CACHE_PATH):
        with open(INDEX_CACHE_PATH) as f:
            cache = json.load(f)
        if cache.get("corpus_hash") == current_hash:
            return motifs, cache["embeddings"]

    embeddings = {m["id"]: embed(_motif_text(m)) for m in motifs}
    with open(INDEX_CACHE_PATH, "w") as f:
        json.dump({"corpus_hash": current_hash, "embeddings": embeddings}, f)
    return motifs, embeddings


def _cosine(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_matches(query_text: str, motifs: list, embeddings: dict, k: int = 2, min_score: float = 0.55) -> list:
    query_vec = embed(query_text)
    motif_by_id = {m["id"]: m for m in motifs}

    scored = []
    for motif_id, vec in embeddings.items():
        score = _cosine(query_vec, vec)
        if score >= min_score:
            scored.append((score, motif_by_id[motif_id]))
    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [{"score": round(score, 3), **motif} for score, motif in scored[:k]]
