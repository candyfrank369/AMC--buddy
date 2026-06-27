"""generate.py — propose a parameterised TWIN of a real anchor, gate it through
verify.py, emit ONLY if it passes.

Design (CLAUDE.md rule #3): the LLM is only a *proposer*. Building this repo is local
coding (no API spend), so the proposer is a deterministic parameter generator per anchor
family; verify.py is the sole judge of correctness (unique answer) and difficulty
(in the real-paper band). We never brute-force-generate-and-discard: proposers stay in
band by construction, so retries are tiny and only cover "does a solution exist".

A twin NEVER reproduces a real stem: the numbers are changed (we assert params != the
anchor's params) and the English is rendered here, not copied from any source PDF.

Only families with a free parameter *independent of the difficulty proxy* can be twinned
without collapsing onto the anchor; single-parameter families (e.g. stepping_stones,
sparse_grid) are CURATED, not generated.
"""
import random

from tutor import verify
from tutor.anchors import REGISTRY

_MARKS = verify._marks_lookup()
_BANDS = verify.learn_bands()


# ---------------------------------------------------------------- proposers
def _p_digit_extremes(rng, base):                      # M1  (twin of 2024 Q26)
    n = len(base["digits"])                            # keep digit count -> same band
    digits = rng.sample(range(1, 10), n)
    groups = rng.choice([[n], [n // 2, n // 2]] if n % 2 == 0 else [[n]])
    return {"type": "digit_extremes", "digits": digits, "groups": groups, "objective": "diff"}


def _p_constrained_number(rng, base):                  # M2  (twin of 2025 Q26)
    mult = rng.choice([3, 4, 6, 9])
    contain = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
    # don't contradict an even multiple (4/6 force even); parity is only free when mult is odd
    parity = "even" if mult % 2 == 0 else rng.choice(["even", "odd"])
    return {"type": "constrained_number", "range": [100, 999], "want": "smallest",
            "predicates": [parity, ["multiple_of", mult], ["contains_digit", contain],
                           ["no_digit", 0], "all_distinct"]}


def _p_op_order(rng, base):                            # M3  (twin of 2024 Q27)
    ops = [[1, rng.choice([8, 10, 12, 15])], [2, 0],
           [verify.MODULES["M3"].Fraction(1, 2), rng.choice([40, 50, 60])],
           [2, rng.choice([3, 5, 7])]]
    return {"type": "op_order", "start": rng.choice([8, 10, 12]), "ops": ops, "objective": "max"}


def _p_fraction_remainder(rng, base):                  # M4  (twin of 2025 Q22)
    F = verify.MODULES["M3"].Fraction
    a, b = rng.sample([2, 3, 4, 5], 2)
    left = rng.choice([6, 8, 9, 10, 12])               # count remaining
    return {"type": "fraction_remainder",
            "stages": [["take_fraction", F(1, a)], ["take_fraction", F(1, b)]],
            "final": ["count", left]}


def _p_iterate_map(rng, base):                         # M6  (twin of 2024 Q29)
    return {"type": "iterate_map", "map": "digit_square_sum",
            "seed": rng.randint(1000, 9999), "index": rng.randint(1000, 9999)}


def _p_bounded_walk(rng, base):                        # M6  (twin of 2013 Q30)
    b = rng.choice([1, 2, 3])
    return {"type": "bounded_walk", "length": base["length"], "low": -b, "high": b, "start": 0}


def _p_count_digit_in_list(rng, base):                 # M5  (twin of 2024 Q28)
    step = rng.choice([3, 4, 5, 6])
    count = rng.choice([200, 250, 300])
    return {"type": "count_digit_in_list", "start": step, "step": step,
            "count": count, "digit": rng.choice([0, 1, 2])}


def _p_crt_candidates(rng, base):                      # M5  (twin of 2024 Q24)
    full = rng.choice([40, 48, 52, 60])
    m1, m2 = 4, rng.choice([5, 6])
    lost = rng.randint(1, 25)
    rem = full - lost
    r1, r2 = rem % m1, rem % m2
    cands = {lost}
    while len(cands) < 5:                              # decoys that fail at least one congruence
        c = rng.randint(1, 30)
        rr = full - c
        if c != lost and not (rr % m1 == r1 and rr % m2 == r2):
            cands.add(c)
    return {"type": "crt_candidates", "full": full, "mods": [[m1, r1], [m2, r2]],
            "candidates": sorted(cands)}


def _p_choose_sum_divisible(rng, base):                # M5  (twin of 2013 Q27)
    n = len(base["set"])                               # keep set size -> same band
    start = rng.choice([1, 2, 4, 5])
    return {"type": "choose_sum_divisible", "set": list(range(start, start + n)),
            "choose": 3, "divisor": rng.choice([2, 3, 4])}


_ROUTE_TRIPLES = [(24, 10, 13), (16, 12, 10), (40, 30, 25), (30, 16, 17), (18, 24, 15)]  # (a,b,half); base 8,6,5 excluded


def _p_route_inspection(rng, base):                   # M8  (twin of 2018 Q24)
    a, b, half = rng.choice(_ROUTE_TRIPLES)           # same topology (8 edges) -> same difficulty band
    return {"type": "route_inspection", "objective": "total",
            "nodes": ["H", "O", "M", "E", "X"],
            "edges": [["H", "O", a], ["M", "E", a], ["E", "H", b], ["O", "M", b],
                      ["H", "X", half], ["X", "M", half], ["E", "X", half], ["X", "O", half]],
            "_dims": [a, b, 2 * half]}


_CUBE_DIGITSETS = [[1, 2, 3], [0, 1, 3], [0, 2, 3], [1, 2, 4], [2, 3, 4]]


def _p_cube_opposite_sum(rng, base):                  # M8  (twin of 2018 Q27)
    from itertools import product as _prod
    digits = rng.choice(_CUBE_DIGITSETS)
    V = sorted(int("".join(map(str, c))) for c in _prod(digits, repeat=3) if c[0] != 0)
    sV = set(V)
    for _ in range(60):                               # build visibles guaranteed to admit a total
        T = rng.randint(2 * min(V), 2 * max(V))
        pairs = [(x, T - x) for x in V if x < T - x and (T - x) in sV]
        if len(pairs) >= 3:
            vis = sorted(x for x, _ in rng.sample(pairs, 3))
            if len(set(vis)) == 3:
                return {"type": "cube_opposite_sum", "digits": digits, "length": 3, "visible": vis}
    return {"type": "cube_opposite_sum", "digits": digits, "length": 3, "visible": sorted(rng.sample(V, 3))}


PROPOSERS = {
    "digit_extremes": _p_digit_extremes,
    "constrained_number": _p_constrained_number,
    "op_order": _p_op_order,
    "fraction_remainder": _p_fraction_remainder,
    "iterate_map": _p_iterate_map,
    "bounded_walk": _p_bounded_walk,
    "count_digit_in_list": _p_count_digit_in_list,
    "crt_candidates": _p_crt_candidates,
    "choose_sum_divisible": _p_choose_sum_divisible,
    "route_inspection": _p_route_inspection,
    "cube_opposite_sum": _p_cube_opposite_sum,
}


# ---------------------------------------------------------------- stems (English, fresh wording)
def _ord(seq):
    return ", ".join(str(x) for x in seq)


def _s_digit_extremes(p):
    digs = _ord(sorted(p["digits"]))
    g = p["groups"]
    if len(g) == 1:
        return (f"Pat has the digit cards {digs}. Using every card exactly once she makes a "
                f"single {g[0]}-digit number. What is the difference between the largest and "
                f"smallest numbers she can make?")
    return (f"Pat has the digit cards {digs}. Using every card exactly once she forms "
            f"{len(g)} numbers of {g[0]} digits each and adds them together. What is the "
            f"difference between the largest and smallest possible totals?")


_MULT_WORD = {3: "a multiple of 3", 4: "a multiple of 4", 6: "a multiple of 6", 9: "a multiple of 9"}


def _s_constrained_number(p):
    parts = []
    for pr in p["predicates"]:
        if pr == "even":
            parts.append("even")
        elif pr == "odd":
            parts.append("odd")
        elif pr == "all_distinct":
            parts.append("has all different digits")
        elif pr[0] == "multiple_of":
            parts.append(_MULT_WORD[pr[1]])
        elif pr[0] == "contains_digit":
            parts.append(f"contains the digit {pr[1]}")
        elif pr[0] == "no_digit":
            parts.append(f"has no digit {pr[1]}")
    return "What is the smallest three-digit number that is " + ", ".join(parts[:-1]) + \
           ", and " + parts[-1] + "?"


def _s_op_order(p):
    a = int(p["ops"][0][1]); c = int(p["ops"][2][1]); d = int(p["ops"][3][1])
    return (f"A counter starts at {p['start']}. Four machines each act on it exactly once: "
            f"machine A adds {a}; machine B doubles it; machine C halves it then adds {c}; "
            f"machine D doubles it then adds {d}. Used in the best order, what is the "
            f"largest value the counter can reach?")


def _s_fraction_remainder(p):
    a = p["stages"][0][1].denominator
    b = p["stages"][1][1].denominator
    left = p["final"][1]
    return (f"A tank of water is used in two stages: first 1/{a} of it is used, then 1/{b} "
            f"of what is left is used. Now {left} litres remain. How many litres were in "
            f"the tank at the start?")


def _s_iterate_map(p):
    return (f"Start with the number {p['seed']}. At each step replace the number with the "
            f"sum of the squares of its digits (for example 24 -> 2^2+4^2 = 20). "
            f"What is the {p['index']}th number in this list?")


def _s_bounded_walk(p):
    g = "goal" if p["high"] == 1 else "goals"
    return (f"Two teams play a match in which {p['length']} goals are scored in total. "
            f"At no time does either team lead by more than {p['high']} {g}. In how many "
            f"different orders can the {p['length']} goals be scored?")


def _s_count_digit_in_list(p):
    last = p["start"] + (p["count"] - 1) * p["step"]
    return (f"You write the {p['count']} numbers {p['start']}, {p['start'] + p['step']}, "
            f"{p['start'] + 2 * p['step']}, ... up to {last}. How many times do you write "
            f"the digit '{p['digit']}'?")


def _s_crt_candidates(p):
    (m1, r1), (m2, r2) = p["mods"]
    return (f"A box held {p['full']} counters but some were lost. When the rest are shared "
            f"equally among {m1} people, {r1} are left over; shared among {m2} people, {r2} "
            f"are left over. Which of these could be the number lost: {_ord(p['candidates'])}?")


def _s_choose_sum_divisible(p):
    s = p["set"]
    return (f"In how many ways can you choose {p['choose']} different numbers from "
            f"{s[0]} to {s[-1]} so that their sum is a multiple of {p['divisor']}?")


def _s_route_inspection(p):
    a, b, hyp = p["_dims"]
    return (f"A rectangular field is {a} km by {b} km. Fences run along all four sides and along "
            f"both diagonals, which cross at the centre (each diagonal is {hyp} km long). A farmer "
            f"starts at one corner, walks along every fence at least once, and returns to that same "
            f"corner. What is the shortest total distance, in kilometres, she can walk?")


def _s_cube_opposite_sum(p):
    ds = ", ".join(map(str, p["digits"]))
    v = p["visible"]
    return (f"Using only the digits {ds}, each face of a cube shows a different {p['length']}-digit "
            f"number. The three faces meeting at one corner show {v[0]}, {v[1]} and {v[2]}. The two "
            f"numbers on each pair of opposite faces add to the same total. What is the largest that "
            f"this total could be?")


STEMS = {
    "digit_extremes": _s_digit_extremes,
    "constrained_number": _s_constrained_number,
    "op_order": _s_op_order,
    "fraction_remainder": _s_fraction_remainder,
    "iterate_map": _s_iterate_map,
    "bounded_walk": _s_bounded_walk,
    "count_digit_in_list": _s_count_digit_in_list,
    "crt_candidates": _s_crt_candidates,
    "choose_sum_divisible": _s_choose_sum_divisible,
    "route_inspection": _s_route_inspection,
    "cube_opposite_sum": _s_cube_opposite_sum,
}


# ----- ★ crowned Year-6-fastest method + the trap (from docs/AMC-KNOWLEDGE-BASE.md)
METHOD = {
    "M1": ("Sort the digits into columns by place value — biggest digits to the biggest "
           "columns; the split into separate numbers is a distraction (the middle columns "
           "cancel in a difference).", "tracking the whole numbers instead of the columns."),
    "M2": ("Apply the constraints in order of pruning power (divisibility / parity first) "
           "while keeping the leading digit as small as possible.",
           "applying the weak constraints first, or dropping the distinct / no-zero filters."),
    "M3": ("Defer the doublings to last (a ×2 multiplies everything gained so far); do the "
           "value-shrinking step early.", "multiplying too early."),
    "M4": ("Reverse the chain — start at the end and undo each step with its inverse, last "
           "step first.", "reporting an intermediate value of the reverse chain as the answer."),
    "M5": ("Bucket by remainder (or build an ordered table): count all-from-one-bucket PLUS "
           "one-from-each — no missing or double counts.",
           "forgetting a case, or counting ordered when it should be unordered."),
    "M6": ("Find the cycle, then index the far-out term by its period (don't grind out every "
           "term).", "an off-by-one in where the cycle starts, or not noticing it repeats."),
    "M8": ("Count how many fences meet at each junction: if any has an ODD number you cannot do "
           "it without repeats. Pair up the odd junctions and re-walk only the cheapest connecting "
           "fences; answer = total fence length + that minimum extra.",
           "just adding up all the fences and forgetting you must double back on the odd junctions."),
}

# per-TYPE overrides (one mechanism can hold several families with different methods/traps)
METHOD_BY_TYPE = {
    "cube_opposite_sum": (
        "List the allowed numbers; for each candidate total T, check whether all three hidden "
        "faces (T minus each visible number) are themselves allowed and all different. Take the "
        "largest T that works.",
        "assuming the three visible faces can be opposite each other — they meet at a corner, so "
        "they are adjacent; their opposites are the three hidden faces."),
}


def make_item(anchor_key, seed=0, max_tries=25):
    """Propose a verified twin of REGISTRY[anchor_key]; return an item dict or None."""
    mech, base = REGISTRY[anchor_key]
    typ = base["type"]
    if typ not in PROPOSERS:
        raise ValueError(f"{typ} is not a generatable family (curate instead)")
    marks = _MARKS[anchor_key]
    anchor_answer = verify.MODULES[mech].solve(base)    # the real question's answer
    rng = random.Random(seed * 1000 + hash(anchor_key) % 997)
    for _ in range(max_tries):
        params = PROPOSERS[typ](rng, base)
        if params == base:                              # never reproduce the real numbers
            continue
        v = verify.verify(mech, params, marks, _BANDS)
        # a genuine twin: passes the gate AND is not just the anchor's own answer re-skinned
        if v["ok"] and v["answer"] != anchor_answer:
            m_star, m_trap = METHOD_BY_TYPE.get(typ, METHOD[mech])
            return {"mechanism": mech, "anchor": f"{anchor_key[0]} Q{anchor_key[1]}",
                    "marks": marks, "type": typ, "params": params,
                    "stem": STEMS[typ](params), "answer": v["answer"],
                    "difficulty": v["difficulty"], "band": v["band"], "unique": v["unique"],
                    "method_star": m_star, "trap": m_trap}
    return None


if __name__ == "__main__":   # self-test: 5 distinct verified twins of one mechanism
    anchor = (2024, 26)
    print(f"=== 5 verified twins of {anchor[0]} Q{anchor[1]} (M1, place-value extreme) ===\n")
    seen = set()
    i = 0
    s = 0
    while i < 5:
        it = make_item(anchor, seed=s); s += 1
        if it is None or it["stem"] in seen:
            continue
        seen.add(it["stem"]); i += 1
        print(f"[{i}] twin of {it['anchor']}  ({it['mechanism']}, {it['marks']} marks)")
        print(f"    Q: {it['stem']}")
        print(f"    answer = {it['answer']}   unique = {it['unique']}   "
              f"difficulty {it['difficulty']} in band {it['band']}\n")
