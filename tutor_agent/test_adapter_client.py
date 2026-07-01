"""End-to-end test of the XiaoZhi voice adapter WITHOUT the device.

Speaks an utterance (OpenAI TTS -> 16 kHz Opus uplink), sends it over the WS protocol exactly
like stackchan-idf would, then decodes the Opus reply and transcribes it to prove the full
chain works: uplink Opus -> STT -> dialog -> TTS -> downlink Opus.
"""
import array
import asyncio
import io
import json
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import websockets
import opuslib_next
from tutor_agent import providers

APP = getattr(opuslib_next, "APPLICATION_VOIP", 2048)
URL = "ws://127.0.0.1:8000/xiaozhi/v1/"


def resample_24k_to_16k(pcm24):
    a = array.array("h"); a.frombytes(pcm24)
    n = len(a); m = n * 16000 // 24000
    out = array.array("h", bytes(2 * m))
    for i in range(m):
        pos = i * 1.5; j = int(pos); frac = pos - j
        s0 = a[j] if j < n else 0
        s1 = a[j + 1] if j + 1 < n else s0
        out[i] = int(s0 + (s1 - s0) * frac)
    return out.tobytes()


def pcm_to_wav(pcm, rate):
    buf = io.BytesIO()
    w = wave.open(buf, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
    w.writeframes(pcm); w.close()
    return buf.getvalue()


async def run():
    print("synthesizing uplink speech 'Give me a question.' ...")
    pcm16 = resample_24k_to_16k(providers.tts_pcm("Give me a question."))
    enc = opuslib_next.Encoder(16000, 1, APP)
    dec = opuslib_next.Decoder(24000, 1)
    FR = 960 * 2
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps({"type": "hello",
            "audio_params": {"format": "opus", "sample_rate": 16000, "frame_duration": 60}}))
        print("server hello:", json.loads(await asyncio.wait_for(ws.recv(), 10)))
        for i in range(0, len(pcm16) - FR + 1, FR):          # speech frames
            await ws.send(enc.encode(pcm16[i:i + FR], 960))
        for _ in range(15):                                   # ~900 ms trailing silence -> VAD end
            await ws.send(enc.encode(b"\x00" * FR, 960))
        reply = bytearray()
        while True:
            msg = await asyncio.wait_for(ws.recv(), 30)
            if isinstance(msg, str):
                d = json.loads(msg)
                tag = d.get("text") or d.get("state") or d.get("emotion") or ""
                print(f"  <- {d.get('type'):5} {tag[:70]}")
                if d.get("type") == "tts" and d.get("state") == "stop":
                    break
            else:
                reply += dec.decode(msg, 1440)
    print(f"\ndownlink audio: {len(reply)//2} samples @24k")
    print("reply transcribes back to:", repr((providers.stt(pcm_to_wav(reply, 24000)) or "")[:160]))


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(run(), 120))
