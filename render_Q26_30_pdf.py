"""Render the Q26-30 stretch tail JSON -> two print-ready PDFs (questions + answer key)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)

items = json.load(open("practice/Frank_Q26_30.json"))
DATE = "30 Jun 2026"
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
    story.append(Paragraph("Frank &mdash; AMC Upper Primary &nbsp;<font size=11 color='#5b2a86'>STRETCH TAIL Q26&ndash;Q30</font>", H1))
    story.append(Paragraph(sub, SUB))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY)); story.append(Spacer(1, 4))


# -------- STUDENT PAPER --------
s = []
header(s, f"{DATE} &nbsp;|&nbsp; The 5 integer-answer tail questions that decide a Prize. These are pitched at "
          f"(or <b>above</b>) the real-paper ceiling &mdash; trial-and-error will not finish them in time. "
          f"Whole-number answers; show your working.")
for it in items:
    s.append(Paragraph(f"<b>Q{it['qno']}.</b> &nbsp;{badge(it['level'])} &nbsp;[{it['marks']} marks] &nbsp; {it['stem']}", QN))
    s.append(Table([[""]], colWidths=[170*mm], rowHeights=[34*mm],
                   style=TableStyle([('BOX',(0,0),(-1,-1),0.4,colors.HexColor('#cccccc')),
                                     ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#fcfcfc'))])))
s.append(Spacer(1, 6)); s.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
s.append(Paragraph("L2 = real-paper difficulty with a hidden condition (don't stop early). "
                   "L3 = above the real-paper ceiling: the search space is too big to list, so count by structure. "
                   "Every item is a code-verified twin of a real AMC anchor family (unique answer, difficulty checked in band).", FOOT))
SimpleDocTemplate("practice/Frank_Q26_30_QUESTIONS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank AMC Stretch Tail Q26-30 - Questions").build(s)

# -------- ANSWER KEY --------
a = []
header(a, f"{DATE} &nbsp;|&nbsp; ANSWER KEY, method &amp; the trap &mdash; for the parent")
for it in items:
    a.append(Paragraph(f"<b>Q{it['qno']}.</b> &nbsp;{badge(it['level'])} &nbsp; Answer: <b>{it['answer']}</b> "
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
                   "L3 is deliberately pushed ABOVE the real-paper ceiling and out of hand-enumeration range. "
                   "Topics target Frank's tail gaps: organised enumeration (M5) and stacked-constraint cross-number (M2).", FOOT))
SimpleDocTemplate("practice/Frank_Q26_30_ANSWERS.pdf", pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                  topMargin=15*mm, bottomMargin=15*mm, title="Frank AMC Stretch Tail Q26-30 - Answers").build(a)

print("WROTE practice/Frank_Q26_30_QUESTIONS.pdf")
print("WROTE practice/Frank_Q26_30_ANSWERS.pdf")
