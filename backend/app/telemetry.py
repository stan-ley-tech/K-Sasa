import hashlib
import json
import os
import threading
import time
from typing import Any, Dict

TELEMETRY_DIR = os.environ.get("K_SASA_AUDIT_DIR", "/app/audit")
TELEMETRY_FILE = os.path.join(TELEMETRY_DIR, "telemetry.log")
lock = threading.Lock()

# Simple in-memory metrics
METRICS = {
    "total_requests": 0,
    "success_requests": 0,
    "total_latency_ms": 0.0,
}


def prompt_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def log_event(event: Dict[str, Any]):
    os.makedirs(TELEMETRY_DIR, exist_ok=True)
    with lock:
        with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")


def record_request(latency_ms: float, success: bool):
    with lock:
        METRICS["total_requests"] += 1
        METRICS["total_latency_ms"] += float(latency_ms)
        if success:
            METRICS["success_requests"] += 1


def snapshot_metrics() -> Dict[str, Any]:
    with lock:
        total = METRICS["total_requests"]
        avg_latency = (METRICS["total_latency_ms"] / total) if total > 0 else 0.0
        completion_rate = (
            (METRICS["success_requests"] / total) if total > 0 else 0.0
        )
        return {
            "total_requests": total,
            "average_latency_ms": round(avg_latency, 2),
            "task_completion_rate": round(completion_rate, 4),
        }
