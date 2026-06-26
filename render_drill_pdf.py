"""Render a generated drill JSON into two print-ready PDFs: student paper + answer key.
Engine = content authority (verified twins); this layer = presentation only.
"""
import json, sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)

SRC = sys.argv[1] if len(sys.argv) > 1 else "practice/Frank_drill_2026-06-25.json"
DATE = "25 Jun 2026"
items = json.load(open(SRC))

st = getSampleStyleSheet()
NAVY = colors.HexColor('#1a3c6e'); RED = colors.HexColor('#b3261e'); GREY = colors.HexColor('#666666')
H1 = ParagraphStyle('H1', parent=st['Heading1'], fontSize=16, textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle('SUB', parent=st['Normal'], fontSize=9, textColor=GREY, spaceAfter=10)
QN = ParagraphStyle('QN', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=10, spaceAfter=4)
ANS = ParagraphStyle('ANS', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=9)
SM = ParagraphStyle('SM', parent=st['Normal'], fontSize=9, leading=12.5, textColor=colors.HexColor('#333333'), leftIndent=6, spaceAfter=2)
FOOT = ParagraphStyle('FOOT', parent=st['Normal'], fontSize=8.5, textColor=GREY)


def header(story, subtitle):
    story.append(Paragraph("Frank &mdash; AMC Medal Drill", H1))
    story.append(Paragraph(subtitle, SUB))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY))
    story.append(Spacer(1, 4))


# ---------- STUDENT PAPER ----------
s = []
header(s, f"{DATE} &nbsp;|&nbsp; Targeted on your 2018 gaps: cross-number / digit-property &amp; organised counting "
          f"&nbsp;|&nbsp; All answers are whole numbers. Show your working.")
for i, it in enumerate(items, 1):
    s.append(Paragraph(f"<b>{i}.</b> &nbsp;[{it['marks']} marks] &nbsp; {it['stem']}", QN))
    s.append(Table([[""]], colWidths=[170*mm], rowHeights=[26*mm],
                   style=TableStyle([('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#cccccc')),
                                     ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fcfcfc'))])))
s.append(Spacer(1, 8))
s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
s.append(Paragraph("Every question is a fresh, code-verified twin of a real AMC Upper Primary question (no past question is reproduced). "
                   "Tip: for &ldquo;multiple of 9&rdquo; add the digits; apply the strongest constraint first.", FOOT))
SimpleDocTemplate("practice/Frank_drill_2026-06-25_QUESTIONS.pdf", pagesize=A4,
                  leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=15*mm,
                  title="Frank AMC Medal Drill - Questions").build(s)

# ---------- ANSWER KEY ----------
a = []
header(a, f"{DATE} &nbsp;|&nbsp; ANSWER KEY &amp; method &mdash; for the parent")
for i, it in enumerate(items, 1):
    a.append(Paragraph(f"<b>{i}.</b> &nbsp; Answer: <b>{it['answer']}</b> &nbsp;&nbsp;"
                       f"<font size=8 color='#666666'>[{it['mechanism']} &middot; twin of real {it['anchor']} &middot; {it['marks']} marks]</font>", ANS))
    a.append(Paragraph(f"<i>{it['stem']}</i>", SM))
    a.append(Paragraph(f"&#9733; Fastest method: {it['method_star']}", SM))
    a.append(Paragraph(f"<font color='#b3261e'>Trap to avoid:</font> {it['trap']}", SM))
a.append(Spacer(1, 8))
a.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
a.append(Paragraph("Source-grounded: each item passed verify.py (unique answer + difficulty inside the real-paper band) and twins a specific real anchor. "
                   "Focus areas chosen from Frank's 2018 misses (Q27 enumeration, Q30 cross-number).", FOOT))
SimpleDocTemplate("practice/Frank_drill_2026-06-25_ANSWERS.pdf", pagesize=A4,
                  leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=15*mm,
                  title="Frank AMC Medal Drill - Answers").build(a)

print("WROTE practice/Frank_drill_2026-06-25_QUESTIONS.pdf")
print("WROTE practice/Frank_drill_2026-06-25_ANSWERS.pdf")
