import json
import os
from typing import Any, Dict

import requests

SYSTEM_PROMPT = """You are **K-SASA**, a Kenyan national assistant.  
... (keep the full prompt exactly as it is) ...
"""


def _ollama_base_url() -> str:
    """Return the Ollama base URL.

    Defaults to http://localhost:11434 but can be overridden with OLLAMA_BASE_URL.
    """
    return os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


def ask_ksasa(user_message: str) -> Dict[str, Any]:
    """Call Ollama (LLaMA 3.1 8B) with the K-SASA system prompt and return parsed JSON.

    On JSON parse failure, return a dict with an `error` field and raw content.
    """
    prompt = f"""
You are K-SASA, Kenyan national assistant.
User query: "{user_message}"
Follow the K-SASA OpenAPI JSON format rules.
"""

    url = f"{_ollama_base_url().rstrip('/')}/api/chat"
    payload: Dict[str, Any] = {
        "model": os.environ.get("OLLAMA_MODEL", "llama3.2:latest"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=60)
    except Exception as exc:  # network / connection error
        return {"error": f"Ollama request failed: {exc}"}

    if resp.status_code != 200:
        return {"error": f"Ollama HTTP {resp.status_code}: {resp.text}"}

    try:
        data = resp.json()
    except Exception as exc:
        return {"error": f"Invalid JSON from Ollama: {exc}", "raw": resp.text}

    # Expected Ollama chat format: { "message": {"content": "..."}, ... }
    content = ""
    try:
        content = (data.get("message") or {}).get("content") or ""
    except Exception:
        content = ""

    if not content:
        return {"error": "Empty response from Ollama", "raw": data}

    # Try to parse structured JSON; if that fails, fall back to returning raw text
    try:
        return json.loads(content)
    except Exception:
        return {"text": content}
