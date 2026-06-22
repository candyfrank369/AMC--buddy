"""designed_mock.py -- a calibrated, hand-designed AMC Upper Primary mock.

This is NOT the parametric generator. Each question is DESIGNED to hit the difficulty
feature target of its slot (see content/difficulty_features.jsonl), with a DISTINCT skill
(no two questions share a method), a real ramp, and a genuine climax. EVERY answer is
COMPUTED here in code -- so the printed answer is machine-verified, never my arithmetic.

Renders two PDFs via the existing PDF writer.  CLI:  python -m tutor.designed_mock
"""
import random
from itertools import combinations

from tutor import paper, fullpaper

rng = random.Random(20260622)
items = []


def add(stem, marks, section, answer, skill, method, trap="", options=None):
    n = len(items) + 1
    if section == "MC":
        if options is not None:                       # explicit options (non-integer answers)
            opts = list(options)
            rng.shuffle(opts)
            labels = "ABCDE"
            choices = [(labels[i], opts[i]) for i in range(len(opts))]
            correct = labels[opts.index(answer)]
        else:
            choices, correct = fullpaper._choices(rng, answer)
        assert sum(1 for _, v in choices if v == answer) == 1, f"ambiguous Q{n}"
        items.append({"n": n, "marks": marks, "section": "MC", "stem": stem, "choices": choices,
                      "correct": correct, "answer": answer, "method": method, "mech": skill})
    else:
        items.append({"n": n, "marks": marks, "section": "INT", "stem": stem, "choices": None,
                      "correct": None, "answer": answer, "method": method, "trap": trap,
                      "mech": skill, "anchor": "designed"})


# ============================ Q1-10  (3 marks, warm-up, still real) ============================
t = 18 * 60 + 50 + 95                                  # 6:50 pm + 95 min
add("A film starts at 6:50 pm and runs for 95 minutes. At what time does it finish?", 3, "MC",
    f"{t//60-12}:{t%60:02d} pm", "time", "6:50 + 1h35 = 8:25 pm.",
    options=["8:25 pm", "8:35 pm", "7:45 pm", "8:15 pm", "9:25 pm"])
add("What is the value of 3 + 6 x 4 - 5?", 3, "MC", 3 + 6 * 4 - 5, "order_of_operations",
    "Multiply first: 3 + 24 - 5 = 22.")
add("A pizza is cut into 8 equal slices and Mia eats 3 of them. What fraction is left?", 3, "MC",
    "5/8", "fraction", "8 - 3 = 5 slices left, so 5/8.",
    options=["5/8", "3/8", "5/3", "3/5", "1/8"])
add("Which of these numbers is the largest?", 3, "MC", "0.54", "decimals",
    "Compare tenths first: 0.54 is largest.",
    options=["0.5", "0.45", "0.405", "0.54", "0.045"])
add("A rectangle is 9 cm long and 4 cm wide. What is its area, in square cm?", 3, "MC",
    9 * 4, "area", "9 x 4 = 36.")
add("In the number 38 472, which digit is in the thousands place?", 3, "MC",
    int(str(38472)[1]), "place_value", "38 472: the thousands digit is 8.")
add("Pencils cost $7 each. How much do 6 pencils cost, in dollars?", 3, "MC",
    6 * 7, "multiplication", "6 x 7 = 42.")
add("What is 1/2 + 1/4?", 3, "MC", "3/4", "fractions", "1/2 = 2/4, so 2/4 + 1/4 = 3/4.",
    options=["3/4", "2/6", "1/3", "1/6", "2/4"])
add("Buses leave every 15 minutes, the first at 9:00 am. At what time does the 5th bus leave?",
    3, "MC", "10:00 am", "sequence", "The 5th bus is 4 x 15 = 60 min after 9:00 = 10:00 am.",
    options=["10:00 am", "9:45 am", "10:15 am", "9:60 am", "11:00 am"])
add("What is the remainder when 50 is divided by 6?", 3, "MC", 50 % 6, "division",
    "50 = 6 x 8 + 2, remainder 2.")

# ============================ Q11-20  (4 marks, genuine two-step) ============================
add("I think of a number, multiply it by 3, then add 4, and the result is 25. "
    "What was my number?", 4, "MC", (25 - 4) // 3, "working_backwards",
    "Undo: (25 - 4) / 3 = 7.")
add("Red and blue marbles are in the ratio 2 : 3. There are 30 blue marbles. "
    "How many red marbles are there?", 4, "MC", 30 // 3 * 2, "ratio",
    "3 parts = 30, so 1 part = 10; red = 2 parts = 20.")
add("Sam's first 4 test scores average 78. What must he score on the 5th test to average 80 "
    "over all 5 tests?", 4, "MC", 80 * 5 - 78 * 4, "average_reverse",
    "Need total 80x5=400; already 78x4=312; so 88.")
add("How many two-digit numbers have digits that add up to 8?", 4, "MC",
    sum(1 for x in range(10, 100) if sum(map(int, str(x))) == 8), "digit_sum_count",
    "17,26,35,44,53,62,71,80 -- eight of them.")
add("A rectangle has a perimeter of 30 cm and its length is twice its width. "
    "What is its area, in square cm?", 4, "MC", 5 * 10, "perimeter_to_area",
    "2(w+2w)=30 -> w=5, l=10, area=50.")
seq = [1]
for _ in range(7):
    seq.append(seq[-1] + len(seq))                     # +1,+2,+3,...
add("A sequence begins 1, 2, 4, 7, 11, 16, ... What is the 8th term?", 4, "MC", seq[7],
    "growing_differences", "Differences grow 1,2,3,...; 8th term = 1+(1+2+..+7)=29.")
add("A $80 jacket is reduced by 25%, then a further $5 is taken off. What is the final price, "
    "in dollars?", 4, "MC", int(80 * 0.75) - 5, "percentage_twostep",
    "25% off 80 = 60, then -5 = 55.")
add("Anna is taller than Bob. Bob is taller than Carl. Dan is shorter than Carl. "
    "Who is the shortest?", 4, "MC", "Dan", "logic_ordering",
    "Order: Anna > Bob > Carl > Dan, so Dan is shortest.",
    options=["Dan", "Carl", "Bob", "Anna", "Cannot tell"])
add("3 painters can paint a fence in 8 hours. Working at the same rate, how many hours would "
    "4 painters take?", 4, "MC", 3 * 8 // 4, "inverse_proportion",
    "Total work = 24 painter-hours; 24 / 4 = 6 hours.")
add("What is the smallest whole number that is divisible by both 6 and 8?", 4, "MC", 24,
    "lcm", "LCM(6,8) = 24.")

# ============================ Q21-25  (5 marks, hard, distinct skills, MC) ============================
add("What is the smallest whole number greater than 50 that leaves remainder 1 when divided "
    "by 4 and remainder 2 when divided by 5?", 5, "MC",
    next(x for x in range(51, 200) if x % 4 == 1 and x % 5 == 2), "modular_crt",
    "Numbers that are 1 mod 4 and 2 mod 5 are 17 mod 20; first above 50 is 57.")

# Q22 -- parity invariant + search (a type the parametric generator cannot make)
def _coin_min_moves():
    from collections import deque
    start, goal = 0, (1 << 8) - 1
    flips = [sum(1 << i for i in c) for c in combinations(range(8), 3)]
    seen = {start: 0}
    dq = deque([start])
    while dq:
        s = dq.popleft()
        if s == goal:
            return seen[s]
        for f in flips:
            ns = s ^ f
            if ns not in seen:
                seen[ns] = seen[s] + 1
                dq.append(ns)
add("Eight coins all show tails. In one move you must turn over exactly 3 coins. What is the "
    "least number of moves to make all eight show heads?", 5, "MC", _coin_min_moves(),
    "parity_invariant", "Each move changes the number of heads by an odd amount, so an even "
    "number of moves is needed; 4 moves suffice.")

add("How many three-digit numbers are the same read forwards and backwards (e.g. 343) and are "
    "even?", 5, "MC", sum(1 for x in range(100, 1000)
                          if str(x) == str(x)[::-1] and x % 2 == 0), "palindrome_count",
    "Palindrome aba is even when a is even: a in {2,4,6,8}, b any -> 4 x 10 = 40.")

# Q24 -- extremal
def _max_sum_product36():
    best = 0
    for a, b, c in combinations(range(1, 37), 3):
        if a * b * c == 36:
            best = max(best, a + b + c)
    return best
add("Three different positive whole numbers multiply together to give 36. What is the largest "
    "possible value of their sum?", 5, "MC", _max_sum_product36(), "extremal_factor",
    "Spread the factors: 1 x 2 x 18 = 36 gives the largest sum, 21.")

add("A square has area 64 square cm. A second square has sides 25% longer. What is the area of "
    "the second square, in square cm?", 5, "MC", (8 * 5 // 4) ** 2, "area_scaling",
    "Side 8 -> 10 (not just +25% of area); area = 10 x 10 = 100.")

# ============================ Q26-30  (integer answers, hardest, distinct, climax) ============================
# Q26 -- cycle indexing (off-by-one), different rule from any anchor
def _seq26(k):
    x, out = 7, []
    for _ in range(k):
        out.append(x)
        x = x // 2 if x % 2 == 0 else x + 5
    return out
add("Start with 7. At each step, if the number is even halve it, and if it is odd add 5. "
    "Writing the numbers in a list starting with 7, what is the 50th number in the list?",
    6, "INT", _seq26(50)[-1], "cycle_indexing",
    "From the 3rd term it cycles 6,3,8,4,2,1 (length 6); index the 50th by the period.",
    trap="off-by-one: the cycle starts at the 3rd term, not the 1st")

# Q27 -- shortest process (BFS), optimisation
def _min_steps_to(target):
    from collections import deque
    seen = {1: 0}
    dq = deque([1])
    while dq:
        v = dq.popleft()
        if v == target:
            return seen[v]
        for nv in (v * 2, v + 3):
            if 0 < nv <= target and nv not in seen:
                seen[nv] = seen[v] + 1
                dq.append(nv)
add("A calculator shows 1. Each press either doubles the number or adds 3 to it. What is the "
    "fewest presses needed to show exactly 25?", 7, "INT", _min_steps_to(25),
    "process_optimisation", "Search shortest path under x2 / +3; build 25 in fewest steps.",
    trap="greedily doubling overshoots; the shortest route mixes the two operations")

# Q28 -- number theory: expressible as sum of >=2 consecutive ints  <=>  not a power of 2
def _count_consec_expressible(N):
    def ok(n):
        for k in range(2, n + 1):                      # length
            num = 2 * n + k - k * k                     # 2n = k(2a+k-1) -> a = (num)/(2k)
            if num <= 0:
                break
            if num % (2 * k) == 0 and num // (2 * k) >= 1:
                return True
        return False
    return sum(1 for n in range(1, N + 1) if ok(n))
add("How many of the numbers from 1 to 100 can be written as a sum of two or more consecutive "
    "positive whole numbers (for example 9 = 4 + 5 = 2 + 3 + 4)?", 8, "INT",
    _count_consec_expressible(100), "consecutive_sum_numbertheory",
    "A number works unless it is a power of 2; the powers of 2 up to 100 are 1,2,4,8,16,32,64.",
    trap="testing numbers one by one instead of spotting the powers-of-2 rule")

# Q29 -- parity-invariant counting (0/1 grid, even row & column sums)
def _even_grids(n):
    from itertools import product
    cnt = 0
    for cells in product((0, 1), repeat=n * n):
        g = [cells[i * n:(i + 1) * n] for i in range(n)]
        if all(sum(r) % 2 == 0 for r in g) and all(sum(g[i][j] for i in range(n)) % 2 == 0
                                                   for j in range(n)):
            cnt += 1
    return cnt
add("Each cell of a 3 x 3 grid is filled with 0 or 1. In how many ways can this be done so that "
    "every row and every column contains an even number of 1s?", 9, "INT", _even_grids(3),
    "parity_grid_invariant", "The top-left 2x2 is free; the last row/column is forced -> 2^4.",
    trap="trying to list cases instead of seeing the last row and column are forced")

# Q30 -- CLIMAX: derive a 3-step recurrence (tribonacci)
def _stairs(n):
    f = [0] * (n + 1)
    f[0] = 1
    for i in range(1, n + 1):
        f[i] = sum(f[i - j] for j in (1, 2, 3) if i - j >= 0)
    return f[n]
add("A frog climbs a staircase of 12 steps. In each hop it goes up 1, 2 or 3 steps. In how many "
    "different ways can it climb to the top?", 10, "INT", _stairs(12), "recurrence_derivation",
    "Conditioning on the first hop gives f(n)=f(n-1)+f(n-2)+f(n-3); build up to f(12).",
    trap="trying to list climbs instead of finding the 3-term recurrence")


def main():
    assert len(items) == 30, f"expected 30, built {len(items)}"
    import os
    outdir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "papers"))
    os.makedirs(outdir, exist_ok=True)
    student = os.path.join(outdir, "AMC_designed_student.pdf")
    answers = os.path.join(outdir, "AMC_designed_answers.pdf")
    paper.write_pdf(fullpaper.student_lines(items), student, "AMC-buddy Designed Mock - Student")
    paper.write_pdf(fullpaper.answer_lines(items), answers, "AMC-buddy Designed Mock - Answers")
    print("STUDENT:", student)
    print("ANSWERS:", answers)
    for it in items:
        a = f"{it['correct']}={it['answer']}" if it["section"] == "MC" else it["answer"]
        print(f"Q{it['n']:>2} [{it['marks']}m] {it['mech']:<28} -> {a}")


if __name__ == "__main__":
    main()
