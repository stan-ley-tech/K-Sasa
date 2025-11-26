from typing import Dict

class AgentOrchestrator:
    def __init__(self):
        self.adapters: Dict[str, object] = {}

    def register(self, name: str, adapter: object):
        self.adapters[name] = adapter

    def route(self, domain: str):
        return self.adapters.get(domain)

    def handle(self, domain: str, message: str, context: Dict):
        adapter = self.route(domain)
        if not adapter:
            return {
                "reply": f"Unsupported domain: {domain}",
                "confidence": 0.0,
                "citations": [],
                "audit": {"domain": domain, "status": "unsupported"},
            }
        return adapter.handle(message, context)
