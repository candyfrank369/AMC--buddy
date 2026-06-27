"""Self-check for the generator (regression guard).

Exits non-zero if:
  (1) an infeasible constrained_number raises instead of returning None, or
  (2) make_item crashes on any generatable anchor/seed, or
  (3) make_item ever emits an item that does not actually pass verify.

Run:  python -m tutor.test_generate
"""
from tutor import generate, verify
from tutor.anchors import REGISTRY
from tutor.mechanisms import m2_constraints as m2


def main():
    fails = 0

    # (0) M8 anchor reproduction: the real 2018 Q24 farm must compute to 60
    from tutor.anchors import REGISTRY as REG
    for key, want in [((2018, 24), 60), ((2018, 27), 321)]:
        mech8, base8 = REG[key]
        got8 = verify.MODULES[mech8].solve(base8)
        if got8 == want:
            print(f"PASS  M8 anchor {key[0]} Q{key[1]} {base8['type']} -> {want}")
        else:
            fails += 1; print(f"FAIL  M8 {key} should be {want}, got {got8}")

    # (1) infeasible constraints must return None, never raise
    bad = {"type": "constrained_number", "range": [100, 999], "want": "smallest",
           "predicates": ["odd", ["multiple_of", 4]]}      # odd AND multiple of 4 = impossible
    try:
        r = m2.solve(bad)
        if r is None:
            print("PASS  infeasible constrained_number -> None (no crash)")
        else:
            fails += 1; print(f"FAIL  infeasible should be None, got {r}")
    except Exception as e:
        fails += 1; print(f"FAIL  infeasible raised {e!r}")

    # (2)+(3) every generatable anchor: make_item never crashes; emitted items verify-ok
    bands = verify.learn_bands()
    marks = verify._marks_lookup()
    anchors = [k for k, (mech, base) in REGISTRY.items() if base["type"] in generate.PROPOSERS]
    emitted = 0
    for ak in anchors:
        for s in range(10):
            try:
                it = generate.make_item(ak, seed=s)
            except Exception as e:
                fails += 1; print(f"FAIL  make_item crashed on {ak} seed={s}: {e!r}"); continue
            if it is None:
                continue
            v = verify.verify(it["mechanism"], it["params"], marks[ak], bands)
            emitted += 1
            if not v["ok"]:
                fails += 1; print(f"FAIL  {ak} seed={s} emitted but verify not ok: {v}")
    print(f"PASS  {emitted} generated twins across {len(anchors)} anchors all verify-ok"
          if fails == 0 else f"--- {fails} failure(s) ---")
    raise SystemExit(1 if fails else 0)


if __name__ == "__main__":
    main()
