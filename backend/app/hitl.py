import uuid
from typing import Dict, List
from app.audit import write_audit

# Simple in-memory pending actions store for demo
PENDING: Dict[str, Dict] = {}


def enqueue(action_type: str, payload: Dict) -> str:
    pid = f"pa-{uuid.uuid4()}"
    PENDING[pid] = {
        "id": pid,
        "type": action_type,
        "payload": payload,
        "status": "pending",
    }
    write_audit({"event": "hitl.enqueue", "pending_id": pid, "type": action_type})
    return pid


def list_pending() -> List[Dict]:
    return [v for v in PENDING.values() if v.get("status") == "pending"]


def approve(pending_id: str) -> Dict:
    item = PENDING.get(pending_id)
    if not item:
        return {"error": "not_found"}
    item["status"] = "approved"
    write_audit({"event": "hitl.approve", "pending_id": pending_id})
    return item


def decline(pending_id: str, reason: str = "") -> Dict:
    item = PENDING.get(pending_id)
    if not item:
        return {"error": "not_found"}
    item["status"] = "declined"
    item["reason"] = reason
    write_audit({"event": "hitl.decline", "pending_id": pending_id, "reason": reason})
    return item
