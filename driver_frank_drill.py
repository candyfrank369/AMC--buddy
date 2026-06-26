"""Targeted drill builder for Frank, driven by the verified engine.
Picks anchors whose MECHANISM matches Frank's real 2018 misses:
  - M2 constrained_number (2025 Q26)  -> his Q30 cross-number / digit-property logic
  - M5 choose_sum_divisible (2013 Q27) -> his Q27 organised enumeration
  - M5 crt_candidates (2024 Q24)       -> constraint elimination
Every item is a verify.py-gated twin of a real anchor. Nothing is improvised.
"""
import json, os
from tutor import generate

PLAN = [
    ((2025, 26), 3, "cross-number / digit-property (M2)"),
    ((2013, 27), 2, "organised enumeration (M5)"),
    ((2024, 24), 1, "constraint elimination (M5)"),
]

items, seen = [], set()
for anchor, n, focus in PLAN:
    got, s = 0, 0
    while got < n and s < 400:
        try:
            it = generate.make_item(anchor, seed=s)
        except Exception:
            it = None          # proposer hit an infeasible combo (engine bug to fix); skip
        s += 1
        if it is None or it["stem"] in seen:
            continue
        seen.add(it["stem"]); it["focus"] = focus
        items.append(it); got += 1

# order by marks so the paper ramps easy->hard like a real tail
items.sort(key=lambda x: x["marks"])

os.makedirs("practice", exist_ok=True)
out = "practice/Frank_drill_2026-06-25.json"
with open(out, "w") as f:
    json.dump([{k: (str(v) if k == "params" else v) for k, v in it.items()} for it in items], f, indent=2)

print(f"generated {len(items)} verified twins -> {out}\n")
for i, it in enumerate(items, 1):
    print(f"[{i}] {it['anchor']} twin  {it['mechanism']}  {it['marks']} marks  "
          f"(diff {it['difficulty']} in band {it['band']}, unique={it['unique']})")
    print(f"    {it['stem']}")
    print(f"    ANSWER = {it['answer']}\n")
