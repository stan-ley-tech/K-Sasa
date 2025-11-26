import json
import sys
import time
import requests

BASE = "http://localhost:8000"

PASS = 0
FAIL = 0
CASES = []

def case(name, ok, info=None):
    global PASS, FAIL
    if ok:
        PASS += 1
    else:
        FAIL += 1
    CASES.append({"name": name, "ok": ok, "info": info})


def strong_citation(citations, thr=0.3):
    return any((c.get("score", 0.0) or 0.0) >= thr for c in (citations or []))


def test_education():
    prompts = [
        ("Hisabati", 4),
        ("Sayansi", 5),
        ("Lugha", 3),
        ("Jiografia", 6),
        ("Historia", 7),
        ("Sanaa", 2),
        ("Teknolojia", 8),
        ("Michezo", 5),
        ("Muziki", 4),
        ("Kilimo", 6),
    ]
    for i, (subject, grade) in enumerate(prompts, 1):
        body = {
            "user_id": f"edu{i}",
            "channel": "tests",
            "domain": "education",
            "prompt": f"Tengeneza mpango wa somo wa {subject} kwa darasa la {grade}.",
            "context": {"grade": grade, "subject": subject, "duration_minutes": 30, "language": "sw"},
        }
        r = requests.post(f"{BASE}/agent/ask", json=body, timeout=60)
        ok = r.status_code == 200
        if not ok:
            case(f"education_{i}", False, f"http {r.status_code}")
            continue
        data = r.json()
        text = data.get("reply", "")
        cites = data.get("citations", [])
        heur = (
            ("Dakika" in text) and ("Malengo" in text or "Malengo ya Kujifunza" in text) and ("Tathmini" in text)
        )
        guard_ok = strong_citation(cites) or text.startswith("I could not find a local source")
        case(f"education_{i}", bool(heur and guard_ok), {"confidence": data.get("confidence"), "cites": len(cites)})


def test_health():
    for i in range(1, 11):
        urgent = (i % 2 == 0)
        visit = "Homa ndogo na kikohozi; Temp 38.0C; maumivu ya koo kwa siku 3."
        body = {
            "user_id": f"health{i}",
            "channel": "tests",
            "domain": "health",
            "prompt": "Muhtasari wa ziara ya kliniki",
            "context": {
                "visit_notes_text": visit,
                "language": "sw",
                "patient_age": 10 + i,
                "urgent_flag": urgent,
            },
        }
        r = requests.post(f"{BASE}/agent/ask", json=body, timeout=60)
        ok = r.status_code == 200
        if not ok:
            case(f"health_{i}", False, f"http {r.status_code}")
            continue
        data = r.json()
        text = data.get("reply", "")
        heur = ("Muhtasari" in text) and ("Maelekezo ya baada ya huduma" in text)
        if urgent:
            heur = heur and ("Inahitaji ukaguzi" in text)
        case(f"health_{i}", bool(heur), {"confidence": data.get("confidence")})


def test_governance():
    # Step 1: ask with missing fields
    body = {
        "user_id": "gov1",
        "channel": "tests",
        "domain": "governance",
        "prompt": "Nataka kusajili biashara",
        "context": {"form": {"business_name": "Maua Store", "owner_name": "Juma K", "id_number": "12345678"}},
    }
    r1 = requests.post(f"{BASE}/agent/ask", json=body, timeout=60)
    ok1 = r1.status_code == 200 and "Tafadhali toa taarifa" in r1.text
    case("governance_missing_prompt", ok1)

    # Step 2: provide full form and preview
    full_form = {
        "business_name": "Maua Store",
        "owner_name": "Juma K",
        "id_number": "12345678",
        "business_type": "Retail",
        "address": "Nairobi CBD",
        "contact": "+254700000000",
        "docs_required": "ID copy",
    }
    body2 = {**body, "context": {"form": full_form}}
    r2 = requests.post(f"{BASE}/agent/ask", json=body2, timeout=60)
    ok2 = r2.status_code == 200 and "Fomu imekamilika" in r2.text
    case("governance_ready", ok2)

    # Action: preview JSON
    resp2 = r2.json()
    audit_id = resp2.get("audit_id")
    act = {"audit_id": audit_id, "action": "submit_form_preview", "payload": {"form": full_form}}
    r3 = requests.post(f"{BASE}/agent/action", json=act, timeout=60)
    ok3 = r3.status_code == 200 and r3.json().get("preview_url")
    case("governance_preview", bool(ok3))

    # Fetch preview JSON
    if ok3:
        url = r3.json().get("preview_url")
        r4 = requests.get(f"{BASE}{url}", timeout=60)
        ok4 = r4.status_code == 200
        try:
            j = r4.json()
            ok4 = ok4 and ("form" in j) and all(k in j["form"] for k in full_form.keys())
        except Exception:
            ok4 = False
        case("governance_fetch_preview", ok4)


def main():
    print("Running K-Sasa tests ...")
    test_education()
    test_health()
    test_governance()
    total = PASS + FAIL
    print(json.dumps({"total": total, "pass": PASS, "fail": FAIL, "cases": CASES}, ensure_ascii=False, indent=2))
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
