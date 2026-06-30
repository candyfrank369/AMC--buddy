"""Frank PRIZE TAIL Q26-30 -- a BALANCED hard tail, one distinct skill per slot (no two
questions share a method), built on the engine's verified solvers (code is the sole judge).

   Q26  M2  stacked-constraint digit number   (generated twin + hidden-condition trap)
   Q27  M5  organised counting / residue mod   (generated twin, search space too big to list)
   Q28  M6  iterate-a-map -> find the CYCLE     (generated twin; invariant/recurrence, not counting)
   Q29  M7  area dissection from EXACT coords   (figure drawn from the same coords as the answer)
   Q30  M8  cube opposite-faces invariant       (generated twin; logic, no formula)

Marks follow the real AMC Upper Primary tail ramp (6,7,8,9,10). Every answer is solver-verified
(unique + difficulty in band); the M7 figure is shoelace-checked against its own coordinates.
No API, no hand-written maths, no spend. Fresh seed -> different from prior drills.
"""
import json, os, random
from math import comb
from fractions import Fraction as F

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, Polygon, Line, Circle, String

from tutor import verify, generate, figures

m2 = verify.MODULES["M2"]; m5 = verify.MODULES["M5"]
SEED = 20260630


# ---------------- M2 / M5 builders (proven, with computed decoy/why) ----------------
def prop(pr):
    k, a = (pr[0], pr[1]) if isinstance(pr, (list, tuple)) else (pr, None)
    return {"multiple_of": f"divisible by {a}", "contains_digit": f"contains the digit {a}",
            "no_digit": f"has no digit {a}", "all_distinct": "has all different digits",
            "num_odd_digits": f"has exactly {a} odd digit" + ("s" if a != 1 else ""),
            "digit_sum_multiple": f"has a digit sum divisible by {a}",
            "divisible_by_unit_digit": "is divisible by its own units digit"}[k]


def stem_constrained(p):
    nd = {(100, 999): "three-digit", (1000, 9999): "four-digit"}[tuple(p["range"])]
    props = "; ".join(prop(x) for x in p["predicates"])
    head = "What is the smallest" if p["want"] == "smallest" else "How many"
    tail = f" {nd} number with all of these properties: {props}?" if p["want"] == "smallest" \
        else f" {nd} numbers have all of these properties: {props}?"
    return head + tail


def build_m2(rng):
    mult = rng.choice([3, 6, 9]); contain = rng.choice([2, 3, 4, 5, 6, 7])
    trap = rng.choice([["num_odd_digits", rng.choice([1, 2])], "divisible_by_unit_digit",
                       ["digit_sum_multiple", rng.choice([4, 5, 7])]])
    base = [["multiple_of", mult], ["contains_digit", contain], ["no_digit", 0], "all_distinct"]
    full = base + [trap]
    pf = {"type": "constrained_number", "range": [100, 999], "want": "smallest", "predicates": full}
    pb = {"type": "constrained_number", "range": [100, 999], "want": "smallest", "predicates": base}
    try:
        true = m2.solve(pf); decoy = m2.solve(pb)
    except StopIteration:
        return None
    if not (decoy < true):
        return None
    return dict(mech="M2 · stacked-constraint number", stem=stem_constrained(pf), answer=true,
                lineage="generated twin of 2025 Q26", source="generated",
                method="Apply the strong filters first (divisibility, no-zero, all-different), THEN check the subtle last condition before you commit — don't stop at the first multiple you find.",
                trap=f"a solver who skips “{prop(trap)}” stops at {decoy} — the planted decoy (a real answer to a weaker question).")


def build_m5(rng):
    n = rng.choice([20, 21, 24]); start = rng.choice([1, 2, 3]); d = rng.choice([3, 4])
    p = {"type": "choose_sum_divisible", "set": list(range(start, start + n)), "choose": 3, "divisor": d}
    cnt = m5.solve(p)
    if not (1 <= cnt <= 999):
        return None
    return dict(mech="M5 · organised counting (residue mod)", stem=generate.STEMS["choose_sum_divisible"](p),
                answer=cnt, lineage="generated twin of 2013 Q27", source="generated",
                method=f"Bucket every number by remainder mod {d}; valid triples are 'all three from one bucket' PLUS the matching one-from-each cross-bucket combinations — add the C(·,3) and product counts.",
                trap=f"C({n},3) = {comb(n, 3)} triples — listing them is impossible in time, and 'choose' is unordered so (a,b,c) must not be recounted as (b,a,c).")


# ---------------- assemble the 5 slots (one distinct mechanism each) ----------------
rng = random.Random(SEED)


def first(builder):
    for _ in range(800):
        it = builder(rng)
        if it:
            return it
    raise RuntimeError("builder failed")


q26 = first(build_m2)
q27 = first(build_m5)

m6 = generate.make_item((2024, 29), seed=11)          # iterate digit-square-sum -> find the cycle
q28 = dict(mech="M6 · iterate a map → find the cycle", stem=m6["stem"], answer=m6["answer"],
           lineage="generated twin of 2024 Q29", source="generated",
           method="Iterate until the numbers REPEAT, then you have a cycle. Find the cycle length L and where it starts; the 3996th term = step into the cycle by (3996 - start) mod L. Never iterate 3996 times.",
           trap=m6["trap"])

m7 = figures.generate_m7(seed=4)                       # area dissection, exact coordinates
v7 = figures.verify_figure(m7)
assert v7["consistent"], "M7 figure/answer mismatch"
q29 = dict(mech="M7 · area dissection (exact figure)", stem=m7["stem"], answer=m7["answer"],
           lineage="generated twin of 2024 Q23", source="figure (coordinate-exact)", figure=m7,
           method="Don't trust the not-to-scale picture. Put the rectangle on a grid and subtract the THREE corner right-triangles from the whole rectangle — no area formula needed. (Closed form here is 3×W×H/8.)",
           trap="Reading lengths off the drawing instead of the stated dimensions; the figure is deliberately not to scale.")

m8 = generate.make_item((2018, 27), seed=9)            # cube opposite faces equal-sum invariant
q30 = dict(mech="M8 · cube opposite-faces invariant", stem=m8["stem"], answer=m8["answer"],
           lineage="generated twin of 2018 Q27", source="generated",
           method="The invariant: all three opposite-face pairs share ONE common sum S. The three shown faces meet at a corner so they are mutually NON-opposite — their three partners are the remaining numbers. Pick the pairing that maximises S, then verify all three pairs really hit the same S.",
           trap=m8["trap"])

MARKS = [6, 7, 8, 9, 10]
items = [q26, q27, q28, q29, q30]
for i, (it, mk) in enumerate(zip(items, MARKS), 26):
    it["qno"] = i; it["marks"] = mk

# persist (drop the live figure spec; keep a flag)
os.makedirs("practice", exist_ok=True)
dump = []
for it in items:
    d = {k: v for k, v in it.items() if k != "figure"}
    d["has_figure"] = "figure" in it
    dump.append(d)
json.dump(dump, open("practice/Frank_prize_tail.json", "w"), indent=2, ensure_ascii=False)


# ---------------- M7 figure as a reportlab Drawing (same exact coords) ----------------
def m7_drawing(spec, scale=10, pad=20):
    W, H = spec["W"], spec["H"]
    w_px, h_px = W * scale + 2 * pad, H * scale + 2 * pad
    d = Drawing(w_px, h_px)

    def X(p): return pad + float(p[0]) * scale
    def Y(p): return pad + float(p[1]) * scale          # reportlab y-up: no flip
    # faint grid
    for gx in range(W + 1):
        d.add(Line(pad + gx * scale, pad, pad + gx * scale, pad + H * scale, strokeColor=colors.HexColor('#eeeeee')))
    for gy in range(H + 1):
        d.add(Line(pad, pad + gy * scale, pad + W * scale, pad + gy * scale, strokeColor=colors.HexColor('#eeeeee')))
    # shaded triangle
    pts = []
    for p in spec["shaded"]:
        pts += [X(p), Y(p)]
    d.add(Polygon(pts, fillColor=colors.HexColor('#9ec9e0'), strokeColor=None))
    # rectangle outline
    rpts = []
    for p in spec["rect"]:
        rpts += [X(p), Y(p)]
    d.add(Polygon(rpts, fillColor=None, strokeColor=colors.HexColor('#222222'), strokeWidth=1.5))
    # construction lines
    for seg in spec["construction"]:
        d.add(Line(X(seg[0]), Y(seg[0]), X(seg[1]), Y(seg[1]), strokeColor=colors.HexColor('#1763a6'), strokeWidth=1))
    # labelled vertices
    for name, p in spec["points"].items():
        x, y = X(p), Y(p)
        d.add(Circle(x, y, 1.8, fillColor=colors.HexColor('#222222'), strokeColor=None))
        dx, dy = (-9, 1) if name in "AD" else (4, 1)
        d.add(String(x + dx, y + dy, name, fontSize=9, fillColor=colors.HexColor('#222222')))
    # dimension labels
    d.add(String(pad + W * scale / 2 - 8, pad - 13, f"W={W}", fontSize=8, fillColor=colors.HexColor('#555555')))
    d.add(String(pad - 16, pad + H * scale / 2, f"H={H}", fontSize=8, fillColor=colors.HexColor('#555555')))
    return d


# ---------------- render the two PDFs ----------------
DATE = "30 Jun 2026"
st = getSampleStyleSheet()
NAVY = colors.HexColor('#1a3c6e'); GREY = colors.HexColor('#666666')
H1 = ParagraphStyle('H1', parent=st['Heading1'], fontSize=16, textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle('SUB', parent=st['Normal'], fontSize=9, textColor=GREY, spaceAfter=10)
QN = ParagraphStyle('QN', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=10, spaceAfter=4)
ANS = ParagraphStyle('ANS', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=9)
SM = ParagraphStyle('SM', parent=st['Normal'], fontSize=9, leading=12.5, leftIndent=6, spaceAfter=2,
                    textColor=colors.HexColor('#333333'))
FOOT = ParagraphStyle('FOOT', parent=st['Normal'], fontSize=8.5, textColor=GREY)


def header(story, sub):
    story.append(Paragraph("Frank &mdash; AMC Upper Primary &nbsp;<font size=11 color='#5b2a86'>BALANCED PRIZE TAIL Q26&ndash;Q30</font>", H1))
    story.append(Paragraph(sub, SUB))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY)); story.append(Spacer(1, 4))


def mech_tag(it):
    return f"<font color='#5b2a86'><b>[{it['mech'].split(' ')[0]}]</b></font>"


# ---- STUDENT PAPER ----
s = []
header(s, f"{DATE} &nbsp;|&nbsp; Five tail questions, <b>five different skills</b> &mdash; counting, residue, "
          f"a repeating-map cycle, an area dissection, and a cube invariant. No two are solved the same way. "
          f"Whole-number answers; show your working.")
for it in items:
    blk = [Paragraph(f"<b>Q{it['qno']}.</b> &nbsp;{mech_tag(it)} &nbsp;[{it['marks']} marks] &nbsp; {it['stem']}", QN)]
    if "figure" in it:
        blk.append(Spacer(1, 2)); blk.append(m7_drawing(it["figure"]))
    blk.append(Table([[""]], colWidths=[170*mm], rowHeights=[30*mm],
                     style=TableStyle([('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
                                       ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fcfcfc'))])))
    s.append(KeepTogether(blk))
s.append(Spacer(1, 6)); s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
s.append(Paragraph("Each item is a code-verified twin of a real AMC anchor (unique answer, difficulty in band). "
                   "The geometry figure is drawn from the SAME exact coordinates used to compute its area, so the "
                   "picture and the answer cannot disagree.", FOOT))
SimpleDocTemplate("practice/Frank_prize_tail_QUESTIONS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank AMC Balanced Prize Tail - Questions").build(s)

# ---- ANSWER KEY ----
a = []
header(a, f"{DATE} &nbsp;|&nbsp; ANSWER KEY, &#9733; method &amp; the trap &mdash; for the parent")
for it in items:
    a.append(Paragraph(f"<b>Q{it['qno']}.</b> &nbsp;{mech_tag(it)} &nbsp; Answer: <b>{it['answer']}</b> "
                       f"&nbsp;<font size=8 color='#666666'>[{it['mech']} &middot; {it['lineage']} &middot; "
                       f"{it['source']} &middot; {it['marks']} marks]</font>", ANS))
    a.append(Paragraph(f"<i>{it['stem']}</i>", SM))
    a.append(Paragraph(f"&#9733; Method: {it['method']}", SM))
    a.append(Paragraph(f"<font color='#b3261e'>The trap:</font> {it['trap']}", SM))
a.append(Spacer(1, 6)); a.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
a.append(Paragraph("Coverage: M2 stacked-constraint number &middot; M5 organised counting &middot; M6 repeating-map cycle "
                   "(invariant, not counting) &middot; M7 area dissection (coordinate-exact figure) &middot; M8 cube "
                   "opposite-faces invariant. Five mechanisms, five methods &mdash; the balanced prize tail.", FOOT))
SimpleDocTemplate("practice/Frank_prize_tail_ANSWERS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank AMC Balanced Prize Tail - Answers").build(a)

print(f"built balanced prize tail, {len(items)} items\n")
for it in items:
    print(f"[Q{it['qno']}] {it['mech']}  [{it['marks']} marks]")
    print(f"    {it['stem']}")
    print(f"    ANSWER = {it['answer']}\n")
print("WROTE practice/Frank_prize_tail_QUESTIONS.pdf")
print("WROTE practice/Frank_prize_tail_ANSWERS.pdf")
