"""voice_adapter_xiaozhi.py — the ONLY module that knows the XiaoZhi WS protocol.

Boundary (per the agreed architecture):
    StackChan  --xiaozhi WS(Opus)-->  THIS ADAPTER  -->  tutor_agent core (dialog + engine)
The teaching engine (tutor/*, dialog) never imports or mentions xiaozhi. Swap this file for a
different transport (or the pure 2b was this) and the brain is untouched.

Pipeline per turn:
    device Opus(16k) --decode--> PCM16 --energy VAD--> utterance
      --> OpenAI STT --> dialog.handle() --> reply text + expression
      --> OpenAI TTS(PCM 24k) --encode--> Opus(24k) --> device;  + stt/llm/tts control JSON

Protocol (reverse-engineered from ciniml/stackchan-idf xiaozhi_client):
  text WS frame = JSON control, binary WS frame = one Opus packet.
  server hello must carry session_id + audio_params.sample_rate (our downlink rate).
  we send: stt{text} · llm{emotion} · tts{state:start|sentence_start(text)|stop}.

Run (needs libopus on the dylib path + OPENAI_API_KEY):
  DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib \
  ./.venv/bin/python -m tutor_agent.voice_adapter_xiaozhi
"""
import array
import asyncio
import io
import json
import os
import sys
import uuid
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import websockets
import opuslib_next
from tutor_agent import dialog, providers

UP_RATE, UP_FRAME = 16000, 960      # device mic: Opus 16 kHz, 60 ms = 960 samples
DN_RATE, DN_FRAME = 24000, 1440     # our TTS: 24 kHz, 60 ms = 1440 samples (matches OpenAI pcm)
_APP_VOIP = getattr(opuslib_next, "APPLICATION_VOIP", 2048)

# energy VAD (server-side turn detection, no torch)
START_RMS, END_RMS = 600, 400
SILENCE_MS, MIN_SPEECH_MS, MAX_UTT_MS = 700, 300, 15000
FRAME_MS = 60
EMO = {"neutral": "neutral", "thinking": "thinking", "talking": "neutral",
       "happy": "happy", "encouraging": "happy"}


def _rms(pcm):
    a = array.array("h"); a.frombytes(pcm)
    return (sum(x * x for x in a) / len(a)) ** 0.5 if len(a) else 0.0


def _pcm_to_wav(pcm, rate):
    buf = io.BytesIO()
    w = wave.open(buf, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
    w.writeframes(pcm); w.close()
    return buf.getvalue()


async def _run(fn, *a):
    return await asyncio.get_event_loop().run_in_executor(None, fn, *a)


async def _process_turn(ws, sid, pcm16):
    text = (await _run(providers.stt, _pcm_to_wav(pcm16, UP_RATE))) or ""
    if not text.strip() or text.startswith("(text-stub"):
        return
    r = dialog.handle("frank", text)
    await ws.send(json.dumps({"type": "stt", "text": text, "session_id": sid}))
    await ws.send(json.dumps({"type": "llm", "emotion": EMO.get(r["expression"], "neutral"), "session_id": sid}))
    await ws.send(json.dumps({"type": "tts", "state": "start", "session_id": sid}))
    await ws.send(json.dumps({"type": "tts", "state": "sentence_start", "text": r["say"], "session_id": sid}))
    pcm24 = await _run(providers.tts_pcm, r["say"])
    enc = opuslib_next.Encoder(DN_RATE, 1, _APP_VOIP)
    step = DN_FRAME * 2
    for i in range(0, len(pcm24), step):
        frame = pcm24[i:i + step]
        if len(frame) < step:
            frame = frame + b"\x00" * (step - len(frame))
        await ws.send(enc.encode(frame, DN_FRAME))          # binary Opus packet
    await ws.send(json.dumps({"type": "tts", "state": "stop", "session_id": sid}))
    print(f"[turn] heard={text!r} -> say={r['say'][:60]!r} ({len(pcm24)//2} pcm samples)")


async def handle(ws):
    sid = uuid.uuid4().hex[:8]
    path = getattr(getattr(ws, "request", None), "path", "?")
    print(f"[conn] {path} session={sid}")
    dec = opuslib_next.Decoder(UP_RATE, 1)
    buf, in_speech, silence_ms, speech_ms = bytearray(), False, 0, 0
    try:
        async for msg in ws:
            if isinstance(msg, str):                        # JSON control
                t = json.loads(msg or "{}").get("type")
                if t == "hello":
                    await ws.send(json.dumps({"type": "hello", "transport": "websocket",
                        "session_id": sid,
                        "audio_params": {"format": "opus", "sample_rate": DN_RATE, "frame_duration": 60, "channels": 1}}))
                elif t == "abort":
                    buf, in_speech, silence_ms, speech_ms = bytearray(), False, 0, 0
                continue
            # binary = one Opus packet from the mic
            try:
                pcm = dec.decode(msg, UP_FRAME)
            except Exception:
                continue
            level = _rms(pcm)
            if level > START_RMS:
                in_speech = True
            if in_speech:
                buf += pcm; speech_ms += FRAME_MS
                silence_ms = silence_ms + FRAME_MS if level < END_RMS else 0
                end = silence_ms >= SILENCE_MS or speech_ms >= MAX_UTT_MS
                if end:
                    if speech_ms - silence_ms >= MIN_SPEECH_MS:
                        await _process_turn(ws, sid, bytes(buf))
                    buf, in_speech, silence_ms, speech_ms = bytearray(), False, 0, 0
    except websockets.ConnectionClosed:
        pass
    print(f"[disc] session={sid}")


async def main():
    port = int(os.environ.get("PORT", "8000"))
    print(f"XiaoZhi voice adapter -> tutor_agent core  |  ws://0.0.0.0:{port}/xiaozhi/v1/  "
          f"(STT/TTS: {providers.mode()})")
    async with websockets.serve(handle, "0.0.0.0", port, max_size=None):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
