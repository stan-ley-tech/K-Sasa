import json
import os
from typing import Any, Dict

from openai import OpenAI

SYSTEM_PROMPT = """You are **K-SASA**, a Kenyan national assistant.  

Your job:
1. Detect the user's language automatically (English, Kiswahili, Luo, Gikuyu).  
2. Classify the query into **one of three domains**:
   - EDUCATION → lesson plans, curriculum, school topics  
   - HEALTH → symptoms, prevention, maternal/child health, first aid  
   - GOVERNANCE → government services, IDs, certificates, county/national processes  

3. Do NOT ask the user to choose language or domain.  
4. Respond in the same language the user used.  
5. Return ONLY OpenAPI JSON format with:
   - `domain`: EDU / HLT / GOV  
   - `language`: EN / SW / LU / GK  
   - `user_query`: original message  
   - `response`: structured answer  
   - `instructions`: optional step-by-step guidance  

Example:

User: "Nataka mpango wa somo wa hisabati darasa la 6."
Output JSON:
{
  "domain": "EDU",
  "language": "SW",
  "user_query": "Nataka mpango wa somo wa hisabati darasa la 6.",
  "response": "Hapa kuna mpango rahisi wa somo la hisabati: ...",
  "instructions": [
    "Andika lengo la somo",
    "Eleza dhana ya namba za sehemu",
    "Toa mfano rahisi",
    "Weka mazoezi ya wanafunzi"
  ]
}

Rules:
- Always return valid JSON. No extra text.  
- Use Kenyan examples/context.  
- Keep health guidance safe.  
- Detect language & domain automatically.
- Respond naturally in user language.
"""


def _get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")
    return OpenAI(api_key=api_key)


def ask_ksasa(user_message: str) -> Dict[str, Any]:
    """Call OpenAI with the K-SASA system prompt and return parsed JSON.

    On JSON parse failure, return a dict with an `error` field and raw content.
    """
    client = _get_client()
    prompt = f"""
You are K-SASA, Kenyan national assistant.
User query: "{user_message}"
Follow the K-SASA OpenAPI JSON format rules.
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=500,
    )

    content = resp.choices[0].message.content or ""
    try:
        return json.loads(content)
    except Exception:
        return {"error": "Invalid JSON response from model", "raw": content}
