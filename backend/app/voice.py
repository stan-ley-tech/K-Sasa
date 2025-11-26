import base64
import os
import uuid
from typing import Optional

from app.audit import write_audit


def _static_dir() -> str:
    path = os.environ.get("K_SASA_STATIC_DIR", "/app/static")
    os.makedirs(path, exist_ok=True)
    return path


def _static_url(filename: str) -> str:
    # In a real deployment put this behind CDN; here we serve via FastAPI StaticFiles at /static
    return f"/static/{filename}"


def transcribe(audio_base64: Optional[str], audio_url: Optional[str], language: str = "sw") -> tuple[str, float]:
    engine = os.environ.get("K_SASA_STT", "stub").lower()
    if engine != "whisper":
        return "(stub) sauti imetambuliwa vizuri", 0.5
    try:
        import whisper  # type: ignore
        import requests  # type: ignore
        import tempfile

        model_name = os.environ.get("K_SASA_WHISPER_MODEL", "base")
        model = whisper.load_model(model_name)
        # prepare temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            if audio_base64:
                data = base64.b64decode(audio_base64)
                tmp.write(data)
            elif audio_url:
                r = requests.get(audio_url)
                r.raise_for_status()
                tmp.write(r.content)
        result = model.transcribe(tmp_path, language=language)
        text = result.get("text", "") or ""
        return text.strip() or "(empty)", 0.7
    except Exception:
        return "(stub) sauti imetambuliwa vizuri", 0.5


def synthesize(text: str, language: str = "sw", voice: Optional[str] = None) -> str:
    engine = os.environ.get("K_SASA_TTS", "stub").lower()
    if engine != "coqui":
        # Write a tiny silent wav as placeholder
        import wave, struct

        filename = f"tts-{uuid.uuid4()}.wav"
        filepath = os.path.join(_static_dir(), filename)
        with wave.open(filepath, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            for _ in range(16000):
                wf.writeframes(struct.pack('<h', 0))
        return _static_url(filename)
    try:
        from TTS.api import TTS  # type: ignore

        model_name = os.environ.get("K_SASA_COQUI_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")
        tts = TTS(model_name)
        filename = f"tts-{uuid.uuid4()}.wav"
        filepath = os.path.join(_static_dir(), filename)
        tts.tts_to_file(text=text, file_path=filepath)
        return _static_url(filename)
    except Exception:
        # fallback to stub file
        return synthesize(text, language, voice=None)
