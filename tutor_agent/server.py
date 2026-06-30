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
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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

    def _read_json(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n) if n else b""
        try:
            return json.loads(raw or b"{}"), raw
        except json.JSONDecodeError:
            return {}, raw

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
        path = self.path.partition("?")[0]
        data, raw = self._read_json()
        if path == "/api/stackchan/answer":
            return self._send(200, _mark(data.get("task_id"), data.get("answer", "")))
        if path == "/api/stackchan/voice":
            # device sends audio; STT -> text -> teaching state machine -> reply (-> TTS).
            # For testing we also accept {"text": ...} so the whole loop runs with no key/device.
            sid = data.get("session_id", "frank")
            text = data.get("text") or providers.stt(raw)
            r = dialog.handle(sid, text)
            r["heard"] = text
            r["audio_b64"] = providers.tts(r["say"])      # "" in text-stub mode
            return self._send(200, r)
        return self._send(404, {"error": "not found"})


def main():
    port = int(os.environ.get("PORT", "8080"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"AMC-buddy StackChan API on http://0.0.0.0:{port}  (STT/TTS: {providers.mode()})")
    srv.serve_forever()


if __name__ == "__main__":
    main()
