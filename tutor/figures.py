"""figures.py — M7 geometry drawn from EXACT coordinates, plus the curated M7/M8 set.

CLAUDE.md rule #6: a generated M7 figure is DRAWN from exact coordinates and its answer is
computed by shoelace over THOSE SAME coordinates — so the picture and the answer can never
disagree. Output is SVG (pure text, stdlib only) + an ASCII preview for the terminal.

True 3-D / novel-visual spatial items (paper folding, opposite-side views, gears) are NOT
faked: they are CURATED from the real papers (the parent prints the actual question; a copy
would be worthless). `curated_worksheet()` assembles those real M7/M8 items by source + page +
answer, without reproducing any stem.
"""
import json
import os
import random
from fractions import Fraction as F

from tutor import verify   # only for _ROOT / corpus path

FIGDIR = os.path.join(verify._ROOT, "content", "figures")


# ----------------------------------------------------------------- geometry
def shoelace(poly):
    """Exact area of a simple polygon given as [(x, y), ...] (Fractions or ints)."""
    n, s = len(poly), F(0)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += F(x1) * F(y2) - F(x2) * F(y1)
    return abs(s) / 2


def point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = float(poly[i][0]), float(poly[i][1])
        xj, yj = float(poly[j][0]), float(poly[j][1])
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


# ----------------------------------------------------------------- M7 twin (coordinate family)
def m7_shaded_triangle(W, H):
    """Family of anchor 2024 Q23: rectangle ABCD (A top-left), shaded triangle joins the
    top-left corner A, the midpoint of the right side, and the midpoint of the bottom side.
    Exact coordinates -> exact area = shoelace = 3*W*H/8."""
    A = (F(0), F(H)); B = (F(W), F(H)); C = (F(W), F(0)); D = (F(0), F(0))
    M = (F(W), F(H, 2))            # midpoint of right side BC
    N = (F(W, 2), F(0))            # midpoint of bottom side DC
    shaded = [A, M, N]
    spec = {
        "name": f"m7_tri_{W}x{H}",
        "W": W, "H": H,
        "rect": [D, C, B, A],                       # rectangle outline (CCW)
        "construction": [[A, M], [M, N], [N, A]],   # drawn lines
        "shaded": shaded,
        "points": {"A": A, "B": B, "C": C, "D": D, "M": M, "N": N},
        "dims": [("W", D, C), ("H", D, A)],         # dimension labels along edges
        "answer": shoelace(shaded),
        "anchor": "2024 Q23",
        "stem": (f"ABCD is a rectangle measuring {W} by {H} (area {W*H}). M is the midpoint of "
                 f"side BC and N is the midpoint of side DC. M and N are each joined to A and "
                 f"to each other. What is the area of the shaded triangle AMN?"),
    }
    return spec


def generate_m7(seed=0):
    """Propose an M7 twin whose answer is a whole number and is NOT the anchor's 21."""
    rng = random.Random(seed)
    for _ in range(50):
        W = rng.choice([8, 12])        # one side divisible by 4 -> integer area
        H = rng.choice([6, 10, 14])
        spec = m7_shaded_triangle(W, H)
        if spec["answer"].denominator == 1 and spec["answer"] != 21:
            spec["answer"] = int(spec["answer"])
            return spec
    raise RuntimeError("no integer-area M7 twin found")


def verify_figure(spec):
    """The whole point of M7: the area re-read off the DRAWN polygon equals the stated answer
    AND the closed-form. Returns the consistency verdict."""
    drawn = shoelace(spec["shaded"])
    closed_form = F(3 * spec["W"] * spec["H"], 8)
    return {"area_from_drawn_polygon": drawn, "closed_form_3WH_8": closed_form,
            "stated_answer": spec["answer"],
            "consistent": drawn == closed_form == spec["answer"]}


# ----------------------------------------------------------------- rendering
def render_svg(spec, scale=42, pad=34):
    W, H = spec["W"], spec["H"]

    def px(p):                                       # math (y-up) -> svg (y-down)
        return (pad + float(p[0]) * scale, pad + (H - float(p[1])) * scale)

    def poly_pts(poly):
        return " ".join(f"{px(p)[0]:.1f},{px(p)[1]:.1f}" for p in poly)

    w_px, h_px = pad * 2 + W * scale, pad * 2 + H * scale
    L = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_px:.0f}" height="{h_px:.0f}" '
         f'font-family="sans-serif" font-size="13">',
         f'<rect width="{w_px:.0f}" height="{h_px:.0f}" fill="white"/>']
    # faint unit grid
    for gx in range(W + 1):
        x = px((gx, 0))[0]
        L.append(f'<line x1="{x:.1f}" y1="{px((0,0))[1]:.1f}" x2="{x:.1f}" y2="{px((0,H))[1]:.1f}" stroke="#eee"/>')
    for gy in range(H + 1):
        y = px((0, gy))[1]
        L.append(f'<line x1="{px((0,0))[0]:.1f}" y1="{y:.1f}" x2="{px((W,0))[0]:.1f}" y2="{y:.1f}" stroke="#eee"/>')
    # shaded region
    L.append(f'<polygon points="{poly_pts(spec["shaded"])}" fill="#9ec9e0" stroke="none"/>')
    # rectangle outline
    L.append(f'<polygon points="{poly_pts(spec["rect"])}" fill="none" stroke="#222" stroke-width="2"/>')
    # construction lines
    for seg in spec["construction"]:
        (x1, y1), (x2, y2) = px(seg[0]), px(seg[1])
        L.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#1763a6" stroke-width="1.5"/>')
    # labelled points
    for name, p in spec["points"].items():
        x, y = px(p)
        dx, dy = (-12, -6) if name in "AD" else (6, -6)
        L.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="#222"/>')
        L.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}">{name}</text>')
    # dimension labels
    for label, p1, p2 in spec["dims"]:
        mx, my = (px(p1)[0] + px(p2)[0]) / 2, (px(p1)[1] + px(p2)[1]) / 2
        off = (0, 18) if label == "W" else (-20, 0)
        L.append(f'<text x="{mx+off[0]:.1f}" y="{my+off[1]:.1f}" fill="#555">{label}={spec[label]}</text>')
    L.append("</svg>")
    return "\n".join(L)


def save_svg(spec):
    os.makedirs(FIGDIR, exist_ok=True)
    path = os.path.join(FIGDIR, spec["name"] + ".svg")
    with open(path, "w") as fh:
        fh.write(render_svg(spec))
    return path


def ascii_preview(spec, cols=44):
    W, H = spec["W"], spec["H"]
    rows = max(8, round(cols * H / W / 2))
    out = []
    for r in range(rows + 1):
        y = H * (rows - r) / rows
        line = []
        for c in range(cols + 1):
            x = W * c / cols
            if point_in_poly(x, y, spec["shaded"]):
                line.append("#")
            elif -0.06 <= x <= W + 0.06 and -0.06 <= y <= H + 0.06:
                line.append(".")
            else:
                line.append(" ")
        out.append("".join(line))
    return "\n".join(out)


# ----------------------------------------------------------------- curated M7/M8 set
def _load_corpus():
    rows = []
    with open(os.path.join(verify._ROOT, "content", "questions.jsonl")) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def curated_worksheet(drilled=(), max_items=12):
    """Real M7/M8 questions (the mechanisms we don't auto-generate) for Frank to drill ON THE
    REAL PAPER. Returns reference rows (no stem text) — source_file + page + answer + note.
    Prioritises the discriminator tail and the novel-visual / curated-only items. `drilled` is
    a set of (year, q) already practised, which are skipped."""
    drilled = set(drilled)
    rows = [r for r in _load_corpus()
            if r["mechanism"] in ("M7", "M8") and (r["year"], r["q"]) not in drilled]

    def priority(r):
        visual = r["answer"] is None or "CURATE" in r["note"] or "spatial" in r["note"].lower()
        return (0 if r["q"] >= 26 else 1 if r["q"] >= 21 else 2,   # tail first
                0 if visual else 1,                                # novel-visual first
                -r["year"], r["q"])

    picked = sorted(rows, key=priority)[:max_items]
    return [{"year": r["year"], "q": r["q"], "mechanism": r["mechanism"], "marks": r["marks"],
             "source_file": r["source_file"], "page": r["page"],
             "answer": r["answer"] if r["answer"] is not None else "(see real paper / figure)",
             "topic": r["stem_summary"].split("(=")[0].strip()} for r in picked]


def render_worksheet(items):
    out = ["=" * 78,
           "CURATED M7/M8 WORKSHEET  (drill on the REAL papers — do not copy the stems)",
           "the parent prints the listed page; answers/traps below are the key only",
           "=" * 78]
    for i, it in enumerate(items, 1):
        out.append(f"{i:2}. {it['mechanism']}  {it['year']} Q{it['q']}  [{it['marks']} marks]  "
                   f"answer = {it['answer']}")
        out.append(f"     print: {it['source_file']}  p.{it['page']}")
        out.append(f"     topic: {it['topic']}")
    out.append("=" * 78)
    return "\n".join(out)


# ----------------------------------------------------------------- demo
if __name__ == "__main__":
    spec = generate_m7(seed=3)
    path = save_svg(spec)
    print("=" * 60)
    print("M7 COORDINATE-DRAWN SAMPLE  (twin of " + spec["anchor"] + ")")
    print("=" * 60)
    print("\nSTUDENT QUESTION:")
    print("  " + spec["stem"])
    print("\nASCII preview (# = shaded, . = inside rectangle):\n")
    print(ascii_preview(spec))
    print("\nexact coordinates:")
    for k, p in spec["points"].items():
        print(f"   {k} = ({p[0]}, {p[1]})")
    v = verify_figure(spec)
    print(f"\nFIGURE<->ANSWER consistency: shoelace(drawn)={v['area_from_drawn_polygon']}  "
          f"closed-form 3WH/8={v['closed_form_3WH_8']}  stated={v['stated_answer']}  "
          f"-> consistent={v['consistent']}")
    print(f"PARENT KEY: shaded area = {spec['answer']}   "
          f"(M7; ★ decompose / subtract corner triangles, no area formula; "
          f"trap: trusting the not-to-scale picture)")
    print(f"\nSVG saved: {path}")

    print("\n")
    print(render_worksheet(curated_worksheet(max_items=10)))
