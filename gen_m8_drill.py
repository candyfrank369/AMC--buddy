"""Generate + render an M8 route-inspection drill (Frank's real Q24 gap)."""
import json, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from tutor import generate

# --- generate 5 distinct verified twins of 2018 Q24 (M8 route inspection) ---
items, seen, s = [], set(), 0
while len(items) < 5 and s < 200:
    it = generate.make_item((2018, 24), seed=s); s += 1
    if not it or it["answer"] in seen:
        continue
    seen.add(it["answer"])
    fence = sum(w for _, _, w in it["params"]["edges"])
    it["fence"] = fence; it["extra"] = it["answer"] - fence
    items.append(it)
items.sort(key=lambda x: x["answer"])
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
    story.append(Paragraph("Frank &mdash; AMC Drill &nbsp;<font size=11 color='#5b2a86'>M8 &middot; route inspection</font>", H1))
    story.append(Paragraph(sub, SUB)); story.append(HRFlowable(width="100%", thickness=1, color=NAVY)); story.append(Spacer(1, 4))


q = []
head(q, "25 Jun 2026 &nbsp;|&nbsp; Targets your real gap (2018 Q24, M8). Walk every fence, return to start. "
        "Whole-number answers in km &mdash; show your working.")
for i, it in enumerate(items, 1):
    q.append(Paragraph(f"<b>{i}.</b> &nbsp;[{it['marks']} marks] &nbsp; {it['stem']}", QN))
    q.append(Table([[""]], colWidths=[170*mm], rowHeights=[28*mm],
                   style=TableStyle([('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
                                     ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fcfcfc'))])))
q.append(Spacer(1, 6)); q.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
q.append(Paragraph("Each is a code-verified twin of the real 2018 Q24. First step every time: count the fences at each "
                   "corner &mdash; are any odd?", FOOT))
SimpleDocTemplate("practice/Frank_M8_route_QUESTIONS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank M8 route - Questions").build(q)

a = []
head(a, "25 Jun 2026 &nbsp;|&nbsp; ANSWER KEY &amp; method &mdash; for the parent")
for i, it in enumerate(items, 1):
    aa, bb, hyp = it["params"]["_dims"]
    a.append(Paragraph(f"<b>{i}.</b> &nbsp; Answer: <b>{it['answer']} km</b> "
                       f"<font size=8 color='#666666'>[M8 &middot; twin of real 2018 Q24 &middot; {it['marks']} marks]</font>", ANS))
    a.append(Paragraph(f"Working: all 4 corners have 3 fences (odd) &rarr; re-walk the two shortest sides. "
                       f"Fence total = 2&times;{aa} + 2&times;{bb} + 2&times;{hyp} = <b>{it['fence']} km</b>; "
                       f"minimum extra = 2&times;{min(aa, bb)} = <b>{it['extra']} km</b>; "
                       f"shortest route = {it['fence']} + {it['extra']} = <b>{it['answer']} km</b>.", SM))
    a.append(Paragraph(f"&#9733; {it['method_star']}", SM))
    a.append(Paragraph(f"<font color='#b3261e'>Trap:</font> {it['trap']}", SM))
SimpleDocTemplate("practice/Frank_M8_route_ANSWERS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank M8 route - Answers").build(a)

json.dump([{k: v for k, v in it.items() if k != "params"} for it in items],
          open("practice/Frank_M8_route.json", "w"), indent=2)
print("WROTE practice/Frank_M8_route_QUESTIONS.pdf + _ANSWERS.pdf")
for it in items:
    print(f"  {it['params']['_dims'][0]}x{it['params']['_dims'][1]} -> {it['answer']} km (fence {it['fence']} + extra {it['extra']})")
