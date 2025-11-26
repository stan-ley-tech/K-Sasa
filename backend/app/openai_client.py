import json
import os
from typing import Any, Dict

import openai

SYSTEM_PROMPT = """You are **K-SASA**, a Kenyan national assistant.  
... (keep the full prompt exactly as it is) ...
"""


def _openai_model() -> str:
    """Return the OpenAI chat model name.

    Defaults to gpt-4o-mini but can be overridden with OPENAI_MODEL.
    """
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def ask_ksasa(user_message: str) -> Dict[str, Any]:
    """Call OpenAI Chat Completions with the K-SASA system prompt.

    Returns a dict with at least:
      - response: main answer text
      - instructions: optional list of follow-up instructions/steps

    On failure, returns a dict with an `error` field.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY is not set"}

    openai.api_key = api_key

    prompt = f"""
You are K-SASA, Kenyan national assistant.
User query: "{user_message}"
Follow the K-SASA OpenAPI JSON format rules.
"""

    try:
        completion = openai.ChatCompletion.create(
            model=_openai_model(),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
    except Exception as exc:
        return {"error": f"OpenAI request failed: {exc}"}

    try:
        content = completion["choices"][0]["message"]["content"]
    except Exception:
        return {"error": "Invalid response format from OpenAI", "raw": completion}

    # Try to parse structured JSON; if that fails, return plain text
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            # Ensure keys expected by /agent/ask exist at least as empty defaults
            if "response" not in data:
                data["response"] = ""
            if "instructions" not in data:
                data["instructions"] = []
            return data
    except Exception:
        pass

    return {"response": content, "instructions": []}