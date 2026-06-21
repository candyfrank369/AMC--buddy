"""mock.py — assemble a full TAIL mock: an English STUDENT PAPER + a PARENT ANSWER KEY.

The prize (CLAUDE.md) is decided by the hard tail, so the mock is the discriminator tail:
one verified twin per anchor, spanning M1-M6. Every item is produced by generate.make_item
(proposer -> verify.py gate), so nothing appears unless it has a UNIQUE answer inside the
real-paper difficulty band. The parent key gives, per question, the answer, the mechanism
tag, the ★ crowned Year-6-fastest method, and the named trap.

CLI:  python -m tutor.mock
"""
from tutor import generate

# Tail anchors to twin, in increasing mark order — spans all six mechanisms.
# (single-parameter families such as stepping_stones are CURATED, not generated, so are
# intentionally absent — see generate.py.)
MOCK_PLAN = [
    (2025, 22),   # M4  fraction_remainder   5 marks
    (2024, 24),   # M5  crt_candidates       5 marks
    (2024, 26),   # M1  digit_extremes       6 marks
    (2025, 26),   # M2  constrained_number   6 marks
    (2013, 27),   # M5  choose_sum_divisible 7 marks
    (2024, 27),   # M3  op_order             7 marks
    (2024, 28),   # M5  count_digit_in_list  8 marks
    (2024, 29),   # M6  iterate_map          9 marks
    (2013, 30),   # M6  bounded_walk        10 marks
]


def build_mock():
    items = []
    for anchor in MOCK_PLAN:
        for seed in range(60):                  # tiny bounded search; proposers stay in band
            it = generate.make_item(anchor, seed=seed)
            if it is not None:
                items.append(it)
                break
        else:
            raise RuntimeError(f"could not produce a verified twin for {anchor}")
    return items


def render(items):
    out = []
    out.append("=" * 78)
    out.append("AMC-buddy MOCK — UPPER PRIMARY TAIL  ·  STUDENT PAPER")
    out.append("Whole-number / short answers.  Diagrams are not drawn to scale.")
    out.append("=" * 78)
    for i, it in enumerate(items, 1):
        out.append(f"\n{i}.  [{it['marks']} marks]")
        out.append("    " + it["stem"])

    out.append("\n\n" + "=" * 78)
    out.append("PARENT ANSWER KEY  (mechanism · answer · ★ fastest method · the trap)")
    out.append("each item below was checked by verify.py before printing")
    out.append("=" * 78)
    for i, it in enumerate(items, 1):
        out.append(f"\n{i}.  answer = {it['answer']}      [{it['mechanism']}, "
                   f"{it['marks']} marks · twin of {it['anchor']}]")
        out.append(f"    ★ fastest method: {it['method_star']}")
        out.append(f"    ✗ the trap: {it['trap']}")
        out.append(f"    (verifier: unique={it['unique']}, difficulty {it['difficulty']} "
                   f"in band {it['band']})")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    print(render(build_mock()))
