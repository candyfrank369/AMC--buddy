"""Pluggable STT / TTS for the StackChan API — standard library only (urllib).

No OPENAI_API_KEY  -> TEXT-STUB mode: stt() echoes a placeholder, tts() returns "" so the JSON
loop is fully testable today with {"text": ...}. Set OPENAI_API_KEY to switch on real speech;
recommended models below are cheap and English-strong. Audio formats get finalised against the
device when we wire Phase 2 (device sends 16 kHz mono PCM/WAV; tts returns mp3 base64).
"""
import base64
import json
import os
import urllib.request

_KEY = os.environ.get("OPENAI_API_KEY")
STT_MODEL = os.environ.get("STT_MODEL", "gpt-4o-mini-transcribe")
TTS_MODEL = os.environ.get("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.environ.get("TTS_VOICE", "alloy")


def mode():
    return "openai" if _KEY else "text-stub (set OPENAI_API_KEY to enable speech)"


def stt(audio_bytes):
    """Speech -> text. Stub until a key is set."""
    if not _KEY or not audio_bytes:
        return "(text-stub: device audio not transcribed yet)"
    # multipart/form-data upload to OpenAI transcriptions (verified live when we enable the key)
    boundary = "----amcbuddy"
    head_model = f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\n{STT_MODEL}\r\n'.encode()
    head_file = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\n'
                 f"Content-Type: audio/wav\r\n\r\n").encode()
    tail = f"--{boundary}--\r\n".encode()
    body = head_model + head_file + audio_bytes + b"\r\n" + tail
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/transcriptions", data=body,
        headers={"Authorization": f"Bearer {_KEY}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("text", "")


def tts(text):
    """Text -> base64 mp3. Returns '' in stub mode (device just shows the expression / text)."""
    if not _KEY or not text:
        return ""
    payload = json.dumps({"model": TTS_MODEL, "voice": TTS_VOICE, "input": text,
                          "response_format": "mp3"}).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech", data=payload,
        headers={"Authorization": f"Bearer {_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return base64.b64encode(r.read()).decode()
