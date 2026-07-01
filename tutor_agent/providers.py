"""STT / TTS via OpenAI (reliable, verified). The LLM brain is on OpenRouter (brain_llm.py).

Two keys, each best at its job: OpenRouter's audio endpoints were tried (2026-06-25) but no
working TTS model id was reachable (all 400 'does not exist'), so audio stays on OpenAI, which
works. If OpenRouter audio matures later, only this file changes.

  STT  multipart POST /v1/audio/transcriptions   (gpt-4o-mini-transcribe; auto-detects zh/en)
  TTS  JSON POST      /v1/audio/speech            (gpt-4o-mini-tts; pcm 24 kHz / wav)
Standard library only (urllib). No key -> text-stub mode (tone / placeholder) for offline tests.
"""
import io
import json
import math
import os
import struct
import urllib.request
import wave

_KEY = os.environ.get("OPENAI_API_KEY")
STT_MODEL = os.environ.get("STT_MODEL", "gpt-4o-mini-transcribe")
TTS_MODEL = os.environ.get("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.environ.get("TTS_VOICE", "alloy")
TTS_MIME = "audio/wav"          # device plays WAV via I2S (no decoder); downlink PCM is 24 kHz


def mode():
    return "openai" if _KEY else "text-stub (set OPENAI_API_KEY to enable speech)"


def _pcm_to_wav(pcm, rate=24000):
    buf = io.BytesIO()
    w = wave.open(buf, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
    w.writeframes(pcm); w.close()
    return buf.getvalue()


def _tone_pcm(ms=350, freq=440, rate=24000):
    n = int(rate * ms / 1000)
    return b"".join(struct.pack("<h", int(2500 * math.sin(2 * math.pi * freq * i / rate))) for i in range(n))


def stt(audio_bytes):
    """WAV bytes -> transcript (Whisper auto-detects Chinese/English)."""
    if not _KEY or not audio_bytes:
        return "(text-stub: device audio not transcribed yet)"
    boundary = "----amcbuddy"
    head_model = f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\n{STT_MODEL}\r\n'.encode()
    head_file = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.wav"\r\n'
                 f"Content-Type: audio/wav\r\n\r\n").encode()
    tail = f"--{boundary}--\r\n".encode()
    body = head_model + head_file + audio_bytes + b"\r\n" + tail
    req = urllib.request.Request("https://api.openai.com/v1/audio/transcriptions", data=body,
        headers={"Authorization": f"Bearer {_KEY}",
                 "Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r).get("text", "")


def tts_pcm(text):
    """Text -> raw PCM16 mono @24 kHz (for Opus encoding). Stub = tone."""
    if not _KEY or not text:
        return _tone_pcm()
    payload = json.dumps({"model": TTS_MODEL, "voice": TTS_VOICE,
                          "input": text, "response_format": "pcm"}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=payload,
        headers={"Authorization": f"Bearer {_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def tts(text):
    """Text -> WAV bytes (24 kHz). Stub = short tone WAV."""
    if not _KEY or not text:
        return _pcm_to_wav(_tone_pcm())
    return _pcm_to_wav(tts_pcm(text))
