"""AMC-buddy thin-client HTTP API (for StackChan).

Standard-library only (no Docker, no pip, no framework) — matches the engine's philosophy and
runs on the Mac as-is. The StackChan is a dumb client: it sends voice/answers and plays back
audio + shows an expression. All tutoring logic + STT/TTS live here.

Endpoints
  GET  /health
  GET  /api/stackchan/next-task?topic=route|cube      -> a verified question to pose
  POST /api/stackchan/answer   {task_id, answer}       -> marked + spoken feedback + expression
  POST /api/stackchan/voice    {text} | <audio bytes>  -> (STT ->) tutor reply (-> TTS) + expression

STT/TTS are pluggable (providers.py). With no OpenAI key set they run in TEXT-STUB mode so the
whole loop is testable today; set OPENAI_API_KEY to switch on real speech.

Run:  python3 -m tutor_agent.server      (from the repo root)   [PORT env overrides 8080]
"""
import json
import os
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root -> import tutor.*
from tutor import generate
from tutor_agent import providers, dialog

# topic -> the real anchor whose verified twins we serve
TOPIC_ANCHOR = {"route": (2018, 24), "cube": (2018, 27)}
TASKS = {}          # task_id -> {"answer", "stem", "marks", "anchor", "method", "trap"}
_seed = {"n": 0}


def _new_task(topic):
    anchor = TOPIC_ANCHOR.get(topic, (2018, 24))
    it = None
    while it is None and _seed["n"] < 9999:
        it = generate.make_item(anchor, seed=_seed["n"]); _seed["n"] += 1
    tid = uuid.uuid4().hex[:8]
    TASKS[tid] = {"answer": str(it["answer"]), "stem": it["stem"], "marks": it["marks"],
                  "anchor": it["anchor"], "method": it["method_star"], "trap": it["trap"]}
    return tid, TASKS[tid]


def _mark(task_id, answer):
    t = TASKS.get(task_id)
    if not t:
        return {"error": "unknown task_id"}
    correct = str(answer).strip() == t["answer"]
    if correct:
        return {"correct": True, "expression": "happy",
                "feedback": "Yes! That's right. Tell me how you knew you hadn't missed a case."}
    return {"correct": False, "expression": "thinking",
            "feedback": f"Not quite. Here's the key step: {t['method']} Watch the trap: {t['trap']}"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_audio(self, body, headers):
        self.send_response(200)
        self.send_header("Content-Type", providers.TTS_MIME)
        self.send_header("Content-Length", str(len(body)))
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):                      # quieter logs
        pass

    def do_GET(self):
        path, _, query = self.path.partition("?")
        q = dict(p.split("=", 1) for p in query.split("&") if "=" in p)
        if path == "/health":
            return self._send(200, {"ok": True, "tasks": len(TASKS), "stt_tts": providers.mode()})
        if path == "/api/stackchan/next-task":
            tid, t = _new_task(q.get("topic", "route"))
            return self._send(200, {"task_id": tid, "marks": t["marks"], "anchor": t["anchor"],
                                    "say": t["stem"], "expression": "neutral"})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path, _, qs = self.path.partition("?")
        query = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
        ctype = self.headers.get("Content-Type", "")
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n) if n else b""
        is_json = "application/json" in ctype or raw[:1] in (b"{", b"[")
        data = {}
        if is_json:
            try:
                data = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                data = {}

        if path == "/api/stackchan/answer":
            return self._send(200, _mark(data.get("task_id"), data.get("answer", "")))

        if path == "/api/stackchan/voice":
            # Device POSTs raw recording bytes; we transcribe IN MEMORY and never write it to disk.
            # Tests may POST JSON {"text": ...} so the whole loop runs with no key/device.
            sid = data.get("session_id") or self.headers.get("X-Session-Id") or query.get("session_id", "frank")
            text = data.get("text") if is_json else providers.stt(raw)
            r = dialog.handle(sid, text or "")
            if query.get("format") == "json":          # testing path: inspect text, no audio
                return self._send(200, {"heard": text, "say": r["say"], "intent": r.get("intent"),
                                        "expression": r.get("expression"), "end": r.get("end", False)})
            audio = providers.tts(r["say"])             # WAV bytes in the body; control info in headers
            return self._send_audio(audio, {
                "X-Intent": r.get("intent", ""), "X-Expression": r.get("expression", ""),
                "X-End": "1" if r.get("end") else "0",
                "X-Heard": quote(text or ""), "X-Say": quote(r["say"])})

        if path == "/v1/chat/completions":
            # OpenAI-compatible LLM endpoint so xiaozhi-esp32-server's LLM slot calls OUR tutor.
            # xiaozhi-server does STT/TTS; we just turn the transcribed text into the tutor's reply.
            msgs = data.get("messages", [])
            user_text = next((m.get("content", "") for m in reversed(msgs) if m.get("role") == "user"), "")
            if isinstance(user_text, list):            # multimodal content -> take text parts
                user_text = " ".join(p.get("text", "") for p in user_text if isinstance(p, dict))
            sid = data.get("user") or self.headers.get("X-Session-Id") or "frank"
            r = dialog.handle(sid, user_text)
            return self._send(200, {
                "id": "chatcmpl-" + uuid.uuid4().hex[:12], "object": "chat.completion",
                "created": int(time.time()), "model": data.get("model", "amcbuddy-tutor"),
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": r["say"]}}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "amcbuddy": {"intent": r.get("intent"), "expression": r.get("expression"), "end": r.get("end", False)}})
        return self._send(404, {"error": "not found"})


def main():
    port = int(os.environ.get("PORT", "8080"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"AMC-buddy StackChan API on http://0.0.0.0:{port}  (STT/TTS: {providers.mode()})")
    srv.serve_forever()


if __name__ == "__main__":
    main()
