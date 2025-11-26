# Adapter Schemas (Draft)

- education.handle(message, context) -> { reply, confidence, citations[], audit }
- health.handle(message, context) -> { reply, confidence, citations[], audit }
- governance.handle(message, context) -> { reply, confidence, citations[], audit }

Citations item: { source: str, snippet: str, score: float }
