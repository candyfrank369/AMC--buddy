"""M4 — Working backwards.

Families
--------
- affine_chain      : forward ops x -> a*x+b applied in order; given the end value,
                      recover the start by inverting in reverse.   (2009 Q2, 2013 Q8)
- fraction_remainder: a quantity is reduced by stages ('take_fraction' f, or
                      'take_count' c); given the final amount (count or fraction of
                      start), recover the start.                    (2022 Q17, 2025 Q22)
- temples           : cross-river-doubles before each of t temples, place the same
                      number each time, 0 left; minimum start.      (2009 Q30)
- consecutive_dates : n consecutive dates summing to S from a known weekday; answer a
                      derived date (e.g. last Friday of the month). (2025 Q23)
"""
from fractions import Fraction
import random

_WD = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _affine_chain(params):
    end = Fraction(params["end"])
    x = end
    for a, b in reversed(params["ops"]):
        x = (x - Fraction(b)) / Fraction(a)        # invert a*x+b
    return int(x) if x.denominator == 1 else x


def _fraction_remainder(params):
    # track remaining = coef * T + const (T = start)
    coef, const = Fraction(1), Fraction(0)
    for kind, v in params["stages"]:
        if kind == "take_fraction":                # remove fraction v of what's left
            coef *= (1 - Fraction(v)); const *= (1 - Fraction(v))
        elif kind == "take_count":                 # remove v items
            const -= Fraction(v)
        else:
            raise ValueError(kind)
    fkind, fval = params["final"]
    if fkind == "count":                           # coef*T + const = fval
        T = (Fraction(fval) - const) / coef
    elif fkind == "fraction":                      # coef*T + const = fval*T
        T = const / (Fraction(fval) - coef)
    else:
        raise ValueError(fkind)
    return int(T) if T.denominator == 1 else T


def _temples(params):
    # cross-river-doubles before each of t temples, place the same f each time, 0 left:
    #   2^t * S = (2^t - 1) * f   ->   f = 2^t * S / (2^t - 1).  Want the min start S.
    t = params["temples"]
    s = 1
    while True:
        f = Fraction(2 ** t * s, 2 ** t - 1)
        if f.denominator == 1 and f > 0:
            return s
        s += 1


def _consecutive_dates(params):
    n, total = params["count"], params["sum"]
    d1 = Fraction(total - n * (n - 1) // 2, n)     # first date
    assert d1.denominator == 1
    d1 = int(d1)
    if params.get("ask") == "last_weekday":
        start_idx = _WD.index(params["start_weekday"])
        target_idx = _WD.index(params["target_weekday"])
        offset = (target_idx - start_idx) % 7
        first = d1 + offset                        # first target-weekday date
        last = first
        while last + 7 <= params.get("days_in_month", 31):
            last += 7
        return last
    return d1


_DISPATCH = {
    "affine_chain": _affine_chain,
    "fraction_remainder": _fraction_remainder,
    "temples": _temples,
    "consecutive_dates": _consecutive_dates,
}


def solve(params):
    return _DISPATCH[params["type"]](params)


def difficulty(params):
    """Proxy = length of the chain to invert."""
    t = params["type"]
    if t == "affine_chain":
        return len(params["ops"])
    if t == "fraction_remainder":
        return len(params["stages"])
    if t == "temples":
        return params["temples"]
    return params.get("count", 3)


def generate(seed):
    rng = random.Random(seed)
    ops, x = [], rng.randint(2, 12)
    for _ in range(rng.choice([2, 3])):
        if rng.random() < 0.5:
            ops.append((2, rng.choice([2, 5])))
        else:
            ops.append((Fraction(1, 2), rng.choice([-2, 1])))
    end = x
    for a, b in ops:
        end = Fraction(a) * end + Fraction(b)
    return {"type": "affine_chain", "ops": ops, "end": end}
