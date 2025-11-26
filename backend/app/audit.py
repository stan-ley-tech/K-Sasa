import json
import os
from datetime import datetime
from typing import Any, Dict

AUDIT_DIR = os.environ.get("K_SASA_AUDIT_DIR", "/app/audit")
AUDIT_FILE = os.path.join(AUDIT_DIR, "audit.log")


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def write_audit(event: Dict[str, Any]):
    ensure_dir(AUDIT_DIR)
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        **event,
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
