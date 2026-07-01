"""brain_llm.py — multilingual LLM orchestrator (the 'brain' behind the voice adapter).

Drop-in for dialog.handle:  respond(session_id, text) -> {"say", "expression"}.
Talks to an OpenAI-compatible LLM via OpenRouter (uses the parent's $100 balance). Converses in
the user's language (Chinese OR English), acts as Frank's warm Learning-Buddy companion, and
calls verified engine TOOLS for any real practice question or marking — it never invents graded
content itself (iron rule). Swap this in and the adapter/transport is untouched.

Env: OPENROUTER_API_KEY (required), OPENROUTER_MODEL (default openai/gpt-4o-mini).
Demo:  set -a; . ~/.amcbuddy.env; set +a; python3 -m tutor_agent.brain_llm
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tutor import generate

_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
_API = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM = (
    "You are Bob, Frank's Learning Buddy — a warm, encouraging AI tutor companion for Frank, an "
    "11-year-old Year-6 student. Your name is Bob. When Frank greets you (e.g. 'Hi Bob'), greet "
    "him back warmly and briefly. You live in a small desktop robot and everything you say is "
    "SPOKEN ALOUD.\n"
    "- Reply in the SAME language the user speaks. Chinese in -> Chinese out; English in -> "
    "English out. Frank's schoolwork is English but he/his parent may speak Chinese.\n"
    "- Keep replies SHORT and natural for speech: usually 1-2 sentences. No markdown, no lists, "
    "no long paragraphs, no emoji.\n"
    "- You can chat about writing ideas, explain a maths/science concept, spelling, study habits, "
    "and cheer Frank on. Be Socratic: nudge with a guiding question rather than dumping answers.\n"
    "- IRON RULE: never invent a practice question or grade an answer yourself. When Frank wants a "
    "real practice question or wants an answer checked, CALL THE TOOL. Explaining and chatting are "
    "free; graded questions come only from tools.\n"
    "- When a tool gives you a question, read the QUESTION to Frank but DO NOT say the answer — "
    "keep it to check his reply."
)

TOOLS = [{
    "type": "function",
    "function": {
        "name": "generate_math_question",
        "description": "Get ONE verified AMC-style maths question (and its hidden answer) from the "
                       "grounded engine. Use when Frank explicitly wants a maths practice question.",
        "parameters": {"type": "object",
                       "properties": {"topic": {"type": "string", "enum": ["route", "cube"],
                                                "description": "route = route-inspection/Euler; cube = cube opposite faces"}},
                       "required": ["topic"]},
    },
}]

_TOPIC = {"route": (2018, 24), "cube": (2018, 27)}
_SESS = {}
_seed = {"n": 0}


def _gen_math(topic):
    anchor = _TOPIC.get(topic, (2018, 24))
    it = None
    while it is None and _seed["n"] < 9999:
        it = generate.make_item(anchor, seed=_seed["n"]); _seed["n"] += 1
    return {"question": it["stem"], "answer": str(it["answer"]), "marks": it["marks"]}


def _chat(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS,
                       "temperature": 0.6, "max_tokens": 400}).encode()
    req = urllib.request.Request(_API, data=body, headers={
        "Authorization": "Bearer " + _KEY, "Content-Type": "application/json",
        "HTTP-Referer": "https://learning-buddy.local", "X-Title": "Learning Buddy"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["choices"][0]["message"]


def respond(sid, text):
    if not _KEY:
        return {"say": "OpenRouter key is not set.", "expression": "neutral"}
    msgs = _SESS.setdefault(sid, [{"role": "system", "content": SYSTEM}])
    msgs.append({"role": "user", "content": text})
    for _ in range(4):                                   # allow up to a few tool round-trips
        m = _chat(msgs)
        msgs.append(m)
        calls = m.get("tool_calls")
        if not calls:
            say = (m.get("content") or "").strip()
            if len(msgs) > 24:                           # bound history, cut only at a user boundary
                k = len(msgs) - 16
                while k > 1 and msgs[k].get("role") != "user":
                    k += 1
                msgs[:] = [msgs[0]] + msgs[k:]
            return {"say": say or "Hmm, tell me more.", "expression": "talking"}
        for tc in calls:
            fn = tc["function"]["name"]
            args = json.loads(tc["function"].get("arguments") or "{}")
            res = _gen_math(args.get("topic", "route")) if fn == "generate_math_question" else {"error": "unknown"}
            msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(res)})
    return {"say": "Let's keep going — what would you like to do?", "expression": "neutral"}


if __name__ == "__main__":
    for u in ["Hi! Who are you?",
              "你能用中文陪我聊聊我的写作想法吗？我想写一个关于机器人的故事",
              "Okay, give me a maths practice question about routes."]:
        r = respond("demo", u)
        print(f"\nUSER: {u}\nBUDDY ({r['expression']}): {r['say']}")
