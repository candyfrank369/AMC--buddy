"""Render the L2/L3 drill JSON -> two print-ready PDFs (questions + answer key)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)

items = json.load(open("practice/Frank_drill_L2L3.json"))
DATE = "25 Jun 2026"
st = getSampleStyleSheet()
NAVY = colors.HexColor('#1a3c6e'); RED = colors.HexColor('#b3261e'); GREY = colors.HexColor('#666666')
PUR = colors.HexColor('#5b2a86')
H1 = ParagraphStyle('H1', parent=st['Heading1'], fontSize=16, textColor=NAVY, spaceAfter=2)
SUB = ParagraphStyle('SUB', parent=st['Normal'], fontSize=9, textColor=GREY, spaceAfter=10)
QN = ParagraphStyle('QN', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=10, spaceAfter=4)
ANS = ParagraphStyle('ANS', parent=st['Normal'], fontSize=11, leading=15, spaceBefore=9)
SM = ParagraphStyle('SM', parent=st['Normal'], fontSize=9, leading=12.5, textColor=colors.HexColor('#333333'), leftIndent=6, spaceAfter=2)
FOOT = ParagraphStyle('FOOT', parent=st['Normal'], fontSize=8.5, textColor=GREY)


def badge(lv):
    c = '#5b2a86' if lv == 'L3' else '#b3261e'
    return f"<font color='{c}'><b>[{lv}]</b></font>"


def header(story, sub):
    story.append(Paragraph("Frank &mdash; AMC Medal Drill &nbsp;<font size=11 color='#5b2a86'>L2 / L3 stretch</font>", H1))
    story.append(Paragraph(sub, SUB))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY)); story.append(Spacer(1, 4))


# -------- STUDENT PAPER --------
s = []
header(s, f"{DATE} &nbsp;|&nbsp; Same two topics, Medal intensity. These are <b>harder than the real-paper ceiling</b>: "
          f"trial-and-error will not finish them &mdash; you must reason structurally. Whole-number answers; show working.")
for i, it in enumerate(items, 1):
    s.append(Paragraph(f"<b>{i}.</b> &nbsp;{badge(it['level'])} &nbsp;[{it['marks']} marks] &nbsp; {it['stem']}", QN))
    s.append(Table([[""]], colWidths=[170*mm], rowHeights=[30*mm],
                   style=TableStyle([('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#cccccc')),
                                     ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fcfcfc'))])))
s.append(Spacer(1, 6)); s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
s.append(Paragraph("L2 = an in-range question with a hidden condition (don't stop early). "
                   "L3 = above the real-paper ceiling: the search space is too big to list, so count by structure. "
                   "Every item is a code-verified twin of a real AMC anchor family.", FOOT))
SimpleDocTemplate("practice/Frank_drill_L2L3_QUESTIONS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank AMC Medal Drill L2L3 - Questions").build(s)

# -------- ANSWER KEY --------
a = []
header(a, f"{DATE} &nbsp;|&nbsp; ANSWER KEY, method &amp; the trap &mdash; for the parent")
for i, it in enumerate(items, 1):
    a.append(Paragraph(f"<b>{i}.</b> &nbsp;{badge(it['level'])} &nbsp; Answer: <b>{it['answer']}</b> "
                       f"&nbsp;<font size=8 color='#666666'>[{it['topic']} &middot; {it['lineage']} &middot; "
                       f"difficulty {it['difficulty']} vs real ceiling {it['ceiling']} &middot; {it['marks']} marks]</font>", ANS))
    a.append(Paragraph(f"<i>{it['stem']}</i>", SM))
    a.append(Paragraph(f"&#9733; Method: {it['method']}", SM))
    if it.get('trap'):
        a.append(Paragraph(f"<font color='#b3261e'>The trap:</font> {it['trap']}", SM))
    if it.get('why'):
        a.append(Paragraph(f"<font color='#5b2a86'>Why it's L3:</font> {it['why']}", SM))
a.append(Spacer(1, 6)); a.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
a.append(Paragraph("Every answer is solver-verified (unique). L2 keeps real-paper difficulty but plants a decoy equal to the common slip; "
                   "L3 is deliberately pushed ABOVE the real-paper ceiling and out of hand-enumeration range. Topics: Frank's 2018 gaps (Q27 enumeration, Q30 cross-number).", FOOT))
SimpleDocTemplate("practice/Frank_drill_L2L3_ANSWERS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank AMC Medal Drill L2L3 - Answers").build(a)

print("WROTE practice/Frank_drill_L2L3_QUESTIONS.pdf")
print("WROTE practice/Frank_drill_L2L3_ANSWERS.pdf")
