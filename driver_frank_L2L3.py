"""L2/L3 Medal-strength drill for Frank — same two topics, much harder.
Built on the engine's verified solvers (the code judge), with explicit Medal gates:
  L2  in-band difficulty + a HIDDEN condition whose omission gives a smaller wrong answer
      (the decoy is computed; we require decoy < true so the trap is real).
  L3  difficulty ABOVE the real-paper ceiling AND a naive search space too large to hand-
      enumerate -> only structural reasoning works. Uniqueness still guaranteed by the solver.
Answers constrained to whole numbers <= 999 (AMC integer-answer format).
"""
import json, os, random
from math import comb
from tutor import verify, generate

m2 = verify.MODULES["M2"]; m5 = verify.MODULES["M5"]
M2_CEIL, M5_CEIL = 5, 12          # real-anchor difficulty ceilings (constrained_number / choose_sum)

# ---------- property phrasing (works for "smallest" and "count") ----------
def prop(pr):
    if isinstance(pr, (list, tuple)):
        k, a = pr[0], pr[1]
    else:
        k, a = pr, None
    return {"multiple_of": f"divisible by {a}", "even": "even", "odd": "odd",
            "contains_digit": f"contains the digit {a}", "no_digit": f"has no digit {a}",
            "all_distinct": "has all different digits",
            "num_odd_digits": f"has exactly {a} odd digit" + ("s" if a != 1 else ""),
            "digit_sum_multiple": f"has a digit sum divisible by {a}",
            "divisible_by_unit_digit": "is divisible by its own units digit"}[k]

def nd_word(rng_lo_hi):
    lo, hi = rng_lo_hi
    return {(100, 999): "three-digit", (1000, 9999): "four-digit"}.get((lo, hi), f"number in {lo}-{hi}")

def stem_constrained(p):
    nd = nd_word(tuple(p["range"]))
    props = "; ".join(prop(x) for x in p["predicates"])
    if p["want"] == "smallest":
        return f"What is the smallest {nd} number with all of these properties: {props}?"
    return f"How many {nd} numbers have all of these properties: {props}?"

# ---------- builders ----------
def m2_L2(rng):
    mult = rng.choice([3, 6, 9])
    contain = rng.choice([2, 3, 4, 5, 6, 7])
    trap = rng.choice([["num_odd_digits", rng.choice([1, 2])], "divisible_by_unit_digit",
                       ["digit_sum_multiple", rng.choice([4, 5, 7])]])
    base = [["multiple_of", mult], ["contains_digit", contain], ["no_digit", 0], "all_distinct"]
    full = base + [trap]
    pf = {"type": "constrained_number", "range": [100, 999], "want": "smallest", "predicates": full}
    pb = {"type": "constrained_number", "range": [100, 999], "want": "smallest", "predicates": base}
    try:
        true = m2.solve(pf); decoy = m2.solve(pb)
    except StopIteration:
        return None
    if not (decoy < true):
        return None
    return dict(level="L2", topic="cross-number / digit-property", marks=7, lineage="real 2025 Q26 (M2) + hidden condition",
                stem=stem_constrained(pf), answer=true, difficulty=len(full), ceiling=M2_CEIL,
                trap=f"a solver who skips “{prop(trap)}” stops at {decoy} — the planted decoy.",
                method="Apply the strong filters first (divisibility, no-zero, distinct), then check the SUBTLE last condition before you commit — don't stop at the first multiple you find.")

def m2_L3(rng):
    mult = rng.choice([11, 12, 13])                # not 9/3 -> digit-sum condition is independent
    preds = [["multiple_of", mult], "all_distinct", ["no_digit", 0],
             ["num_odd_digits", rng.choice([2, 3])], ["digit_sum_multiple", rng.choice([3, 9])],
             ["contains_digit", rng.choice([2, 4, 6, 8])]]   # 6 preds -> above the M2 ceiling of 5
    p = {"type": "constrained_number", "range": [1000, 9999], "want": "count", "predicates": preds}
    cnt = m2.solve(p)
    if not (1 <= cnt <= 999):
        return None
    return dict(level="L3", topic="cross-number / digit-property", marks=8, lineage="scaled twin of 2025 Q26 (M2)",
                stem=stem_constrained(p), answer=cnt, difficulty=len(preds), ceiling=M2_CEIL,
                why="~9000 four-digit candidates — you cannot list them. Count structurally: fix the digit-sum/parity buckets and use divisibility.",
                method="Don't hunt for examples — partition by the binding condition (digit sum / parity) and count each class.")

def m5_choose_L3(rng):
    n = rng.choice([20, 21, 24]); start = rng.choice([1, 2, 3]); d = rng.choice([3, 4])
    p = {"type": "choose_sum_divisible", "set": list(range(start, start + n)), "choose": 3, "divisor": d}
    cnt = m5.solve(p)
    if not (1 <= cnt <= 999):
        return None
    return dict(level="L3", topic="organised counting (residue classes)", marks=7, lineage="scaled twin of 2013 Q27 (M5)",
                stem=generate.STEMS["choose_sum_divisible"](p), answer=cnt, difficulty=n, ceiling=M5_CEIL,
                why=f"C({n},3) = {comb(n, 3)} triples — impossible to list. Sort the numbers into remainder buckets mod {d} and count the bucket combinations.",
                method=f"Bucket all numbers by remainder mod {d}; the valid triples are 'all-from-one-bucket' + the matching cross-bucket combinations.")

def m5_count_L3(rng):
    step = rng.choice([3, 4, 6, 7]); count = rng.choice([250, 300, 400]); digit = rng.choice([0, 1, 2])
    p = {"type": "count_digit_in_list", "start": step, "step": step, "count": count, "digit": digit}
    ans = m5.solve(p)
    if not (1 <= ans <= 999):
        return None
    last = step + (count - 1) * step
    return dict(level="L3", topic="organised counting (digit positions)", marks=8, lineage="scaled twin of 2024 Q28 (M5)",
                stem=generate.STEMS["count_digit_in_list"](p), answer=ans, difficulty=count, ceiling="(n/a)",
                why=f"{count} terms up to {last} — you can't write them out. Count the digit '{digit}' one place-column at a time (units, tens, hundreds).",
                method="Go place-column by place-column: count how often the digit appears in the units, then tens, then hundreds across the whole list.")

PLAN = [(m2_L2, 2), (m2_L3, 1), (m5_choose_L3, 2), (m5_count_L3, 1)]

items, seen, seen_ans, rng = [], set(), set(), random.Random(7)
for builder, n in PLAN:
    got, tries = 0, 0
    while got < n and tries < 600:
        tries += 1
        it = builder(rng)
        if it is None or it["stem"] in seen or it["answer"] in seen_ans:
            continue                       # dedupe by stem AND by answer (kill twin-answer clashes)
        seen.add(it["stem"]); seen_ans.add(it["answer"]); items.append(it); got += 1

order = {"L2": 0, "L3": 1}
items.sort(key=lambda x: (order[x["level"]], x["marks"]))

os.makedirs("practice", exist_ok=True)
json.dump([{k: (str(v) if k == "params" else v) for k, v in it.items()} for it in items],
          open("practice/Frank_drill_L2L3.json", "w"), indent=2, ensure_ascii=False)

print(f"built {len(items)} L2/L3 items\n")
for i, it in enumerate(items, 1):
    print(f"[{i}] {it['level']}  {it['topic']}  (diff {it['difficulty']} vs ceiling {it['ceiling']})")
    print(f"    {it['stem']}")
    print(f"    ANSWER = {it['answer']}\n")
