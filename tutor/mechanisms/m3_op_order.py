"""M3 — Non-commutative operation ordering.

A bag of affine operations x -> a*x + b, each used once; choose the order that
maximises (or minimises) the final value from a given start.

Anchor reproduced: 2024 Q27 (=270).
"""
from fractions import Fraction
from itertools import permutations
import random


def _apply(start, order):
    x = Fraction(start)
    for a, b in order:
        x = Fraction(a) * x + Fraction(b)
    return x


def solve(params):
    assert params["type"] == "op_order"
    start = params["start"]
    ops = [tuple(o) for o in params["ops"]]          # list of (a, b)
    obj = params.get("objective", "max")
    vals = [_apply(start, list(p)) for p in permutations(ops)]
    best = max(vals) if obj == "max" else min(vals)
    # answers are dollar amounts -> integer when the data is integral
    return int(best) if best.denominator == 1 else best


def difficulty(params):
    """Proxy = number of operations to order (search space is n!)."""
    return len(params["ops"])


def generate(seed):
    rng = random.Random(seed)
    n = rng.choice([3, 4])
    ops = []
    kinds = rng.sample(["add", "mul", "halfadd", "muladd"], n)
    for k in kinds:
        if k == "add":
            ops.append((1, rng.choice([5, 10, 20])))
        elif k == "mul":
            ops.append((2, 0))
        elif k == "halfadd":
            ops.append((Fraction(1, 2), rng.choice([40, 50])))
        else:
            ops.append((2, rng.choice([5, 10])))
    return {"type": "op_order", "start": rng.choice([5, 10]), "ops": ops, "objective": "max"}
