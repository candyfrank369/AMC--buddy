"""M2 — Stacked-constraint number (incl. divisibility, cryptarithms, bracketing).

Each anchor is a small constraint-satisfaction / search problem; code enumerates and
returns the unique answer. Families are dispatched on params['type']:

  constrained_number  smallest/largest/count satisfying named predicates (2025 Q26=576,
                      2011 Q26=336, 2024 Q18=14)
  int_set_sum_product positive ints with given sum & product, return max  (2009 Q16=7)
  two_digit_reverse   count 2-digit n with n+reverse=target              (2010 Q21=7)
  consecutive_product k consecutive ints with given product, return sum  (2010 Q28=69)
  digit_append        append a digit both ends -> +increase; find x      (2010 Q29=87)
  cryptarithm_addition column addition with lettered boxes; sum of boxes (2011 Q21=23)
  two_digit_property  2-digit n = first digit + (second digit)^2         (2011 Q27=89)
  paul_ages           age product + kids' sum = target; value yrs before (2011 Q29=997)
  remove_plus         drop one '+' to merge two cards; the merged number (2012 Q16=65)
  crossnumber_reverse cross-number digit-sum via 11*(x+y) palindrome      (2012 Q23=11)
  product_bracket     n(n+gap) just at/under bound; product now          (2013 Q19=992)
  harmonic_shares     combined=ab/(a-b) per-other                        (2013 Q22=15)
  ascending_times     largest ascending number whose *mult is descending (2013 Q29=168)
  not_possible_total  which candidate total can't realise all %          (2025 Q16=25)
"""
from itertools import combinations_with_replacement, product as iproduct, permutations
import random


# ---------- predicates for constrained_number ----------
def _digits(n):
    return [int(c) for c in str(n)]


def _pred(name_arg, n):
    if isinstance(name_arg, (list, tuple)):
        name, arg = name_arg[0], name_arg[1]
    else:
        name, arg = name_arg, None
    d = _digits(n)
    if name == "multiple_of":
        return n % arg == 0
    if name == "even":
        return n % 2 == 0
    if name == "odd":
        return n % 2 == 1
    if name == "contains_digit":
        return arg in d
    if name == "no_digit":
        return arg not in d
    if name == "all_distinct":
        return len(set(d)) == len(d)
    if name == "num_odd_digits":
        return sum(1 for x in d if x % 2 == 1) == arg
    if name == "digit_sum_multiple":
        return sum(d) % arg == 0
    if name == "divisible_by_unit_digit":
        u = n % 10
        return u != 0 and n % u == 0
    raise ValueError(name)


def _constrained_number(p):
    lo, hi = p.get("range", [1, 10 ** 7])
    preds = p["predicates"]
    want = p["want"]
    hits = (n for n in range(lo, hi + 1) if all(_pred(pr, n) for pr in preds))
    if want == "smallest":
        return next(hits, None)              # None = no satisfier (verify rejects; never crash)
    if want == "count":
        return sum(1 for _ in hits)
    if want == "largest":
        seq = list(hits)
        return max(seq) if seq else None
    raise ValueError(want)


def _int_set_sum_product(p):
    n, S, P = p["n"], p["total_sum"], p["total_product"]
    sols = []
    for combo in combinations_with_replacement(range(1, S), n):
        if sum(combo) == S:
            pr = 1
            for x in combo:
                pr *= x
            if pr == P:
                sols.append(combo)
    assert len({tuple(sorted(s)) for s in sols}) == 1, "non-unique"
    return max(sols[0]) if p.get("want", "max") == "max" else min(sols[0])


def _two_digit_reverse(p):
    return sum(1 for n in range(10, 100) if n + int(str(n)[::-1]) == p["target"])


def _consecutive_product(p):
    k, P = p["k"], p["product"]
    n = 1
    while True:
        run = list(range(n, n + k))
        pr = 1
        for x in run:
            pr *= x
        if pr == P:
            return sum(run)
        if pr > P:
            return None
        n += 1


def _digit_append(p):
    dig, inc = p["digit"], p["increase"]
    for x in range(1, 10 ** 6):
        L = len(str(x))
        new = dig * 10 ** (L + 1) + x * 10 + dig
        if new - x == inc:
            return x
    return None


def _value(tokens, assign):
    v = 0
    for t in tokens:
        v = v * 10 + (t if isinstance(t, int) else assign[t])
    return v


def _cryptarithm_addition(p):
    addends, result, boxes = p["addends"], p["result"], p["boxes"]
    names = sorted({t for grp in addends + [result] for t in grp if isinstance(t, str)})
    leads = {grp[0] for grp in addends + [result] if isinstance(grp[0], str) and len(grp) > 1}
    box_sums = set()
    for vals in iproduct(range(10), repeat=len(names)):
        assign = dict(zip(names, vals))
        if any(assign[l] == 0 for l in leads):
            continue
        if sum(_value(a, assign) for a in addends) == _value(result, assign):
            box_sums.add(sum(assign[b] for b in boxes))
    assert len(box_sums) == 1, f"box-sum not invariant: {box_sums}"
    return box_sums.pop()


def _two_digit_property(p):
    # n = first_digit + (second_digit)^2
    out = [n for n in range(10, 100) if n == (n // 10) + (n % 10) ** 2]
    assert len(out) == 1
    return out[0]


def _paul_ages(p):
    target, gap, nk, kg, yb = (p["target"], p["parent_gap"], p["num_kids"],
                               p["kid_gap"], p["years_before"])
    for parent in range(target, 1, -1):           # larger parent first
        prod = parent * (parent - gap)
        if prod > target:
            continue
        rem = target - prod                       # = sum of kids' ages
        # kids: nk consecutive (step kg) ages m, m+kg, ...; sum = nk*m + kg*(0+..+nk-1)
        base = kg * sum(range(nk))
        if (rem - base) % nk:
            continue
        m = (rem - base) // nk
        kids = [m + kg * i for i in range(nk)]
        if m >= 1 and max(kids) < parent - gap:   # kids younger than the younger parent
            P2 = (parent - yb) * (parent - gap - yb)
            return P2 + sum(k - yb for k in kids)
    return None


def _remove_plus(p):
    seq, target = p["sequence"], p["target"]
    base = sum(seq)
    for i in range(len(seq) - 1):
        merged = 10 * seq[i] + seq[i + 1]
        if base - seq[i] - seq[i + 1] + merged == target:
            return merged
    return None


def _crossnumber_reverse(p):
    # 1-down = 11*(x+y) is 3-digit with tens digit 2; 7-down = x+y
    out = {s for s in range(2, 19) if 100 <= 11 * s <= 999 and (11 * s // 10) % 10 == 2}
    assert len(out) == 1
    return out.pop()


def _product_bracket(p):
    gap, bound = p["gap"], p["bound"]
    m = 1
    while not (m * (m + gap) <= bound < (m + 1) * (m + 1 + gap)):
        m += 1
    return m * (m + gap)


def _harmonic_shares(p):
    a, b = p["one_class"], p["combined"]
    return a * b // (a - b)


def _ascending_times(p):
    nd, mult = p["ndigits"], p["mult"]
    best = None
    lo, hi = 10 ** (nd - 1), 10 ** nd
    for n in range(lo, hi):
        s = str(n)
        if list(s) == sorted(s) and len(set(s)) == nd:        # strictly ascending distinct
            t = str(n * mult)
            if list(t) == sorted(t, reverse=True) and len(set(t)) == len(t):
                best = n
    return best


def _not_possible_total(p):
    import math
    pcts = p["percentages"]
    need = 1
    for q in pcts:                                # N*q/100 integer for all q
        need = math.lcm(need, 100 // math.gcd(100, q))
    bad = [c for c in p["candidates"] if c % need != 0]
    assert len(bad) == 1
    return bad[0]


_DISPATCH = {
    "constrained_number": _constrained_number,
    "int_set_sum_product": _int_set_sum_product,
    "two_digit_reverse": _two_digit_reverse,
    "consecutive_product": _consecutive_product,
    "digit_append": _digit_append,
    "cryptarithm_addition": _cryptarithm_addition,
    "two_digit_property": _two_digit_property,
    "paul_ages": _paul_ages,
    "remove_plus": _remove_plus,
    "crossnumber_reverse": _crossnumber_reverse,
    "product_bracket": _product_bracket,
    "harmonic_shares": _harmonic_shares,
    "ascending_times": _ascending_times,
    "not_possible_total": _not_possible_total,
}


def solve(params):
    return _DISPATCH[params["type"]](params)


def solution_count(params):
    """Whether the *asked answer* is well-defined and unique (for verify.py).
    'count' is always single-valued; 'smallest'/'largest' need >=1 satisfier."""
    if params["type"] == "constrained_number":
        if params["want"] == "count":
            return 1
        lo, hi = params.get("range", [1, 10 ** 6])
        n_sat = sum(1 for n in range(lo, hi + 1)
                    if all(_pred(pr, n) for pr in params["predicates"]))
        return 1 if n_sat >= 1 else 0
    return 1


def difficulty(params):
    t = params["type"]
    if t == "constrained_number":
        return len(params["predicates"])
    return 3


def generate(seed):
    rng = random.Random(seed)
    preds = [["multiple_of", rng.choice([3, 9])], rng.choice(["even", "odd"]),
             "all_distinct", ["no_digit", 0]]
    return {"type": "constrained_number", "range": [100, 999], "want": "smallest", "predicates": preds}
