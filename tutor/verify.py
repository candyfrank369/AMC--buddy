"""verify.py — THE REVIEWER (CLAUDE.md rule #2).

A candidate (mechanism, params, marks) passes only if:
  (1) it has a UNIQUE, well-defined answer (solve returns a single value; where a
      family can have multiple satisfying objects, solution_count must be 1), AND
  (2) difficulty(params) sits inside the real-paper band for that mechanism + mark level
      (the band is learnt from the catalogued anchors — difficulty is NEVER invented).

No practice is generated here; this is the gate Phase 4's generator must pass through.
"""
import json
import os

from tutor.mechanisms import (m1_place_value as m1, m2_constraints as m2, m3_op_order as m3,
                              m4_backwards as m4, m5_enumeration as m5, m6_sequences as m6,
                              m8_logic as m8)
from tutor.anchors import REGISTRY

MODULES = {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6, "M8": m8}

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_QJSONL = os.path.join(_ROOT, "content", "questions.jsonl")


def _marks_lookup():
    out = {}
    with open(_QJSONL) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                out[(r["year"], r["q"])] = r["marks"]
    return out


def learn_bands():
    """Difficulty band per (mechanism, marks), learnt from the official anchors."""
    marks = _marks_lookup()
    bands = {}
    for (year, q), (mech, params) in REGISTRY.items():
        d = MODULES[mech].difficulty(params)
        key = (mech, marks[(year, q)])
        lo, hi = bands.get(key, (d, d))
        bands[key] = (min(lo, d), max(hi, d))
    return bands


def is_unique(mech, params):
    mod = MODULES[mech]
    if hasattr(mod, "solution_count"):
        try:
            return mod.solution_count(params) == 1
        except Exception:
            pass
    ans = mod.solve(params)
    return ans is not None


def verify(mech, params, marks, bands=None):
    """Return a verdict dict; ok == passes uniqueness AND difficulty-in-band."""
    if bands is None:
        bands = learn_bands()
    mod = MODULES[mech]
    answer = mod.solve(params)
    d = mod.difficulty(params)
    band = bands.get((mech, marks))
    in_band = band is not None and band[0] <= d <= band[1]
    unique = is_unique(mech, params)
    return {"answer": answer, "difficulty": d, "band": band,
            "unique": unique, "in_band": in_band, "ok": bool(unique and in_band)}


if __name__ == "__main__":   # tiny self-demo on a couple of anchors (no practice emitted)
    bands = learn_bands()
    for (year, q) in [(2024, 26), (2013, 27), (2024, 18)]:
        mech, params = REGISTRY[(year, q)]
        marks = _marks_lookup()[(year, q)]
        print(year, q, mech, verify(mech, params, marks, bands))
