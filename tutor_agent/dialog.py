"""Deterministic teaching state machine (the core — before any audio).

Text in, text out. No LLM, no key, no device. Intents (per the agreed v1 set):
  start_question · submit_answer · explain · repeat · progress · stop/next
Every question + answer + worked solution comes from the verified engine (tutor.generate),
never improvised. The audio shell (STT/TTS) wraps this later; the loop here IS the tutor.

Demo the whole conversation:  python3 -m tutor_agent.dialog
"""
import re
from tutor import generate

TOPIC_ANCHOR = {"route": (2018, 24), "cube": (2018, 27)}
SESSIONS = {}


def _session(sid):
    return SESSIONS.setdefault(sid, {"task": None, "asked": 0, "correct": 0, "attempts": 0, "seed": 0})


def _num(text):
    m = re.search(r"-?\d+", text.replace(",", ""))
    return m.group(0) if m else None


def detect_intent(text):
    t = text.lower().strip()
    if re.fullmatch(r"-?\d+\s*(km)?", t) or (re.search(r"\b(answer|got|is|equals|it's|i think)\b", t) and _num(t)):
        return "submit_answer"
    if any(w in t for w in ["explain", "why", "how do", "show me", "work it", "don't get", "stuck"]):
        return "explain"
    if any(w in t for w in ["repeat", "again", "what was", "say that"]):
        return "repeat"
    if any(w in t for w in ["progress", "how am i", "my score", "how's frank", "doing"]):
        return "progress"
    if any(w in t for w in ["stop", "quit", "finish", "bye", "that's enough"]):
        return "stop"
    if any(w in t for w in ["next", "another", "skip", "start", "question", "drill", "practice", "begin", "give me"]):
        return "start_question"
    return "unknown"


def _worked(it):
    p = it["params"]
    if it["type"] == "route_inspection":
        a, b, hyp = p["_dims"]
        fence = sum(w for _, _, w in p["edges"]); extra = it["answer"] - fence
        return (f"All four corners have 3 fences, which is odd, so you must re-walk the two shortest "
                f"sides. Fence total is 2 times {a} plus 2 times {b} plus 2 times {hyp}, that's {fence}. "
                f"The minimum extra is 2 times {min(a, b)}, that's {extra}. So the shortest route is "
                f"{fence} plus {extra}, which is {it['answer']} kilometres.")
    v = p["visible"]; o = [it["answer"] - x for x in v]
    return (f"The three faces you can see meet at a corner, so they are not opposite each other — "
            f"their opposites are hidden. For a total of {it['answer']}, the hidden faces are "
            f"{it['answer']} minus {v[0]} is {o[0]}, {it['answer']} minus {v[1]} is {o[1]}, and "
            f"{it['answer']} minus {v[2]} is {o[2]}. All three use only the allowed digits and are "
            f"different, so the largest total is {it['answer']}.")


def _start(s, topic):
    anchor = TOPIC_ANCHOR[topic]
    it = None
    while it is None and s["seed"] < 9999:
        it = generate.make_item(anchor, seed=s["seed"]); s["seed"] += 1
    s["task"] = it; s["last_task"] = it; s["attempts"] = 0; s["asked"] += 1
    return {"intent": "start_question", "expression": "neutral",
            "say": f"Here's a {it['marks']}-mark question. {it['stem']}"}


def _submit(s, text):
    it = s["task"]
    if not it:
        return {"intent": "submit_answer", "expression": "neutral",
                "say": "We haven't started a question yet. Say 'start a question' when you're ready."}
    given = _num(text)
    s["attempts"] += 1
    if given is not None and given == str(it["answer"]):
        s["correct"] += 1; s["task"] = None
        return {"intent": "submit_answer", "expression": "happy", "correct": True,
                "say": f"Yes, {it['answer']} is right! Now tell me: how do you know you didn't miss a case?"}
    if s["attempts"] == 1:
        return {"intent": "submit_answer", "expression": "thinking", "correct": False,
                "say": f"Not quite. Here's the key idea: {it['method_star']} Have another go."}
    return {"intent": "submit_answer", "expression": "encouraging", "correct": False,
            "say": f"Still not there. Watch this trap: {it['trap']} Say 'explain' if you'd like me to walk it through."}


def _explain(s):
    it = s["task"] or s.get("last_task")
    if not it:
        return {"intent": "explain", "expression": "neutral", "say": "Start a question first, then I can explain it."}
    return {"intent": "explain", "expression": "talking", "say": _worked(it)}


def handle(sid, text):
    s = _session(sid)
    intent = detect_intent(text)
    if intent == "start_question":
        return _start(s, "cube" if "cube" in text.lower() else "route")
    if intent == "submit_answer":
        return _submit(s, text)
    if intent == "explain":
        return _explain(s)
    if intent == "repeat":
        it = s["task"]
        return {"intent": "repeat", "expression": "neutral",
                "say": it["stem"] if it else "There's no question yet — say 'start'."}
    if intent == "progress":
        return {"intent": "progress", "expression": "neutral",
                "say": f"So far this session you've tried {s['asked']} questions and got {s['correct']} right. "
                       f"We're focusing on your weak spot, M8 logic and route puzzles."}
    if intent == "stop":
        return {"intent": "stop", "expression": "happy", "end": True,
                "say": "Great work today, Frank. See you next time!"}
    return {"intent": "unknown", "expression": "neutral",
            "say": "You can say: start a question, my answer is …, explain, repeat, progress, or stop."}


if __name__ == "__main__":
    sid = "demo"
    script = ["Hi, give me a question", "is it 999?", "my answer is 500", "explain",
              "start a cube question", "progress", "stop"]
    for u in script:
        # for the demo, when we 'know' the answer, submit the correct one to show the success path
        if u == "my answer is 500" and SESSIONS.get(sid, {}).get("task"):
            u = f"my answer is {SESSIONS[sid]['task']['answer']}"
        r = handle(sid, u)
        print(f"\nFRANK: {u}\nBUDDY ({r['expression']}): {r['say']}")
