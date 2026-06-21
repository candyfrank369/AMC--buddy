"""diagnose.py — turn Frank's completed paper into a fix.

Input  : a list of attempts. Each attempt is a question he sat (mechanism + type + params +
         which real anchor it twins + the correct answer is recomputed here), plus HIS answer,
         his WORKING (text), and whether it was right/wrong.
Output : the weak mechanism(s); the exact broken step in his working (matched to a NAMED
         typical mistake = the mechanism's trap); an explanation grounded in the nearest
         official Solution (TWO methods, the ★ crowned fastest, the trap); and 3-5 verified
         same-mechanism twins to drill (each gated through verify.py). A per-mechanism profile
         is updated on disk.

Run the built-in demo:  python -m tutor.diagnose
"""
import json
import os
import re
from itertools import combinations

from tutor import generate, verify

MODULES = verify.MODULES
_PROFILE = os.path.join(verify._ROOT, "content", "profile.json")


# ----------------------------------------------------------------- the two methods per card
METHODS = {
    "M1": dict(name="place-value extreme",
               fast="Sort the digits into place-value columns (biggest digits to the biggest "
                    "columns). For two 3-digit numbers the answer is 99 x (top-column sum - "
                    "bottom-column sum) — the middle column cancels.",
               other="Build the largest total and the smallest total as whole numbers, then subtract.",
               trap="tracking the whole numbers instead of the columns, or giving one total "
                    "instead of the difference."),
    "M2": dict(name="stacked-constraint number",
               fast="Order the constraints by pruning power (divisibility/parity first; digit-sum "
                    "for /9, last digit for even/5) and keep the leading digit as small as possible.",
               other="List every multiple in range and filter by the other conditions.",
               trap="applying the weak constraints first, or dropping the distinct / no-zero filters."),
    "M3": dict(name="non-commutative op ordering",
               fast="Defer the doublings to last (a x2 scales everything already gained); do the "
                    "value-shrinking step early.",
               other="Try all orderings and compare the finals.",
               trap="multiplying too early."),
    "M4": dict(name="working backwards",
               fast="Reverse the chain from the end, undoing each step with its inverse, last step first.",
               other="Write the forward expression and solve the equation.",
               trap="reporting an intermediate value of the reverse chain (or the amount left) "
                    "instead of the start."),
    "M5": dict(name="organised enumeration / modular bucketing",
               fast="Bucket by remainder (or an ordered table): count all-from-one-bucket PLUS "
                    "one-from-each — no missing or double counts.",
               other="Enumerate every combination and test the condition.",
               trap="forgetting a case (e.g. the all-same-bucket one), or counting ordered vs unordered."),
    "M6": dict(name="sequence / recurrence",
               fast="Find the cycle, then index the far term by its period.",
               other="Iterate the rule term by term.",
               trap="an off-by-one in where the cycle starts, or not noticing it repeats."),
}

DRILL_ANCHOR = {"M1": (2024, 26), "M2": (2025, 26), "M3": (2024, 27),
                "M4": (2025, 22), "M5": (2024, 28), "M6": (2024, 29)}


# ----------------------------------------------------------------- error models (broken step)
def _nums(working):
    return [int(x) for x in re.findall(r"-?\d+", working or "")]


def _e_digit_extremes(p, ans, working):
    hi = MODULES["M1"].solve({**p, "objective": "maxsum"})
    lo = MODULES["M1"].solve({**p, "objective": "minsum"})
    if ans == hi:
        return f"You found the LARGEST total ({hi}) but stopped — you never subtracted the smallest ({lo}). The answer is the difference {hi - lo}."
    if ans == lo:
        return f"You found the smallest total ({lo}) only. The answer is largest - smallest = {hi - lo}."
    return f"Your value doesn't match the largest ({hi}), smallest ({lo}) or their difference ({hi - lo}) — re-sort the digits into columns."


def _e_constrained_number(p, ans, working):
    preds = p["predicates"]
    for i in range(len(preds)):
        sub = {**p, "predicates": preds[:i] + preds[i + 1:]}
        try:
            if MODULES["M2"].solve(sub) == ans:
                dropped = preds[i]
                desc = generate._MULT_WORD.get(dropped[1], str(dropped)) if isinstance(dropped, list) and dropped[0] == "multiple_of" else dropped
                return f"{ans} satisfies every condition EXCEPT one — you dropped '{desc}'. Put that filter back in."
        except StopIteration:
            pass
    return f"{ans} is not the smallest number meeting all the conditions — check them in pruning order."


def _e_op_order(p, ans, working):
    as_listed = MODULES["M3"].solve({**p, "ops": p["ops"]})  # solve is order-independent (it optimises)
    F = MODULES["M3"].Fraction
    listed_val = p["start"]
    for a, b in p["ops"]:
        listed_val = F(a) * listed_val + F(b)
    listed_val = int(listed_val) if listed_val.denominator == 1 else listed_val
    if ans == listed_val:
        return f"You used the machines in the order written ({listed_val}). Re-order: defer the doublings to last."
    return f"{ans} comes from a sub-optimal order; the best order does the halving early and the doublings last."


def _e_affine_chain(p, ans, working):
    # reverse chain at PRIMITIVE granularity (subtract b, then divide by a) — this is how the
    # official solution undoes each step, so intermediates like 14 are visible.
    from fractions import Fraction as F

    def show(v):
        return int(v) if v.denominator == 1 else v

    trace, cur = [show(F(p["end"]))], F(p["end"])
    for a, b in reversed(p["ops"]):
        cur = cur - F(b); trace.append(show(cur))
        cur = cur / F(a); trace.append(show(cur))
    start = trace[-1]
    if ans in trace[1:-1]:
        return (f"You stopped one step early: {ans} is an INTERMEDIATE value of the reverse "
                f"chain {' -> '.join(map(str, trace))}. Keep undoing to the start = {start}.")
    if ans == p["end"]:
        return f"You gave the final value ({p['end']}) you ended on, not the original number ({start})."
    return f"Your reverse chain went wrong; it should be {' -> '.join(map(str, trace))} (start = {start})."


def _e_fraction_remainder(p, ans, working):
    if p["final"][0] == "count" and ans == p["final"][1]:
        return f"You gave the amount REMAINING ({ans}), not the starting amount. Work backwards from what's left."
    return f"{ans} isn't consistent with the fractions removed — invert the stages in reverse order."


def _residue_split(p):
    d = p["divisor"]
    same = sum(1 for c in combinations(p["set"], p["choose"])
               if len({x % d for x in c}) == 1 and sum(c) % d == 0)
    total = MODULES["M5"].solve(p)
    return same, total - same, total


def _e_choose_sum_divisible(p, ans, working):
    same, mixed, total = _residue_split(p)
    if ans == mixed:
        return f"You counted the mixed-remainder triples ({mixed}) but forgot the all-from-one-remainder-group case (+{same}). Total = {total}."
    if ans == same:
        return f"You counted only the all-from-one-group case ({same}); add the one-from-each case (+{mixed}). Total = {total}."
    return f"{ans} is off; bucket by remainder: all-same-group ({same}) + one-from-each ({mixed}) = {total}."


def _e_crt_candidates(p, ans, working):
    (m1, r1), (m2, r2) = p["mods"]
    rem = p["full"] - ans
    ok1, ok2 = rem % m1 == r1, rem % m2 == r2
    if ok1 and not ok2:
        return f"{ans} satisfies only the /{m1} condition; you skipped the /{m2} check (need remainder {r2})."
    if ok2 and not ok1:
        return f"{ans} satisfies only the /{m2} condition; you skipped the /{m1} check (need remainder {r1})."
    return f"{ans} fits neither remainder condition — test both before choosing."


def _e_iterate_map(p, ans, working):
    for delta, word in ((-1, "one before"), (1, "one after")):
        if ans == MODULES["M6"].solve({**p, "index": p["index"] + delta}):
            return f"Off-by-one: {ans} is the term {word} the {p['index']}th. Recount where the cycle starts."
    return f"{ans} isn't a nearby term — find the cycle, then index by its period."


def _e_bounded_walk(p, ans, working):
    from math import comb
    L = p["length"]
    if ans == 2 ** L:
        return f"You counted ALL {2 ** L} orderings and ignored the lead limit of {p['high']}."
    if ans == comb(L, L // 2):
        return f"You only counted level-finish sequences ({comb(L, L // 2)}); the lead-limit rules out many of them."
    return f"{ans} doesn't match the bounded count — track the running lead and never let it exceed {p['high']}."


ERROR = {
    "digit_extremes": _e_digit_extremes, "constrained_number": _e_constrained_number,
    "op_order": _e_op_order, "affine_chain": _e_affine_chain,
    "fraction_remainder": _e_fraction_remainder, "choose_sum_divisible": _e_choose_sum_divisible,
    "crt_candidates": _e_crt_candidates, "iterate_map": _e_iterate_map,
    "bounded_walk": _e_bounded_walk,
}


# ----------------------------------------------------------------- profile
def load_profile():
    if os.path.exists(_PROFILE):
        with open(_PROFILE) as fh:
            return json.load(fh)
    return {}


def save_profile(prof):
    with open(_PROFILE, "w") as fh:
        json.dump(prof, fh, indent=2, sort_keys=True)


# ----------------------------------------------------------------- diagnosis
def diagnose_attempt(att):
    mech, typ, params = att["mechanism"], att["type"], att["params"]
    correct = MODULES[mech].solve(params)
    is_right = att["frank_answer"] == correct
    broken = None
    if not is_right:
        det = ERROR.get(typ)
        broken = det(params, att["frank_answer"], att.get("working", "")) if det \
            else f"answer {att['frank_answer']} != {correct}; review the {mech} method."
    return {"q": att.get("q"), "mechanism": mech, "anchor": att.get("anchor", "?"),
            "frank": att["frank_answer"], "correct": correct, "right": is_right, "broken": broken}


def diagnose_paper(attempts, n_drills=4):
    results = [diagnose_attempt(a) for a in attempts]

    # per-paper + cumulative profile
    prof = load_profile()
    paper = {}
    for r in results:
        m = r["mechanism"]
        paper.setdefault(m, [0, 0])
        paper[m][1] += 1
        paper[m][0] += int(r["right"])
        slot = prof.setdefault(m, {"attempts": 0, "correct": 0})
        slot["attempts"] += 1
        slot["correct"] += int(r["right"])
    save_profile(prof)

    weak = sorted((m for m, (c, n) in paper.items() if c < n),
                  key=lambda m: (paper[m][0] / paper[m][1], -paper[m][1], m))
    weakest = weak[0] if weak else None

    drills = []
    if weakest:
        anchor = DRILL_ANCHOR[weakest]
        seen, s = set(), 0
        while len(drills) < n_drills and s < 200:
            it = generate.make_item(anchor, seed=s); s += 1
            if it and it["stem"] not in seen:
                seen.add(it["stem"]); drills.append(it)
    return {"results": results, "paper": paper, "profile": prof,
            "weak": weak, "weakest": weakest, "drills": drills}


def render(rep):
    out = ["=" * 78, "DIAGNOSIS — Frank's paper", "=" * 78]
    for r in rep["results"]:
        if r["right"]:
            continue
        m = r["mechanism"]
        out.append(f"\nQ{r['q']}  WRONG  [{m} {METHODS[m]['name']} · twin of {r['anchor']}]")
        out.append(f"   his answer {r['frank']}   (correct {r['correct']})")
        out.append(f"   BROKEN STEP: {r['broken']}")
        out.append(f"   grounded in {r['anchor']}'s official method:")
        out.append(f"     ★ fastest: {METHODS[m]['fast']}")
        out.append(f"     also     : {METHODS[m]['other']}")
        out.append(f"     ✗ trap    : {METHODS[m]['trap']}")

    out.append("\n" + "-" * 78)
    out.append("WEAK MECHANISMS (this paper): " +
               (", ".join(f"{m} {rep['paper'][m][0]}/{rep['paper'][m][1]}" for m in rep["weak"]) or "none"))
    out.append("CUMULATIVE PROFILE: " +
               "  ".join(f"{m}={v['correct']}/{v['attempts']}" for m, v in sorted(rep["profile"].items())))

    if rep["weakest"]:
        wk = rep["weakest"]
        out.append("\n" + "-" * 78)
        out.append(f"DRILL — weakest mechanism {wk} ({METHODS[wk]['name']}): "
                   f"{len(rep['drills'])} verified same-mechanism twins")
        for i, it in enumerate(rep["drills"], 1):
            out.append(f"  D{i} [{it['marks']} marks, twin of {it['anchor']}]  {it['stem']}")
        out.append("  drill answer key: " +
                   ", ".join(f"D{i}={it['answer']}" for i, it in enumerate(rep["drills"], 1)) +
                   "   (each verifier-checked: unique + in band)")
    out.append("=" * 78)
    return "\n".join(out)


# ----------------------------------------------------------------- demo
def _demo_paper():
    """One realistic completed paper: he twists each mechanism a known way."""
    g = generate.make_item
    atts = []

    it = g((2024, 26), seed=0)                       # M1: gives the largest total only
    hi = MODULES["M1"].solve({**it["params"], "objective": "maxsum"})
    atts.append({"q": 1, "mechanism": "M1", "type": it["type"], "params": it["params"],
                 "anchor": it["anchor"], "frank_answer": hi,
                 "working": f"biggest sum = {hi}. (ringed it as the answer)"})

    it = g((2025, 26), seed=1)                       # M2: correct
    atts.append({"q": 2, "mechanism": "M2", "type": it["type"], "params": it["params"],
                 "anchor": it["anchor"], "frank_answer": it["answer"], "working": "checked /, even, distinct"})

    it = g((2024, 27), seed=2)                       # M3: correct
    atts.append({"q": 3, "mechanism": "M3", "type": it["type"], "params": it["params"],
                 "anchor": it["anchor"], "frank_answer": it["answer"], "working": "doublings last"})

    # M4 (a): the signature intermediate-value trap (2013 Q8 family)
    p4 = {"type": "affine_chain", "ops": [[2, 2], [generate.verify.MODULES["M3"].Fraction(1, 2), -2]], "end": 6}
    atts.append({"q": 4, "mechanism": "M4", "type": "affine_chain", "params": p4, "anchor": "2013 Q8",
                 "frank_answer": 14, "working": "6 +2 = 8, x2 = 16, -2 = 14  -> 14"})

    # M4 (b): gave the amount remaining
    it = g((2025, 22), seed=3)
    atts.append({"q": 5, "mechanism": "M4", "type": it["type"], "params": it["params"],
                 "anchor": it["anchor"], "frank_answer": it["params"]["final"][1],
                 "working": "1/4 then 1/3 ... wrote down what's left"})

    it = g((2013, 27), seed=4)                       # M5: forgot the all-same-bucket case
    same, mixed, total = _residue_split(it["params"])
    atts.append({"q": 6, "mechanism": "M5", "type": it["type"], "params": it["params"],
                 "anchor": it["anchor"], "frank_answer": mixed,
                 "working": "one from each remainder group only"})

    it = g((2024, 29), seed=5)                       # M6: off-by-one on the cycle
    near = MODULES["M6"].solve({**it["params"], "index": it["params"]["index"] + 1})
    atts.append({"q": 7, "mechanism": "M6", "type": it["type"], "params": it["params"],
                 "anchor": it["anchor"], "frank_answer": near, "working": "found the cycle, counted to the next term"})
    return atts


if __name__ == "__main__":
    # fresh profile for a clean demo
    if os.path.exists(_PROFILE):
        os.remove(_PROFILE)
    print(render(diagnose_paper(_demo_paper())))
