from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from app.agents.orchestrator import AgentOrchestrator
from app.agents.education_adapter import EducationAdapter
from app.agents.health_adapter import HealthAdapter
from app.agents.governance_adapter import GovernanceAdapter
from app.rag import SimpleRetriever, format_citations
from app.audit import write_audit
from app.hitl import enqueue, list_pending, approve, decline
import os
from app.model import ModelWrapper
from app.voice import transcribe, synthesize
from app.openai_client import ask_ksasa
import time
from app.telemetry import log_event, prompt_hash, record_request, snapshot_metrics

app = FastAPI(title="K-Sasa Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "K-Sasa API Running"}

    domain: Optional[str] = None  # education | health | governance


class Citation(BaseModel):
    source: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    reply: str
    confidence: float
    citations: List[Citation]
    audit_id: str


class ChatRequest(BaseModel):
    user_id: str
    channel: str
    domain: Optional[str] = None
    message: str


class STTRequest(BaseModel):
    # For demo, accept base64 audio or URL; both optional for stub
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    language: Optional[str] = "sw"


class STTResponse(BaseModel):
    transcript: str
    confidence: float
    audit_id: str


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    language: Optional[str] = "sw"


class TTSResponse(BaseModel):
    audio_url: str
    audit_id: str


class AgentAskRequest(BaseModel):
    user_id: str
    channel: str
    domain: str
    prompt: str
    context: Optional[dict] = None


class AgentActionRequest(BaseModel):
    audit_id: str
    action: str  # confirm | decline | execute
    payload: Optional[dict] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    audit_id = f"audit-{uuid4()}"
    domain = (req.domain or "").lower() if req.domain else ""
    context = {"channel": req.channel, "user_id": req.user_id, "audit_id": audit_id}
    result = orchestrator.handle(domain=domain, message=req.message, context=context)
    cits = [Citation(**c) for c in result.get("citations", [])]
    return ChatResponse(
        reply=result.get("reply", ""),
        confidence=float(result.get("confidence", 0.0)),
        citations=cits,
        audit_id=audit_id,
    )


@app.post("/agent/ask", response_model=ChatResponse)
def agent_ask(req: AgentAskRequest):
    audit_id = f"audit-{uuid4()}"
    data = ask_ksasa(req.prompt)

    # Defaults
    reply_text = ""
    conf = 1.0
    citations: list[dict] = []

    if "error" in data:
        reply_text = f"OpenAI error: {data['error']}"
    else:
        resp = data.get("response", "")
        instructions = data.get("instructions") or []
        if isinstance(instructions, list) and instructions:
            steps = "\n".join(f"- {step}" for step in instructions)
            reply_text = f"{resp}\n\nSteps:\n{steps}"
        else:
            reply_text = str(resp)

    return ChatResponse(
        reply=reply_text,
        confidence=conf,
        citations=[Citation(**c) for c in citations],
        audit_id=audit_id,
    )


@app.post("/agent/action")
def agent_action(req: AgentActionRequest):
    payload = req.payload or {}
    # Route governance actions
    if req.action == "submit_form_preview":
        # Write JSON preview to static and return URL
        form = payload.get("form") or {}
        fname = f"form-preview-{uuid4()}.json"
        path = os.path.join(static_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            import json
            json.dump({"form": form, "audit_id": req.audit_id}, f, ensure_ascii=False, indent=2)
        url = f"/static/{fname}"
        write_audit({
            "audit_id": req.audit_id,
            "event": "agent.action",
            "action": req.action,
            "preview_url": url,
        })
        return {"status": "ok", "audit_id": req.audit_id, "preview_url": url}

    if req.action == "submit_form_confirm":
        pending_id = enqueue("submit_form_confirm", {"audit_id": req.audit_id, **payload})
        write_audit({
            "audit_id": req.audit_id,
            "event": "agent.action",
            "action": req.action,
            "pending_id": pending_id,
        })
        return {"status": "pending_review", "audit_id": req.audit_id, "pending_id": pending_id}

    if req.action == "triage_recommendation":
        # Enqueue for review (info-only), not a medical diagnosis
        pending_id = enqueue("triage_recommendation", {"audit_id": req.audit_id, **payload})
        write_audit({
            "audit_id": req.audit_id,
            "event": "agent.action",
            "action": req.action,
            "pending_id": pending_id,
        })
        return {"status": "pending_review", "audit_id": req.audit_id, "pending_id": pending_id}

    # Default: log only
    write_audit({
        "audit_id": req.audit_id,
        "event": "agent.action",
        "action": req.action,
        "payload": payload,
    })
    return {"status": "ok", "audit_id": req.audit_id}


@app.get("/admin/pending")
def admin_pending():
    return {"items": list_pending()}


class ReviewRequest(BaseModel):
    pending_id: str
    reason: Optional[str] = None


@app.post("/admin/approve")
def admin_approve(req: ReviewRequest):
    return approve(req.pending_id)


@app.post("/admin/decline")
def admin_decline(req: ReviewRequest):
    return decline(req.pending_id, req.reason or "")


@app.post("/voice/stt", response_model=STTResponse)
def voice_stt(req: STTRequest):
    audit_id = f"audit-{uuid4()}"
    transcript, conf = transcribe(req.audio_base64, req.audio_url, req.language or "sw")
    write_audit({
        "audit_id": audit_id,
        "event": "voice.stt",
        "language": req.language,
    })
    return STTResponse(transcript=transcript, confidence=float(conf), audit_id=audit_id)


@app.post("/voice/tts", response_model=TTSResponse)
def voice_tts(req: TTSRequest):
    audit_id = f"audit-{uuid4()}"
    audio_url = synthesize(req.text, req.language or "sw", req.voice)
    write_audit({
        "audit_id": audit_id,
        "event": "voice.tts",
        "language": req.language,
        "voice": req.voice or "default",
    })
    return TTSResponse(audio_url=audio_url, audit_id=audit_id)


class STTToAgentRequest(BaseModel):
    user_id: str
    channel: str
    domain: str
    language: Optional[str] = "sw"
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    context: Optional[dict] = None


@app.post("/voice/stt_to_agent", response_model=ChatResponse)
def voice_stt_to_agent(req: STTToAgentRequest):
    transcript, _ = transcribe(req.audio_base64, req.audio_url, req.language or "sw")
    # Reuse agent_ask flow
    ask = AgentAskRequest(
        user_id=req.user_id,
        channel=req.channel,
        domain=req.domain,
        prompt=transcript,
        context=req.context or {"language": req.language},
    )
    return agent_ask(ask)


class SMSInboundRequest(BaseModel):
    from_number: str
    to_number: Optional[str] = None
    text: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    domain: Optional[str] = None


@app.post("/sms/inbound")
def sms_inbound(req: SMSInboundRequest):
    user_id = req.user_id or req.from_number
    domain = (req.domain or "education")
    ask = AgentAskRequest(
        user_id=user_id,
        channel="sms",
        domain=domain,
        prompt=req.text,
        context={"session_id": req.session_id},
    )
    resp = agent_ask(ask)
    return resp


@app.post("/generate")
async def generate(payload: dict):
    text = payload["text"]
    output = kiswahili_translate(text)
    return {"output": output}


@app.get("/metrics")
def metrics():
    return snapshot_metrics()


orchestrator = AgentOrchestrator()
retriever = SimpleRetriever()
# shared lightweight model wrapper (placeholder)
model = ModelWrapper()
# Attempt to build from project seed data
seed_dir = os.environ.get(
    "K_SASA_SEED_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "seed")),
)
retriever.build_from_seed(seed_dir)

orchestrator.register("education", EducationAdapter(retriever, model))
orchestrator.register("health", HealthAdapter(retriever))
orchestrator.register("governance", GovernanceAdapter(retriever))
