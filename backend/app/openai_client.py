import json
import os
from typing import Any, Dict

import openai  # <-- change here

SYSTEM_PROMPT = """You are **K-SASA**, a Kenyan national assistant.  
... (keep the full prompt exactly as it is) ...
"""

def _init_client() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")
    openai.api_key = api_key  # <-- set key on module

def ask_ksasa(user_message: str) -> Dict[str, Any]:
    """Call OpenAI with the K-SASA system prompt and return parsed JSON.

    On JSON parse failure, return a dict with an `error` field and raw content.
    """
    _init_client()

    prompt = f"""
You are K-SASA, Kenyan national assistant.
User query: "{user_message}"
Follow the K-SASA OpenAPI JSON format rules.
"""

    resp = openai.ChatCompletion.create(  
        model="gpt-3.5-turbo",            
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    content = resp["choices"][0]["message"]["content"] or ""
    try:
        return json.loads(content)
    except Exception:
        return {"error": "Invalid JSON response from model", "raw": content}