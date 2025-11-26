class GovernanceAdapter:
    def __init__(self, retriever):
        self.retriever = retriever

    def handle(self, message: str, context: dict):
        citations = context.get("evidence", [])
        form = context.get("form") or {}

        required = [
            "business_name",
            "owner_name",
            "id_number",
            "business_type",
            "address",
            "contact",
            "docs_required",
        ]
        missing = [k for k in required if not form.get(k)]

        if missing:
            prompt_qs = ", ".join(missing)
            reply = (
                "[governance] Tafadhali toa taarifa zifuatazo: " + prompt_qs + ". "
                "Tuma kama JSON 'form' katika ombi linalofuata, au andika majibu yako moja kwa moja."
            )
            confidence = 0.6
            if citations:
                confidence = max(0.5, min(0.9, max(c.get("score", 0.0) for c in citations)))
            return {
                "reply": reply,
                "confidence": float(confidence),
                "citations": citations,
                "audit": {"action": "form_fill", "missing": missing},
            }

        reply = (
            "[governance] Fomu imekamilika. Tumia hatua: 'submit_form_preview' kupata faili ya hakikisho, kisha 'submit_form_confirm' kuwasilisha (hitaji HITL)."
        )
        confidence = 0.7
        if citations:
            confidence = max(confidence, min(0.9, max(c.get("score", 0.0) for c in citations)))
        return {
            "reply": reply,
            "confidence": float(confidence),
            "citations": citations,
            "audit": {"action": "form_ready", "missing": []},
        }
