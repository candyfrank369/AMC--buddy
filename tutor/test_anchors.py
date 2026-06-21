"""Phase-2 proof: for EVERY catalogued OFFICIAL M1-M6 anchor, solve(params) must
reproduce the official answer recorded in content/questions.jsonl.

Run: python -m tutor.test_anchors
Prints PASS / FAIL / FLAG (deliberately-not-modelled) / MISSING (registry gap) and a
coverage summary, then exits non-zero if any FAIL or MISSING.
"""
import json
import os
import re
import sys

from tutor.mechanisms import (m1_place_value as m1, m2_constraints as m2, m3_op_order as m3,
                              m4_backwards as m4, m5_enumeration as m5, m6_sequences as m6)
from tutor.anchors import REGISTRY, FLAGGED

MODULES = {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6}
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_official():
    """(year,q) -> (mechanism, expected_string) for official M1-M6 anchors."""
    out = {}
    with open(os.path.join(_ROOT, "content", "questions.jsonl")) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["mechanism"] in MODULES and r["answer_provenance"] == "official" and r["answer"] is not None:
                m = re.search(r"\(=\s*([^)]+?)\s*\)", r["stem_summary"])
                expected = m.group(1) if m else None
                out[(r["year"], r["q"])] = (r["mechanism"], expected)
    return out


def matches(result, expected):
    """Compare solver output to the corpus's '(=...)' value, robustly."""
    if expected is None:
        return False
    digits = re.sub(r"[^0-9]", "", expected)          # '28th' -> '28', '792' -> '792'
    if isinstance(result, list):                       # set-valued (e.g. 'could be')
        return digits != "" and int(digits) in result
    if isinstance(result, str):
        return result == expected
    if digits != "":
        return result == int(digits)
    return str(result) == expected


def main():
    official = load_official()
    passed, failed, flagged, missing = [], [], [], []
    for (year, q), (mech, expected) in sorted(official.items()):
        key = (year, q)
        if key in FLAGGED:
            flagged.append((key, mech, expected, FLAGGED[key]))
            continue
        if key not in REGISTRY:
            missing.append((key, mech, expected))
            continue
        rmech, params = REGISTRY[key]
        try:
            result = MODULES[rmech].solve(params)
        except Exception as e:
            failed.append((key, mech, expected, f"EXC {e!r}"))
            continue
        if matches(result, expected):
            passed.append((key, mech, expected, result))
        else:
            failed.append((key, mech, expected, result))

    w = lambda s: print(s)
    w("=" * 72)
    w("PHASE 2 ANCHOR PROOF  —  official M1-M6  ==  solve(params)")
    w("=" * 72)
    for key, mech, exp, res in passed:
        w(f"PASS  {mech} {key[0]} Q{key[1]:<2}  official={exp:<6} computed={res}")
    for key, mech, exp, res in failed:
        w(f"FAIL  {mech} {key[0]} Q{key[1]:<2}  official={exp:<6} computed={res}")
    for key, mech, exp, why in flagged:
        w(f"FLAG  {mech} {key[0]} Q{key[1]:<2}  official={exp:<6} (not modelled: {why[:60]}...)")
    for key, mech, exp in missing:
        w(f"MISS  {mech} {key[0]} Q{key[1]:<2}  official={exp}  (no registry entry!)")

    total = len(official)
    w("-" * 72)
    w(f"official anchors: {total}   PASS {len(passed)}   FAIL {len(failed)}   "
      f"FLAG {len(flagged)}   MISSING {len(missing)}")
    by_mech = {}
    for (year, q), (mech, _) in official.items():
        d = by_mech.setdefault(mech, [0, 0])
        d[1] += 1
        if (year, q) in {k for k, *_ in [(p[0],) for p in passed]}:
            pass
    # per-mechanism pass tally
    pset = {k for k, *_ in passed}
    tally = {}
    for (year, q), (mech, _) in official.items():
        t = tally.setdefault(mech, [0, 0])
        t[1] += 1
        if (year, q) in pset:
            t[0] += 1
    w("per mechanism (passed/total): " + "  ".join(f"{m}={t[0]}/{t[1]}" for m, t in sorted(tally.items())))
    w("=" * 72)
    return 1 if (failed or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
