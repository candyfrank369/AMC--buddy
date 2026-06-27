"""Combined M8 drill: route inspection (Q24 gap) + cube opposite-faces (Q27 gap).
All items are verified twins of real anchors (2018 Q24=60, 2018 Q27=321)."""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from tutor import generate


def twins(anchor, n, key):
    out, seen, s = [], set(), 0
    while len(out) < n and s < 300:
        it = generate.make_item(anchor, seed=s); s += 1
        if it and it["answer"] not in seen:
            seen.add(it["answer"]); out.append(it)
    return out


items = twins((2018, 24), 3, "route") + twins((2018, 27), 3, "cube")
for it in items:
    if it["type"] == "route_inspection":
        it["fence"] = sum(w for _, _, w in it["params"]["edges"]); it["extra"] = it["answer"] - it["fence"]
    else:
        it["opp"] = [it["answer"] - v for v in it["params"]["visible"]]
os.makedirs("practice", exist_ok=True)

st = getSampleStyleSheet()
NAVY = colors.HexColor('#1a3c6e'); GREY = colors.HexColor('#666666')
H1 = ParagraphStyle('H1', parent=st['Heading1'], fontSize=16, textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle('SUB', parent=st['Normal'], fontSize=9, textColor=GREY, spaceAfter=10)
QN = ParagraphStyle('QN', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=10, spaceAfter=4)
ANS = ParagraphStyle('ANS', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=9)
SM = ParagraphStyle('SM', parent=st['Normal'], fontSize=9, leading=12.5, leftIndent=6, spaceAfter=2,
                    textColor=colors.HexColor('#333333'))
FOOT = ParagraphStyle('FOOT', parent=st['Normal'], fontSize=8.5, textColor=GREY)


def head(story, sub):
    story.append(Paragraph("Frank &mdash; AMC Drill &nbsp;<font size=11 color='#5b2a86'>M8 &middot; logic / invariant</font>", H1))
    story.append(Paragraph(sub, SUB)); story.append(HRFlowable(width="100%", thickness=1, color=NAVY)); story.append(Spacer(1, 4))


q = []
head(q, "25 Jun 2026 &nbsp;|&nbsp; Your real weak spot (M8). Q1&ndash;3 = route inspection (twins of 2018 Q24); "
        "Q4&ndash;6 = cube opposite faces (twins of 2018 Q27). Whole-number answers; show working.")
for i, it in enumerate(items, 1):
    q.append(Paragraph(f"<b>{i}.</b> &nbsp;[{it['marks']} marks] &nbsp; {it['stem']}", QN))
    q.append(Table([[""]], colWidths=[170*mm], rowHeights=[26*mm],
                   style=TableStyle([('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
                                     ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fcfcfc'))])))
q.append(Spacer(1, 6)); q.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
q.append(Paragraph("Every item is a code-verified twin of a real 2018 question. Route: count odd junctions first. "
                   "Cube: the three shown faces are adjacent (meet at a corner), not opposite.", FOOT))
SimpleDocTemplate("practice/Frank_M8_QUESTIONS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank M8 - Questions").build(q)

a = []
head(a, "25 Jun 2026 &nbsp;|&nbsp; ANSWER KEY &amp; method &mdash; for the parent")
for i, it in enumerate(items, 1):
    a.append(Paragraph(f"<b>{i}.</b> &nbsp; Answer: <b>{it['answer']}</b> "
                       f"<font size=8 color='#666666'>[M8 &middot; twin of real {it['anchor']} &middot; {it['marks']} marks]</font>", ANS))
    if it["type"] == "route_inspection":
        aa, bb, hyp = it["params"]["_dims"]
        a.append(Paragraph(f"Working: 4 odd corners &rarr; fence total 2&times;{aa}+2&times;{bb}+2&times;{hyp} = "
                           f"<b>{it['fence']}</b>; re-walk the two shortest sides = 2&times;{min(aa,bb)} = "
                           f"<b>{it['extra']}</b>; route = {it['fence']}+{it['extra']} = <b>{it['answer']} km</b>.", SM))
    else:
        v = it["params"]["visible"]; o = it["opp"]
        a.append(Paragraph(f"Working: the hidden (opposite) faces are {it['answer']}&minus;{v[0]}={o[0]}, "
                           f"{it['answer']}&minus;{v[1]}={o[1]}, {it['answer']}&minus;{v[2]}={o[2]} &mdash; all use only "
                           f"the allowed digits and are different, so the largest total is <b>{it['answer']}</b>.", SM))
    a.append(Paragraph(f"&#9733; {it['method_star']}", SM))
    a.append(Paragraph(f"<font color='#b3261e'>Trap:</font> {it['trap']}", SM))
SimpleDocTemplate("practice/Frank_M8_ANSWERS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank M8 - Answers").build(a)

print("WROTE practice/Frank_M8_QUESTIONS.pdf + _ANSWERS.pdf  (%d items)" % len(items))
for it in items:
    print(f"  {it['type']:18} {it['anchor']}  -> {it['answer']}")
