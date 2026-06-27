"""paper_ingest.py — turn a REAL completed paper into structured diagnosis input.

Closes the missing link: a real paper is just answers on paper; this maps each question to
its catalogued (mechanism, band, marks, OFFICIAL answer) from content/questions.jsonl, marks
the student's answers against the official key (code is the authority, not hand-marking), and
produces a per-mechanism / per-band weakness profile that diagnose.py can act on.

Questions whose official answer is not in the corpus (answer == null) are reported as UNKEYED
and never guessed.

Run the built-in demo (Frank's real 2018 Upper Primary paper):  python -m tutor.paper_ingest
"""
import json
import os
import collections

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_QJSONL = os.path.join(_ROOT, "content", "questions.jsonl")


def _norm(a):
    return str(a).strip().upper() if a is not None else None


def load_paper(year):
    rows = {}
    with open(_QJSONL) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["year"] == year:
                rows[r["q"]] = r
    if not rows:
        raise ValueError(f"year {year} not in corpus")
    return rows


def mark_paper(year, answers):
    """answers: {q -> student's answer}. Returns a structured marked report."""
    rows = load_paper(year)
    per_q, by_mech, by_band = [], {}, {}
    earned = keyed_total = full_total = 0
    unkeyed = []
    for q in sorted(rows):
        r = rows[q]
        marks = r["marks"]
        full_total += marks
        official = r["answer"]
        mech = r["mechanism"] or "(easy/untagged)"
        band = r["band"]
        stud = answers.get(q)
        if official is None:                       # not in official key — never guess
            unkeyed.append(q)
            per_q.append(dict(q=q, marks=marks, band=band, mechanism=mech,
                              official=None, student=stud, result="UNKEYED", earned=0))
            continue
        keyed_total += marks
        right = _norm(stud) == _norm(official)
        earned += marks if right else 0
        per_q.append(dict(q=q, marks=marks, band=band, mechanism=mech, official=official,
                          student=stud, result="OK" if right else "WRONG",
                          earned=marks if right else 0))
        bm = by_mech.setdefault(mech, [0, 0, 0]); bm[0] += int(right); bm[1] += 1; bm[2] += marks * (not right)
        bb = by_band.setdefault(band, [0, 0, 0]); bb[0] += int(right); bb[1] += 1; bb[2] += marks * (not right)
    wrong = [d["q"] for d in per_q if d["result"] == "WRONG"]
    weak_mech = sorted((m for m, (c, n, lost) in by_mech.items() if c < n),
                       key=lambda m: -by_mech[m][2])
    return dict(year=year, per_q=per_q, earned=earned, keyed_total=keyed_total,
                full_total=full_total, wrong=wrong, unkeyed=unkeyed,
                by_mech=by_mech, by_band=by_band, weak_mech=weak_mech)


def render(rep):
    out = [f"AMC {rep['year']} Upper Primary — auto-marked against the official key",
           f"Score (keyed): {rep['earned']} / {rep['keyed_total']}"
           + (f"   (full paper {rep['full_total']}; {len(rep['unkeyed'])} questions UNKEYED in corpus: "
              f"{', '.join('Q'+str(q) for q in rep['unkeyed'])})" if rep['unkeyed'] else ""),
           ""]
    out.append(f"{'Q':>3} {'band':8} {'mk':>3} {'mech':>14} {'official':>9} {'student':>8}  result")
    for d in rep["per_q"]:
        out.append(f"{d['q']:>3} {d['band']:8} {d['marks']:>3} {str(d['mechanism']):>14} "
                   f"{str(d['official']):>9} {str(d['student']):>8}  {d['result']}")
    out.append("")
    out.append("Wrong (keyed): " + (", ".join("Q" + str(q) for q in rep["wrong"]) or "none"))
    out.append("By mechanism (correct/seen, marks lost): " +
               "  ".join(f"{m} {c}/{n}(-{lost})" for m, (c, n, lost) in sorted(rep["by_mech"].items())))
    out.append("By band (correct/seen, marks lost): " +
               "  ".join(f"{b} {c}/{n}(-{lost})" for b, (c, n, lost) in sorted(rep["by_band"].items())))
    out.append("Weakest mechanisms (most marks lost first): " + (", ".join(rep["weak_mech"]) or "none"))
    return "\n".join(out)


# Frank's real 2018 Upper Primary answers (as marked on his paper)
FRANK_2018 = {
    1: "D", 2: "E", 3: "D", 4: "A", 5: "E", 6: "D", 7: "D", 8: "C", 9: "B", 10: "B",
    11: "C", 12: "A", 13: "A", 14: "C", 15: "E", 16: "B", 17: "C", 18: "B", 19: "B", 20: "A",
    21: "A", 22: "E", 23: "E", 24: "A", 25: "D", 26: "918", 27: "322", 28: "509", 29: "252", 30: "6",
}


if __name__ == "__main__":
    print(render(mark_paper(2018, FRANK_2018)))
