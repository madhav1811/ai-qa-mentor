"""Local embedding client via Ollama. No API keys, no network calls beyond
localhost.
"""
import requests

from .llm import LLMError

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
DEFAULT_EMBED_MODEL = "nomic-embed-text"


def embed(text: str, model: str = DEFAULT_EMBED_MODEL) -> list:
    try:
        resp = requests.post(
            OLLAMA_EMBED_URL, json={"model": model, "prompt": text}, timeout=60
        )
    except requests.exceptions.ConnectionError as e:
        raise LLMError(
            "Could not reach Ollama at http://localhost:11434 — is it running? "
            "Start it with: brew services start ollama"
        ) from e
    resp.raise_for_status()
    return resp.json()["embedding"]
