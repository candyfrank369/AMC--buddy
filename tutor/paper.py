"""paper.py — ONE command turns a mock into two printable PDFs:
a STUDENT PAPER and a PARENT ANSWER MANUAL.

Every item is produced by generate.make_item (proposer -> verify.py gate), so
nothing is printed unless it has a UNIQUE answer inside the real-paper difficulty
band. Pure standard library: no external packages, no network, $0 to run.

CLI:  python -m tutor.paper              # the canonical paper
      python -m tutor.paper --seed 1     # a different draw of verified twins
"""
import argparse
import datetime
import os
import textwrap

from tutor import generate
from tutor.mock import MOCK_PLAN

# ---------------------------------------------------------------------------
# tiny dependency-free PDF writer  (Letter page, base-14 Helvetica, text only)
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = 612, 792
ML, MR, MT, MB = 60, 60, 64, 60          # left / right / top / bottom margins
USABLE = PAGE_W - ML - MR


def _esc(s):
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _wrap(text, size, indent):
    max_chars = max(8, int((USABLE - indent) / (size * 0.50)))
    return textwrap.wrap(text, width=max_chars) or [""]


def _flow(lines):
    """lines: (text, font_key, size, indent, space_before).
    Returns a list of pages; each page is a list of (x, y, text, font_key, size)."""
    pages, cur = [], []
    y = PAGE_H - MT
    for text, fk, size, indent, space_before in lines:
        y -= space_before
        leading = size * 1.4
        if text == "":
            y -= leading
            continue
        for piece in _wrap(text, size, indent):
            if y - leading < MB:
                pages.append(cur)
                cur = []
                y = PAGE_H - MT
            cur.append((ML + indent, y, piece, fk, size))
            y -= leading
    pages.append(cur)
    return pages


def _serialize(pages, title):
    # object plan: 1 Catalog, 2 Pages, 3 Helvetica, 4 Helvetica-Bold,
    # then per page a Contents object and a Page object.
    content_nums, page_nums = [], []
    num = 5
    for _ in pages:
        content_nums.append(num); num += 1
        page_nums.append(num); num += 1
    total = num - 1

    objs = {}
    objs[1] = "<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{p} 0 R" for p in page_nums)
    objs[2] = f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>"
    objs[3] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    objs[4] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
    for i, page in enumerate(pages):
        runs = [f"BT /{fk} {size:.1f} Tf 1 0 0 1 {x:.1f} {y:.1f} Tm ({_esc(t)}) Tj ET"
                for (x, y, t, fk, size) in page]
        objs[content_nums[i]] = ("STREAM", "\n".join(runs))
        objs[page_nums[i]] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            f"/Contents {content_nums[i]} 0 R >>")

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = {}
    for n in range(1, total + 1):
        offsets[n] = len(out)
        body = objs[n]
        if isinstance(body, tuple):                      # content stream
            data = body[1].encode("latin-1", "replace")
            out += f"{n} 0 obj\n<< /Length {len(data)} >>\nstream\n".encode("latin-1")
            out += data + b"\nendstream\nendobj\n"
        else:
            out += f"{n} 0 obj\n{body}\nendobj\n".encode("latin-1")
    xref_pos = len(out)
    out += f"xref\n0 {total + 1}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for n in range(1, total + 1):
        out += f"{offsets[n]:010d} 00000 n \n".encode("latin-1")
    out += (f"trailer\n<< /Size {total + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n").encode("latin-1")
    return bytes(out)


def write_pdf(lines, path, title):
    with open(path, "wb") as f:
        f.write(_serialize(_flow(lines), title))


# ---------------------------------------------------------------------------
# build the verified item set, then the two page layouts (ASCII-only text)
# ---------------------------------------------------------------------------
def build_items(seed_base=0):
    items = []
    for anchor in MOCK_PLAN:
        for seed in range(seed_base, seed_base + 80):
            it = generate.make_item(anchor, seed=seed)
            if it is not None:
                items.append(it)
                break
        else:
            raise RuntimeError(f"no verified twin for {anchor} at seed_base {seed_base}")
    return items


def _student_lines(items):
    L = [("AMC-buddy Mock  -  Upper Primary Tail", "F2", 16, 0, 0),
         ("Student Paper", "F2", 12, 0, 8),
         ("60 minutes   -   9 questions   -   whole-number answers   -   diagrams are not drawn to scale",
          "F1", 9.5, 0, 5),
         ("Name: __________________     Date: ____________     Score: ____ / 9", "F1", 10, 0, 12),
         ("", "F1", 10, 0, 4)]
    for i, it in enumerate(items, 1):
        L.append((f"Q{i}.    [{it['marks']} marks]", "F2", 11.5, 0, 12))
        L.append((it["stem"], "F1", 11, 16, 4))
        L.append(("Answer: ____________________", "F1", 10, 16, 8))
    return L


def _answer_lines(items):
    L = [("AMC-buddy Mock  -  Parent Answer Manual", "F2", 16, 0, 0),
         ("Upper Primary Tail   -   every item was checked by verify.py before printing",
          "F1", 9.5, 0, 8),
         ("", "F1", 10, 0, 4)]
    for i, it in enumerate(items, 1):
        L.append((f"Q{i}.   answer = {it['answer']}     "
                  f"[{it['mechanism']}, {it['marks']} marks - twin of {it['anchor']}]",
                  "F2", 11.5, 0, 12))
        L.append((f"* fastest method: {it['method_star']}", "F1", 10.5, 16, 5))
        L.append((f"x the trap: {it['trap']}", "F1", 10.5, 16, 3))
        L.append((f"(verifier: unique={it['unique']}, difficulty {it['difficulty']} "
                  f"in band {it['band']})", "F1", 9, 16, 3))
    return L


def main():
    ap = argparse.ArgumentParser(description="Print a mock as student + answer PDFs.")
    ap.add_argument("--seed", type=int, default=0, help="draw a different set of verified twins")
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "..", "papers"))
    args = ap.parse_args()

    items = build_items(args.seed)
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    tag = datetime.date.today().isoformat() + (f"_v{args.seed}" if args.seed else "")
    student = os.path.join(outdir, f"AMC_mock_{tag}_student.pdf")
    answers = os.path.join(outdir, f"AMC_mock_{tag}_answers.pdf")

    write_pdf(_student_lines(items), student, "AMC-buddy Mock - Student Paper")
    write_pdf(_answer_lines(items), answers, "AMC-buddy Mock - Parent Answer Manual")

    print("STUDENT PAPER : " + student)
    print("ANSWER MANUAL : " + answers)


if __name__ == "__main__":
    main()
