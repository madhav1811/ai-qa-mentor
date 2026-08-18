"""Thin client for a locally-running Ollama model. No API keys, no network calls
beyond localhost.
"""
import json

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen2.5:7b-instruct"


class LLMError(RuntimeError):
    pass


def _post(system_prompt, user_prompt, model, extra, timeout):
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {"temperature": 0.2},
                **extra,
            },
            timeout=timeout,
        )
    except requests.exceptions.ConnectionError as e:
        raise LLMError(
            "Could not reach Ollama at http://localhost:11434 — is it running? "
            "Start it with: brew services start ollama"
        ) from e
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def chat_json(system_prompt, user_prompt, model=DEFAULT_MODEL, timeout=300):
    """Call the local model and parse its reply as JSON."""
    content = _post(system_prompt, user_prompt, model, {"format": "json"}, timeout)
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise LLMError(
            f"Model did not return valid JSON: {e}\nRaw output:\n{content[:1000]}"
        ) from e


def chat_text(system_prompt, user_prompt, model=DEFAULT_MODEL, timeout=300):
    """Call the local model and return its raw text reply."""
    return _post(system_prompt, user_prompt, model, {}, timeout)
