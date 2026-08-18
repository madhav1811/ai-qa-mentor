"""Local, file-based per-tester profile store. Plain JSON on disk — no external
services.
"""
import json
import os

PROFILE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "profiles"
)


def _profile_path(tester: str) -> str:
    os.makedirs(PROFILE_DIR, exist_ok=True)
    safe_name = tester.strip().lower().replace(" ", "_")
    return os.path.join(PROFILE_DIR, f"{safe_name}.json")


def load_profile(tester: str) -> dict:
    path = _profile_path(tester)
    if not os.path.exists(path):
        return {"tester": tester, "sessions": [], "blindspot_counts": {}}
    with open(path) as f:
        return json.load(f)


def save_profile(tester: str, profile: dict) -> None:
    path = _profile_path(tester)
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)
