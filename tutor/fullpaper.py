"""fullpaper.py — ONE command produces a COMPLETE AMC Upper Primary mock:
30 questions on the real ramp, as a STUDENT PAPER + an ANSWER KEY (two PDFs).

Real AMC Upper Primary shape (135 marks, 60 minutes, no calculator):
    Q1-10   3 marks each   warm-up        multiple choice A-E
    Q11-20  4 marks each   medium         multiple choice A-E
    Q21-25  5 marks each   hard           multiple choice A-E
    Q26-30  6/7/8/9/10     medal tail     integer answer 0-999

Q1-25 are CODE-COMPUTED multiple-choice items: the answer is produced by the same
function that writes the question, so it is correct by construction; distractors are
distinct and the key is unambiguous. Q26-30 come from the verified twin engine
(generate.make_item -> verify.py gate): unique answer inside the real-paper band.

Pure standard library + the existing engine. No network, no API, $0 to run.

CLI:  python -m tutor.fullpaper            # a complete paper
      python -m tutor.fullpaper --seed 3   # a different draw
"""
import argparse
import datetime
import os
import random

from tutor import generate, paper, verify


# --------------------------------------------------------------- MC helper
def _choices(rng, answer, distractors=()):
    """Return (list of (label, value), correct_label) with 5 distinct options."""
    pool = [answer]
    for d in distractors:
        if d not in pool:
            pool.append(d)
    if isinstance(answer, int):
        cand = [answer + 1, answer - 1, answer + 2, answer - 2, answer + 3,
                answer + 5, answer - 5, answer + 10, answer - 10, answer * 2]
        i = 0
        while len(pool) < 5 and i < len(cand):
            if cand[i] not in pool and cand[i] >= 0:
                pool.append(cand[i])
            i += 1
    k = 0
    while len(pool) < 5:                     # final guard for tiny answers
        c = answer + 100 + k
        if c not in pool:
            pool.append(c)
        k += 1
    pool = pool[:5]
    rng.shuffle(pool)
    labels = "ABCDE"
    return [(labels[i], pool[i]) for i in range(5)], labels[pool.index(answer)]


# --------------------------------------------------------------- EASY (3 marks)
def e_arith(rng):
    a, b, c = rng.randint(4, 9), rng.randint(4, 9), rng.randint(2, 9)
    return {"stem": f"What is the value of {a} x {b} + {c}?", "answer": a * b + c,
            "distractors": [a * (b + c), a * b - c, a * b],
            "method": f"Multiply first: {a}x{b}={a*b}, then add {c} = {a*b+c}.", "mech": "order of operations"}

def e_change(rng):
    price, note = rng.randint(12, 38), rng.choice([50, 100])
    return {"stem": f"A book costs ${price}. Maya pays with a ${note} note. How much change should she get?",
            "answer": note - price, "distractors": [note + price, price, note - price + 10],
            "method": f"${note} - ${price} = ${note-price}.", "mech": "subtraction"}

def e_fraction(rng):
    d, k = rng.choice([2, 3, 4, 5]), rng.randint(4, 9)
    t = d * k
    return {"stem": f"There are {t} children at a party. 1/{d} of them are boys. How many boys are there?",
            "answer": k, "distractors": [t - k, k + 1, t],
            "method": f"{t} divided by {d} = {k}.", "mech": "fraction of a quantity"}

def e_seq(rng):
    s, k = rng.randint(2, 9), rng.choice([2, 3, 4, 5])
    terms = [s + i * k for i in range(4)]
    return {"stem": f"What is the next number in the pattern {terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ...?",
            "answer": s + 4 * k, "distractors": [s + 5 * k, terms[3] + k - 1, terms[3] + 1],
            "method": f"Each term goes up by {k}, so next is {terms[3]}+{k}={s+4*k}.", "mech": "number pattern"}

def e_round(rng):
    n = rng.randint(1120, 8880)
    return {"stem": f"What is {n} rounded to the nearest hundred?", "answer": ((n + 50) // 100) * 100,
            "distractors": [(n // 100) * 100, ((n + 50) // 100) * 100 + 100, n],
            "method": f"The tens digit decides rounding; {n} -> {((n+50)//100)*100}.", "mech": "rounding"}

def e_remain(rng):
    H, U = rng.randint(150, 400), rng.randint(40, 120)
    return {"stem": f"A shop had {H} apples and sold {U} of them. How many are left?", "answer": H - U,
            "distractors": [H + U, U, H - U + 10], "method": f"{H} - {U} = {H-U}.", "mech": "subtraction"}

def e_mult(rng):
    b, n = rng.choice([6, 8, 12]), rng.randint(4, 9)
    return {"stem": f"Eggs are packed {b} to a box. How many eggs are in {n} boxes?", "answer": b * n,
            "distractors": [b + n, b * n + b, b * (n + 1)], "method": f"{b} x {n} = {b*n}.", "mech": "multiplication"}

def e_perim(rng):
    l = rng.randint(6, 12); w = rng.randint(3, l - 1)
    return {"stem": f"A rectangle is {l} cm long and {w} cm wide. What is its perimeter, in cm?",
            "answer": 2 * (l + w), "distractors": [l * w, l + w, 2 * l + w],
            "method": f"Perimeter = 2 x ({l}+{w}) = {2*(l+w)} cm.", "mech": "perimeter"}

def e_remainder(rng):
    d = rng.choice([3, 4, 5, 6, 7]); q = rng.randint(9, 20); r = rng.randint(1, d - 1)
    N = d * q + r
    return {"stem": f"What is the remainder when {N} is divided by {d}?", "answer": r,
            "distractors": [0, d - r, q], "method": f"{N} = {d}x{q} + {r}, remainder {r}.", "mech": "division"}

def e_half(rng):
    N = 2 * rng.randint(30, 90)
    return {"stem": f"What is half of {N}?", "answer": N // 2,
            "distractors": [N, N // 2 + 1, N * 2], "method": f"{N} divided by 2 = {N//2}.", "mech": "halving"}

def e_place(rng):
    n = rng.randint(1000, 9999); ans = (n // 100) % 10
    others = list({(n) % 10, (n // 10) % 10, (n // 1000) % 10} - {ans})
    while len(others) < 3:
        c = rng.randint(0, 9)
        if c != ans and c not in others:
            others.append(c)
    return {"stem": f"In the number {n}, which digit is in the hundreds place?", "answer": ans,
            "distractors": others[:3], "method": f"Hundreds digit of {n} is {ans}.", "mech": "place value"}

def e_count_mult(rng):
    m = rng.choice([3, 4]); nums = rng.sample(range(6, 40), 6)
    ans = sum(1 for x in nums if x % m == 0)
    return {"stem": f"How many of these numbers are multiples of {m}?   {', '.join(map(str, nums))}",
            "answer": ans, "distractors": [ans + 1, ans + 2, max(ans - 1, 0)],
            "method": f"Check each: {ans} are multiples of {m}.", "mech": "multiples"}

EASY = [e_arith, e_change, e_fraction, e_seq, e_round, e_remain,
        e_mult, e_perim, e_remainder, e_half, e_place, e_count_mult]


# --------------------------------------------------------------- MEDIUM (4 marks)
def m_area_cut(rng):
    l = rng.randint(8, 14); w = rng.randint(5, l - 1); s = rng.randint(2, min(w - 1, 4))
    return {"stem": f"A rectangle {l} cm by {w} cm has a square of side {s} cm cut from one corner. "
                    f"What area, in square cm, is left?", "answer": l * w - s * s,
            "distractors": [l * w, s * s, (l - s) * (w - s)],
            "method": f"{l}x{w} - {s}x{s} = {l*w} - {s*s} = {l*w-s*s}.", "mech": "area"}

def m_ratio(rng):
    r = rng.choice([2, 3, 4]); unit = rng.randint(5, 15); total = (1 + r) * unit
    return {"stem": f"Anna and Ben share ${total} in the ratio 1 : {r}. How many dollars does Ben get?",
            "answer": r * unit, "distractors": [unit, total, total // 2],
            "method": f"{1+r} parts = ${total}, so 1 part = ${unit}; Ben has {r} parts = ${r*unit}.",
            "mech": "ratio"}

def m_avg(rng):
    n = rng.choice([4, 5]); A = rng.randint(7, 14)
    others = [rng.randint(3, A + 5) for _ in range(n - 1)]
    ans = A * n - sum(others)
    if ans <= 0:
        others = [A] * (n - 1); ans = A
    return {"stem": f"The average of {n} numbers is {A}. {n-1} of the numbers are "
                    f"{', '.join(map(str, others))}. What is the other number?", "answer": ans,
            "distractors": [A, sum(others), ans + n], "method": f"Total = {A}x{n} = {A*n}; "
            f"other = {A*n} - {sum(others)} = {ans}.", "mech": "average"}

def m_packs(rng):
    C = rng.randint(22, 40); per = rng.choice([2, 3]); pack = rng.choice([5, 6, 8])
    need = C * per; ans = (need + pack - 1) // pack
    return {"stem": f"A class of {C} students each need {per} pencils. Pencils come in packs of {pack}. "
                    f"What is the smallest number of packs needed?", "answer": ans,
            "distractors": [need // pack, ans + 1, need], "method": f"Need {need} pencils; "
            f"{need}/{pack} rounds up to {ans} packs.", "mech": "division with rounding"}

def m_percent(rng):
    P = rng.choice([10, 20, 25, 50, 75]); T = 20 * rng.randint(3, 12); ans = T * P // 100
    return {"stem": f"What is {P}% of {T}?", "answer": ans,
            "distractors": [T - ans, T * P // 10, ans + 5], "method": f"{P}% of {T} = {ans}.",
            "mech": "percentage"}

def m_two_digit(rng):
    k = rng.choice([3, 4]); s = sorted(rng.sample(range(1, 10), k))
    return {"stem": f"Using the digits {', '.join(map(str, s))}, how many different two-digit numbers can "
                    f"be made if no digit is repeated?", "answer": k * (k - 1),
            "distractors": [k * k, (k - 1) * (k - 1), k * (k - 1) + k],
            "method": f"{k} choices for the first digit, {k-1} for the second: {k}x{k-1} = {k*(k-1)}.",
            "mech": "counting"}

def m_consec(rng):
    k = rng.choice([3, 4, 5]); s = rng.randint(4, 14); ans = sum(range(s, s + k))
    return {"stem": f"What is the sum of {k} consecutive whole numbers starting from {s}?", "answer": ans,
            "distractors": [k * s, ans + k, ans - k], "method": f"{'+'.join(str(s+i) for i in range(k))} = {ans}.",
            "mech": "consecutive sum"}

def m_speed(rng):
    v = rng.choice([40, 50, 60, 80]); t = rng.choice([2, 3, 4])
    return {"stem": f"A car travels at {v} km/h for {t} hours. How many km does it travel?", "answer": v * t,
            "distractors": [v + t, v * t + v, v * (t - 1)], "method": f"{v} x {t} = {v*t} km.", "mech": "rate"}

def m_buy(rng):
    x = rng.randint(2, 5); a = rng.randint(2, 6); y = rng.randint(2, 5); b = rng.randint(2, 6)
    ans = x * a + y * b
    return {"stem": f"Pens cost ${a} each and rulers cost ${b} each. What is the total cost of {x} pens and "
                    f"{y} rulers, in dollars?", "answer": ans,
            "distractors": [(x + y) * (a + b), x * b + y * a, ans + a],
            "method": f"{x}x${a} + {y}x${b} = ${x*a} + ${y*b} = ${ans}.", "mech": "two-step money"}

def m_next_multiple(rng):
    N = rng.randint(50, 200); d = rng.choice([6, 7, 8, 9]); ans = ((N // d) + 1) * d
    return {"stem": f"What is the smallest number greater than {N} that is a multiple of {d}?", "answer": ans,
            "distractors": [(N // d) * d, ans + d, N + d], "method": f"Next multiple of {d} after {N} is {ans}.",
            "mech": "multiples"}

def m_rule(rng):
    start = rng.randint(2, 5)
    terms = [start]
    for _ in range(3):
        terms.append(2 * terms[-1] - 1)
    ans = 2 * terms[-1] - 1
    return {"stem": f"A sequence starts at {start}. Each next number is double the one before, minus 1, giving "
                    f"{terms[0]}, {terms[1]}, {terms[2]}, {terms[3]}, ... What is the next number?",
            "answer": ans, "distractors": [2 * terms[-1], terms[-1] + terms[-2], ans - 1],
            "method": f"2 x {terms[-1]} - 1 = {ans}.", "mech": "recursive pattern"}

def m_square_area(rng):
    side = rng.randint(5, 11); P = 4 * side
    return {"stem": f"A square has a perimeter of {P} cm. What is its area, in square cm?", "answer": side * side,
            "distractors": [P, side * 4, (side + 1) ** 2], "method": f"Side = {P}/4 = {side}; area = {side}x{side} = {side*side}.",
            "mech": "perimeter and area"}

MEDIUM = [m_area_cut, m_ratio, m_avg, m_packs, m_percent, m_two_digit,
          m_consec, m_speed, m_buy, m_next_multiple, m_rule, m_square_area]


# --------------------------------------------------------------- HARD (verified, pushed)
# Every hard question is built straight from a real mechanism solver: the answer is
# COMPUTED and checked unique; the stem is rendered by generate.STEMS (same wording engine
# as the verified twins). AMC integer answers are 0-999, so hardness comes from STRUCTURE
# (more constraints, longer chains, bigger search) -- never from inflating the numbers.
TYPE_MECH = {"digit_extremes": "M1", "constrained_number": "M2", "op_order": "M3",
             "fraction_remainder": "M4", "iterate_map": "M6", "bounded_walk": "M6",
             "count_digit_in_list": "M5", "crt_candidates": "M5", "choose_sum_divisible": "M5"}


def _hard_item(rng, typ, params):
    mech = TYPE_MECH[typ]
    try:
        if not verify.is_unique(mech, params):        # no/duplicate solution -> reject
            return None
        ans = verify.MODULES[mech].solve(params)
    except (StopIteration, ValueError, AssertionError, ZeroDivisionError):
        return None
    if ans is None:
        return None
    return {"stem": generate.STEMS[typ](params), "answer": ans, "mech": mech,
            "method": generate.METHOD[mech][0], "trap": generate.METHOD[mech][1],
            "fixed_choices": params["candidates"] if typ == "crt_candidates" else None}


def _draw_hard(rng, ctor, int_only=False, tries=300):
    for _ in range(tries):
        typ, params = ctor(rng)
        it = _hard_item(rng, typ, params)
        if it is None or (int_only and not 0 <= it["answer"] <= 999):
            continue
        return it
    raise RuntimeError(f"hard family {ctor.__name__} produced nothing valid")


# ---- hard families for the multiple-choice discriminators (Q21-25) ----
def hm_constrained(rng):
    parity = rng.choice(["even", "odd"])
    mult = rng.choice([3, 9]) if parity == "odd" else rng.choice([4, 6])  # keep it satisfiable
    return "constrained_number", {"type": "constrained_number", "range": [100, 999],
            "want": "smallest", "predicates": [parity, ["multiple_of", mult],
            ["contains_digit", rng.choice([3, 5, 7, 9])], ["no_digit", 0], "all_distinct"]}

def hm_crt(rng):
    return "crt_candidates", generate._p_crt_candidates(rng, None)

def hm_op_order(rng):
    return "op_order", generate._p_op_order(rng, None)

def hm_fraction(rng):
    return "fraction_remainder", generate._p_fraction_remainder(rng, None)

def hm_choose_sum(rng):
    start, nn = rng.choice([1, 2]), rng.choice([10, 11, 12])
    return "choose_sum_divisible", {"type": "choose_sum_divisible",
            "set": list(range(start, start + nn)), "choose": 3, "divisor": rng.choice([3, 4])}

HARD_MC = [hm_constrained, hm_crt, hm_op_order, hm_fraction, hm_choose_sum]


# ---- hardest families for the integer-answer tail (Q26-30) ----
def hi_digit_extremes(rng):
    return "digit_extremes", {"type": "digit_extremes", "digits": rng.sample(range(1, 10), 6),
            "groups": [3, 3]}

def hi_count_digit(rng):
    v = rng.choice([3, 4, 6])
    return "count_digit_in_list", {"type": "count_digit_in_list", "start": v, "step": v,
            "count": rng.choice([250, 300]), "digit": rng.choice([0, 1, 2])}

def hi_iterate(rng):
    return "iterate_map", {"type": "iterate_map", "map": "digit_square_sum",
            "seed": rng.randint(1000, 9999), "index": rng.randint(5000, 9000)}

def hi_bounded(rng):
    b, L = rng.choice([1, 2]), rng.choice([10, 12, 14])
    return "bounded_walk", {"type": "bounded_walk", "length": L, "low": -b, "high": b, "start": 0}

def hi_choose_sum(rng):
    start, nn = rng.choice([1, 2, 3]), rng.choice([13, 14, 15, 16])
    return "choose_sum_divisible", {"type": "choose_sum_divisible",
            "set": list(range(start, start + nn)), "choose": 3, "divisor": rng.choice([3, 4])}

HARD_INT = [hi_digit_extremes, hi_count_digit, hi_iterate, hi_bounded, hi_choose_sum]


# --------------------------------------------------------------- assembly
def build_paper(seed=0):
    rng = random.Random(seed)
    items = []
    n = 0

    def add_mc(stem, answer, distractors, marks, mech, method, fixed=None):
        nonlocal n
        n += 1
        if fixed:
            opts = list(fixed)
            rng.shuffle(opts)
            labels = "ABCDE"
            choices = [(labels[i], opts[i]) for i in range(len(opts))]
            correct = labels[opts.index(answer)]
        else:
            choices, correct = _choices(rng, answer, distractors)
        assert sum(1 for _, v in choices if v == answer) == 1, f"ambiguous key Q{n}"
        items.append({"n": n, "marks": marks, "section": "MC", "stem": stem,
                      "choices": choices, "correct": correct, "answer": answer,
                      "method": method, "mech": mech})

    for fam in rng.sample(EASY, 10):                  # Q1-10 warm-up
        q = fam(rng)
        add_mc(q["stem"], q["answer"], q.get("distractors", ()), 3, q["mech"], q["method"])
    for fam in rng.sample(MEDIUM, 10):                # Q11-20 medium
        q = fam(rng)
        add_mc(q["stem"], q["answer"], q.get("distractors", ()), 4, q["mech"], q["method"])
    for ctor in rng.sample(HARD_MC, 5):               # Q21-25 hard, verified, multiple choice
        it = _draw_hard(rng, ctor)
        add_mc(it["stem"], it["answer"], (), 5, it["mech"], it["method"], it["fixed_choices"])
    for marks, ctor in zip([6, 7, 8, 9, 10], rng.sample(HARD_INT, 5)):  # Q26-30 hardest, integer
        it = _draw_hard(rng, ctor, int_only=True)
        n += 1
        items.append({"n": n, "marks": marks, "section": "INT", "stem": it["stem"],
                      "choices": None, "correct": None, "answer": it["answer"],
                      "method": it["method"], "trap": it["trap"], "mech": it["mech"],
                      "anchor": "generated"})
    return items


# --------------------------------------------------------------- rendering
def _opt_line(choices):
    return "     ".join(f"({lab}) {val}" for lab, val in choices)


def student_lines(items):
    L = [("AMC-buddy Full Mock  -  Upper Primary (Year 6)", "F2", 16, 0, 0),
         ("Student Paper", "F2", 12, 0, 8),
         ("30 questions   -   60 minutes   -   no calculator   -   diagrams are not drawn to scale",
          "F1", 9.5, 0, 5),
         ("Q1-25 multiple choice (mark one letter)   -   Q26-30 write an integer from 0 to 999",
          "F1", 9.5, 0, 3),
         ("Name: __________________      Date: ____________      Score: ____ / 135", "F1", 10, 0, 12)]
    headers = {1: "Questions 1-10   -   3 marks each",
               11: "Questions 11-20   -   4 marks each",
               21: "Questions 21-25   -   5 marks each",
               26: "Questions 26-30   -   6, 7, 8, 9, 10 marks   -   integer answer"}
    for it in items:
        if it["n"] in headers:
            L.append((headers[it["n"]], "F2", 11, 0, 14))
        L.append((f"{it['n']}.   {it['stem']}", "F1", 11, 0, 9))
        if it["section"] == "MC":
            L.append((_opt_line(it["choices"]), "F1", 10.5, 16, 4))
        else:
            L.append(("Answer (an integer from 0 to 999): ____________", "F1", 10, 16, 6))
    return L


def answer_lines(items):
    quick = "   ".join(f"{it['n']}-{it['correct']}" for it in items if it["section"] == "MC")
    L = [("AMC-buddy Full Mock  -  Answer Key & Methods", "F2", 16, 0, 0),
         ("Q1-25 every answer is code-computed; Q26-30 each passed verify.py before printing",
          "F1", 9.5, 0, 8),
         ("Quick mark (multiple choice):  " + quick, "F1", 9.5, 0, 8),
         ("", "F1", 10, 0, 2)]
    for it in items:
        if it["section"] == "MC":
            L.append((f"Q{it['n']}.   {it['correct']}   ( = {it['answer']} )    "
                      f"[{it['marks']} marks - {it['mech']}]", "F2", 11, 0, 11))
            L.append((f"method: {it['method']}", "F1", 10, 16, 4))
        else:
            L.append((f"Q{it['n']}.   answer = {it['answer']}    "
                      f"[{it['marks']} marks - {it['mech']} - twin of {it['anchor']}]", "F2", 11, 0, 11))
            L.append((f"* fastest method: {it['method']}", "F1", 10, 16, 4))
            L.append((f"x the trap: {it['trap']}", "F1", 10, 16, 3))
    return L


def main():
    ap = argparse.ArgumentParser(description="Print a complete AMC Upper Primary mock as two PDFs.")
    ap.add_argument("--seed", type=int, default=0, help="draw a different complete paper")
    ap.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "..", "papers"))
    args = ap.parse_args()

    items = build_paper(args.seed)
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)
    tag = datetime.date.today().isoformat() + (f"_v{args.seed}" if args.seed else "")
    student = os.path.join(outdir, f"AMC_full_{tag}_student.pdf")
    answers = os.path.join(outdir, f"AMC_full_{tag}_answers.pdf")

    paper.write_pdf(student_lines(items), student, "AMC-buddy Full Mock - Student Paper")
    paper.write_pdf(answer_lines(items), answers, "AMC-buddy Full Mock - Answer Key")

    print(f"30-question paper ready  (seed {args.seed})")
    print("STUDENT PAPER : " + student)
    print("ANSWER KEY    : " + answers)


if __name__ == "__main__":
    main()
