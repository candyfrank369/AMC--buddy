"""M1 — Place-value extreme value.

Form k numbers by partitioning a digit multiset into groups (highest place first),
the *value* of an arrangement is the SUM of those numbers; report max / min / their
difference. The insight the mechanism tests: only the column weights matter.

Anchors reproduced: 2010 Q8 (=495), 2013 Q5 (=41976), 2024 Q26 (=792).
"""
from itertools import permutations
import random


def _value(perm, groups):
    total, i = 0, 0
    for g in groups:
        num = 0
        for _ in range(g):
            num = num * 10 + perm[i]
            i += 1
        total += num
    return total


def solve(params):
    assert params["type"] == "digit_extremes"
    digits, groups = params["digits"], params["groups"]
    assert sum(groups) == len(digits), "groups must use every digit once"
    vals = {_value(p, groups) for p in set(permutations(digits))}
    obj = params.get("objective", "diff")
    if obj == "maxsum":
        return max(vals)
    if obj == "minsum":
        return min(vals)
    return max(vals) - min(vals)          # 'diff'


def difficulty(params):
    """Proxy = number of digits placed (the count of weighted columns to juggle)."""
    return len(params["digits"])


def generate(seed):
    rng = random.Random(seed)
    n = rng.choice([4, 5, 6])
    digits = rng.sample(range(1, 10), n)
    # split n digits into 1 or 2 groups of (near) equal length
    if n % 2 == 0 and rng.random() < 0.5:
        groups = [n // 2, n // 2]
    else:
        groups = [n]
    return {"type": "digit_extremes", "digits": digits, "groups": groups, "objective": "diff"}
