from typing import Optional


class EducationAdapter:
    def __init__(self, retriever, model):
        self.retriever = retriever
        self.model = model

    def handle(self, message: str, context: dict):
        # Use retrieved evidence passed via context if available
        citations = context.get("evidence", [])
        # Simple safety rule: flag unsafe materials keywords
        unsafe_keywords = ["acid", "explosive", "knife"]
        flagged = any(k.lower() in message.lower() for k in unsafe_keywords)

        # Build lesson plan using model wrapper; include context params if provided
        edu_ctx = {
            "grade": context.get("grade") or context.get("grade_level"),
            "subject": context.get("subject"),
            "duration_minutes": context.get("duration_minutes", 30),
            "language": context.get("language", "sw"),
        }
        reply = self.model.generate_lesson_plan(edu_ctx, citations)
        if flagged:
            reply += "\nTahadhari: Ombi linaweza kuwa na vifaa visivyo salama; tafadhali kagua kabla ya kutekeleza."

        confidence = 0.6
        if citations:
            confidence = max(0.5, min(0.9, max(c.get("score", 0.0) for c in citations)))

        return {
            "reply": reply,
            "confidence": float(confidence),
            "citations": citations,
            "audit": {"action": "generate_lesson_plan", "flagged": flagged},
        }
