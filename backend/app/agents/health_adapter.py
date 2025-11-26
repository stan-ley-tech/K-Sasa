class HealthAdapter:
    def __init__(self, retriever):
        self.retriever = retriever

    def handle(self, message: str, context: dict):
        citations = context.get("evidence", [])
        # Extract schema fields
        visit_notes = context.get("visit_notes_text") or message
        language = (context.get("language") or "sw").lower()
        age = context.get("patient_age")
        urgent = bool(context.get("urgent_flag", False))

        clinic_summary = "Muhtasari: " + (visit_notes[:300] + ("..." if len(visit_notes) > 300 else ""))
        aftercare = (
            "Maelekezo ya baada ya huduma: Pumzika, kunywa maji ya kutosha, tumia dawa kama ulivyoelekezwa (mf. paracetamol kulingana na dozi sahihi), na rudi kliniki ukizidiwa au dalili zikiongezeka."
        )
        triage = "Mapendekezo ya triage: Fuata hali; rudi haraka ikiwa upumuaji unakuwa mgumu, homa kali >38.5C, maumivu makali, au kutapika kupita kiasi. (Hakuna utambuzi; taarifa ya jumla tu)"

        human_review = urgent is True

        reply = (
            "[health]\n" + clinic_summary + "\n\n" + aftercare + "\n\n" + triage + ("\n\nTahadhari: Inahitaji ukaguzi wa binadamu." if human_review else "")
        )

        confidence = 0.6
        if citations:
            confidence = max(0.5, min(0.9, max(c.get("score", 0.0) for c in citations)))

        return {
            "reply": reply,
            "confidence": float(confidence),
            "citations": citations,
            "audit": {
                "action": "summarize_and_aftercare",
                "human_review": human_review,
                "urgent": urgent,
            },
        }
