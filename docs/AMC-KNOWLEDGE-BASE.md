# AMC Knowledge Base — the 8 discriminator mechanisms (M1–M8)

One card per mechanism. Each is grounded in **real Upper Primary anchors** from `content/questions.jsonl`
(✷ = the flagship anchor used for the worked methods; ✱ on a year means it sits in the hard tail Q21–30).
Every card gives **what it tests · recognition trigger · real anchors · TWO methods (★ = the method a Year-6
can do fastest) · the trap · twin recipe · how verify.py checks it**. This file is the teaching source of
truth; `verify.py` (Phase 3) implements the "how verify.py checks it" line — no engine code exists yet.

> Difficulty ruler reminder (CLAUDE.md rule #1): difficulty is NEVER invented. Every generated twin is a
> parameterised copy of a *specific* anchor below and must preserve that anchor's mechanism.
> Generatability: **M1–M6** fully code-verifiable (generate freely) · **M7** via coordinate-drawn figures ·
> **M8** generate the numeric/graph ones, **CURATE** the novel-visual ones (folding, 3-D views).

---

## M1 — Place-value extreme value
**What it tests.** Building the largest/smallest number — or the max/min of a *sum or difference* of numbers —
by deciding which digit lands in which **weighted column**. The insight: only the column weights
(×100, ×10, ×1) matter; the split into separate numbers is a distraction.

**Recognition trigger.** Digit *cards* to be placed into positions; "largest minus smallest"; "form two
3-digit numbers and add"; max/min of a sum/product from a fixed digit set.

**Real anchors.**
- ✷ **2024 Q26✱ = 792** — digits 1–6 form two 3-digit numbers, added; max sum − min sum.
- **2013 UP Q5 = 41976** (B) — largest − smallest 5-digit number from cards 1–5.
- **2010 UP Q8 = 495** (B) — largest − smallest 3-digit from 2,7,5 (the small, early-question version).

**Two methods (2024 Q26).** Sum of the two numbers = 100·(h₁+h₂) + 10·(t₁+t₂) + (u₁+u₂).
- **Method A — build both numbers.** Construct the max-sum pair (e.g. 642+531) and the min-sum pair, then
  subtract. Works, but you juggle six digits across two numbers and it is easy to misplace one.
- **★ Method B — sort into columns (Year-6-fastest).** Ignore "two numbers". For the **max** put the biggest
  digits in the hundreds column: hundreds {6,5}, tens {4,3}, units {2,1} → 100·11+10·7+3 = 1173. For the
  **min** swap: hundreds {1,2}, units {5,6} → 381. The tens cancel, so
  **difference = 99 × (hundreds-sum − units-sum) = 99 × (11−3) = 792.**

**The trap.** Tracking the two whole numbers instead of the columns; reusing a digit; getting the sign of the
difference backwards. (Setters reward seeing that tens cancel.)

**Twin recipe.** Parameterise: digit set (1..n or an arbitrary distinct set), how many numbers k, digits per
number, and whether the question asks max, min, or their difference. Keep within the real band by matching
column count to the anchor.

**How verify.py checks it.** Enumerate every assignment of the digit set into the column structure; confirm a
**unique** extremal value; difficulty proxy = number of columns × digits (must sit in the anchor's band);
distractors are produced by NAMED mistakes — "summed the numbers not the columns", "put a digit in the wrong
column", "min−max instead of max−min".

---

## M2 — Stacked-constraint number
**What it tests.** Finding the number(s) meeting several simultaneous conditions at once, by **ordering the
constraints from most- to least-pruning** and using fast divisibility tests (digit-sum for ÷9 and ÷3, last
digit for even/÷5). Includes cryptarithms and "bracketing" (n(n+1) < target < (n+1)(n+2)).

**Recognition trigger.** A bulleted list of conditions ("even · multiple of 9 · contains a 5 · no 0 · all
different"); "smallest/largest number such that…"; "divisible by"; digit-pattern puzzles; "first time the
product exceeds…".

**Real anchors.**
- ✷ **2025 Q26✱ = 576** — smallest 3-digit that is even, a multiple of 9, contains a 5, has no 0, all digits
  different.
- **2024 Q18 = 14** (B) — count of 20–50 divisible by their unit digit. · **2019 Q29✱ = 15** — 20A​M​C19
  divisible by 9 (digit-sum constraint). · **2018 Q26✱ = 918** — cryptarithm a+ab+abc+1000 = 2018.
- **2019 Q28✱ = 125** & **2011 Q29✱ = 997** & **2013 Q19 = 992** — age "bracketing" (product crosses a bound).
- **2011 Q26✱ = 336** (smallest ÷42 with two odd digits) · **2010 Q29✱ = 87** (digit-append) · **2009 Q16 = 7**.

**Two methods (2025 Q26).**
- **★ Method A — order by pruning power (Year-6-fastest).** "Smallest" ⇒ make the hundreds digit as small as
  possible, then tens, then units. Hardest filters first: multiple of 9 ⇒ digit-sum 9 or 18; even ⇒ last digit
  even; must contain a 5; no 0; all different. Walking hundreds = 1,2,3,4 each fails (no even, distinct,
  digit-sum-9/18 number containing 5 exists). Hundreds = 5: 5_ _ with digit-sum 18, even, distinct →
  5,7,6 → **576**.
- **Method B — full filter.** List every 3-digit multiple of 9 and apply the other tests. Reliable but slow.

**The trap.** Applying the weak constraints first (huge search); forgetting "smallest" also minimises tens then
units; dropping the "distinct / no-zero" filters.

**Twin recipe.** Pick 3–5 constraints from {parity, ÷9/÷3/÷11, contains-digit, distinct digits, no-zero,
bracketing} and ask smallest/largest/how-many. Parameterise the range and the divisor.

**How verify.py checks it.** Enumerate the range, apply the constraint set, confirm a **unique** answer;
difficulty proxy = how many candidates survive until the *last* constraint; distractors drop exactly one
constraint each (named: "forgot even", "forgot all-different", "allowed a 0").

---

## M3 — Non-commutative operation ordering
**What it tests.** Choosing the order to apply a set of affine operations (×, +, ÷, −) — each used once — to
maximise/minimise the result. The key idea: the operations **don't commute**, and a ×k helps most when the
running value is already large, so **defer multiplications** and do small-value additions/divisions early.

**Recognition trigger.** "Visit in the order that maximises…"; a list of operations each applied once; "best
order"; a chain where you control the sequence.

**Real anchors.**
- ✷ **2024 Q27✱ = 270** — start $10; grandparents apply +10, ×2, (÷2 then +50), (×2 then +5); choose the visit
  order that maximises the final amount. *(The only clean Upper-Primary M3 anchor in the corpus — M3 is rare,
  so generate M3 twins sparingly and tag-check against this anchor.)*

**Two methods (2024 Q27).**
- **Method A — try the orders.** 4! = 24 orderings; compute each. Feasible but laborious and error-prone.
- **★ Method B — the deferral principle (Year-6-fastest).** A ×2 multiplies *everything* accumulated so far, so
  it pays to apply ×2 operations **last**, when the pot is biggest; apply the value-shrinking "halve then +50"
  **early** (when halving costs little and the +50 still lands); additive boosts (+10) before the big
  multiplies. This ordering yields **270**; you only sanity-check one or two neighbouring orders.

**The trap.** Assuming order doesn't matter; multiplying early; mishandling the compound op (Grampa Charles
*halves then* adds 50 — halving first is what makes "go early" correct).

**Twin recipe.** 3–4 operations of the form x ↦ a·x + b; ask max (or min) over all orderings. Parameterise the
a's and b's, keeping one ×, one ÷, two +.

**How verify.py checks it.** Brute-force all permutations, compute each, confirm a **unique** optimum; difficulty
proxy = gap between best and second-best ordering (too large ⇒ too easy); distractors = specific sub-optimal
orderings (named: "multiplied too early", "added after the last ×").

---

## M4 — Working backwards
**What it tests.** Inverting a forward chain from a known endpoint to the start — undo each step, **in reverse
order**, with its inverse operation. Covers "doubling/halving" machines, fraction-of-remainder problems, and
meeting/refilling situations.

**Recognition trigger.** "The final answer is X — what was the original?"; a process described forwards with the
end state given; "after spending/selling…, X remain"; reverse-engineer a starting amount.

**Real anchors.**
- ✷ **2013 UP Q8 = 7** (C) — double, +2, then halve, −2 → 6; find the original.
- **2021 Q30✱ = 117** — a+b = 11.63; shifting one decimal point left gives 5.87; find 100·(a−b).
- **2021 Q28✱ = 45** (hare runs the wrong way, meets at halfway) · **2009 Q30✱ = 7** (temples, double at each
  river, 0 left) · **2025 Q22✱ = 80** (cupcakes) · **2025 Q23✱ = 28th** · **2022 Q17 = 24** · **2009 Q2 = 13**.

**Two methods (2013 Q8).**
- **★ Method A — reverse the chain (Year-6-fastest).** Start at the end (6) and undo each step with its inverse,
  last-step-first: 6 → (undo −2) **+2 = 8** → (undo ÷2) **×2 = 16** → (undo +2) **−2 = 14** → (undo ×2)
  **÷2 = 7**. Original = **7**.
- **Method B — forward algebra.** ((2x+2)/2) − 2 = x − 1 = 6 ⇒ x = 7.

**The trap (important — this is a real anchor-keeping error).** Reporting an **intermediate value of the reverse
chain as the answer.** Here the reverse chain passes through 14 on its way to 7; CLAUDE.md's M4 anchor wrongly
recorded "Q8 = 14". The trap is *"stopping one step early"* / mistaking a midpoint for the start. Also: undoing
in the wrong order, or using the wrong inverse.

**Twin recipe.** A chain of 3–5 invertible operations (+, −, ×, ÷, decimal shift, take-a-fraction), give the
endpoint, ask for the start. Parameterise operations and constants; keep all steps invertible.

**How verify.py checks it.** Simulate **forward** from the candidate start and confirm it reaches the endpoint;
confirm the start is unique; distractors are exactly the intermediate values of the reverse chain (named
"stopped one step early") and wrong-inverse results.

---

## M5 — Organised enumeration / modular bucketing
**What it tests.** Systematic counting with **no missing and no double counts**: bucket by remainder (mod),
build an ordered table, split into clean cases, or use a combination count. The hallmark official phrase
(2013 Q27): *"a modulo arithmetic argument… presented so it can be understood by primary students."*

**Recognition trigger.** "How many ways / numbers / arrangements?"; "distinct totals"; divisibility-driven
counts; lattice/grid configurations; "count the … with property P".

**Real anchors.**
- ✷ **2013 UP Q27✱ = 76** — choose 3 different of 1–12 with sum divisible by 3 ("three piles").
- **2025 Q28✱ = 12** (sparse 4×4 grids) · **2024 Q28✱ = 199** (count digit '0' in 5…1500) ·
  **2020 Q28✱ = 20** (even 3-digit, digit-sum 8) · **2020 Q29✱ = 50** (PIN on edge-adjacent keypad) ·
  **2022 Q28✱ = 151** (distinct sums of three odds) · **2022 Q29✱ = 150** (C(5,2)·C(6,2) relay teams) ·
  **2013 Q26✱ = 4** (bags for $4/kg) · **2019 Q30✱ = 80** (Hugh not between) · **2012 Q21✱ = 11** (squares
  from points) · **2020 Q30✱ = 636** (digit stream). *(M5 is the most common tail mechanism — 37 anchors.)*

**Two methods (2013 Q27).**
- **★ Method A — residue piles (Year-6-fastest).** Split 1–12 by remainder mod 3 into three piles of four:
  R0 {3,6,9,12}, R1 {1,4,7,10}, R2 {2,5,8,11}. A sum is divisible by 3 ⇔ the three come **all from one pile**
  (3 · C(4,3) = 12) **or one from each pile** (4·4·4 = 64). Total **76**.
- **Method B — brute list.** Check all C(12,3) = 220 triples. Correct, gives no insight, infeasible under time.

**The trap.** Missing a case (counting "one from each" but forgetting "all from one pile"); double-counting
ordered vs unordered; off-by-one at range ends (the classic in digit-counting twins).

**Twin recipe.** Choose a set + a divisor, or a counting frame (digits with a property / arrangements with a
restriction / lattice configurations). Parameterise modulus and set size; keep the "two clean cases" structure.

**How verify.py checks it.** Code enumerates exhaustively and returns the count; the proposed answer must match;
difficulty proxy = size of the *naïve* search vs. the structured count (a real-band twin needs the structure to
matter); distractors = "counted ordered not unordered", "forgot the all-same-bucket case", "included an endpoint
it shouldn't".

---

## M6 — Sequence / pattern / recurrence
**What it tests.** Spotting the rule (arithmetic, geometric, recursive, **cyclic/eventually-periodic**), then
extrapolating or indexing a far-out term **by period** rather than by brute iteration.

**Recognition trigger.** "…continues…"; "the nth / 2024th number"; lists that cycle or return to start;
figurate or growing patterns; Fibonacci-style "ways to reach".

**Real anchors.**
- ✷ **2024 Q29✱ = 89** — start 2024, repeatedly sum the squares of the digits; find the 2024th term (a cycle).
- **2024 Q30✱ = 41** (stepping stones, Fibonacci-like) · **2022 Q26✱ = 56** (xₙ₊₁ = 2xₙ+4, drop hundreds; 2022nd) ·
  **2010 Q26✱ = 180** (words cycle first letter → LCM of lengths) · **2019 Q23✱ = 224** (octahedra, +9 each) ·
  **2019 Q26✱ = 110** (+20,−1,+19,−2,… peak) · **2021 Q26✱ = 666** (squares grow +3) · **2013 Q30✱ = 972**
  (bounded walk recurrence) · **2025 Q18 = 63** (triangular numbers) · **2025 Q20 = 900** (cycle sum).

**Two methods (2024 Q29).**
- **★ Method A — find the cycle, index by period (Year-6-fastest).** Iterate: 2024 → 24 → 20 → 4 → 16 → 37 →
  58 → 89 → 145 → 42 → **20** → … It re-enters 20, so from term 3 there is a cycle of length 8
  (20,4,16,37,58,89,145,42). Map 2024 onto the cycle by subtracting the pre-cycle length and taking the
  remainder mod 8 → lands on **89**.
- **Method B — iterate to 2024.** Compute term by term to the 2024th — only feasible *because* the cycle makes
  it finite; without spotting the cycle it is hopeless.

**The trap.** Not noticing it cycles (trying to grind out thousands of terms); an **off-by-one in indexing**
(where exactly the cycle starts, and whether the term count is 1- or 0-based).

**Twin recipe.** Define a deterministic `next()` (digit-square map, affine-with-mod, tiling/figurate growth),
ask for a far-out term or count, parameterise seed and index so the period stays in a Year-6-tractable range.

**How verify.py checks it.** Iterate `next()` with **cycle detection**, return the indexed term; confirm
uniqueness; difficulty proxy = cycle length and index magnitude; distractors = off-by-one period results and the
terms immediately before/after the answer.

---

## M7 — Geometry area / perimeter dissection (coordinate-computable)
**What it tests.** Area, perimeter, or volume by **decomposing / rearranging / subtracting**, or by place-and-
coordinate relations — frequently the official solution says it "can be done **without the area formula**". The
figure is exact, so it is **drawn by code from exact coordinates** (figure and answer can't disagree).

**Recognition trigger.** "What fraction is shaded?"; lattice/grid figures; nets; midpoints joined; dissections;
"area/perimeter of the shaded region".

**Real anchors.**
- ✷ **2024 Q23✱ = 21** — rectangle area 56; midpoints of BC and DC joined to A and to each other; area of the
  shaded triangle.
- **2013 UP Q12 = 32** — square, diagonal 8; area "without the area formula" (draw the other diagonal → four
  right triangles). · **2025 Q30✱ = 750** · **2013 Q10 = 1/4** (Sierpinski-style) · **2020 Q22✱ = 30**
  (4-rectangle perimeter invariant: opposite corners pair-sum equal) · **2020 Q24✱ = 16** (staircase dissection
  to a square) · **2018 Q21✱ = 1/2** (diagonal stripe; 180°-symmetry) · **2009 Q29✱ = 840** · **2012 Q14 = 20**
  (inscribed tilted square) · **2010 Q15 = 4⅙** (area in hexagonal units). *(38 anchors — the largest bank.)*

**Two methods (2024 Q23).**
- **★ Method A — fractions of the whole (Year-6-fastest, "no formula").** The shaded triangle = rectangle minus
  the three unshaded corner triangles. With X = mid BC and the midpoint of DC, each cut-off triangle is a clean
  fraction of the 56 (e.g. ½·½, ½·¼ …); summing the unshaded fractions and subtracting gives shaded =
  (7/?)·56 → **21**. No coordinates, just part-of-whole.
- **Method B — coordinates + shoelace.** Put A,B,C,D on axes, find the midpoints, apply the shoelace formula →
  **21**. (This is exactly how verify.py confirms the answer.)

**The trap.** Trusting the *not-to-scale* picture; double-counting an overlapping piece; reaching for a formula
when a dissection is faster (the setters specifically reward the no-formula route).

**Twin recipe.** Place the figure on an integer/rational coordinate grid; ask area / perimeter / fraction.
**M7 figures must be generated by code from the exact coordinates** so the drawn figure and the verified answer
are guaranteed consistent.

**How verify.py checks it.** Compute the area by shoelace (or perimeter by edge lengths) **from the exact
coordinates**, and confirm it equals the dissection answer; difficulty proxy = number of pieces / how non-obvious
the decomposition is; distractors = "read the scale off the diagram", "missed a piece", and the common
fraction-arithmetic slips.

---

## M8 — Logic / extreme-value / invariant
**What it tests.** Using an **invariant** (parity, shared-cell multiplicity, a conserved quantity), an
**extremal** argument, or pure **deduction** — instead of trial. The deepest tail mechanism.

**Recognition trigger.** "Largest/smallest possible…"; "which is **NOT** possible"; "which **must** be true";
line/graph puzzles where circles are shared between lines; handshakes/parity; something conserved; route or
tiling optimisation; pigeonhole ("guarantee").

**Real anchors.**
- ✷ **2025 Q25✱ = 17** (B) — place 1–9 in 9 circles so the four lines of three share one equal sum S; find the
  largest S. *(Shared-cell multiplicity invariant.)*
- **2024 Q25✱** (handshake/"met" parity) · **2021 Q29✱ = 17** (magic triangle, smallest side-total) ·
  **2021 Q27✱ = 72** (H-graph, equal line *products*) · **2022 Q25✱ = 19** (5-point star) · **2018 Q27✱ = 321**
  (cube opposite-face sums) · **2012 Q28✱ = 92** (cube opposite-face *products*) · **2020 Q25✱ = 2/3** (bottle —
  conserved air volume) · **2018 Q24✱ = 60** (route inspection, odd-vertex parity) · **2010 Q23✱ = 18 Nov**
  (median minimises total distance) · **2009 Q12 = 21** (pigeonhole) · **2013 Q24✱ = 3** (vertex sums).

**Two methods (2025 Q25).** Lines = {1,3,8}, {3,4,5}, {6,7,8}, {2,5,9}; three circles lie on two lines each.
- **★ Method A — the invariant (Year-6-fastest, once seen).** Add the four line-sums:
  4S = (1+…+9) + (the three shared circles counted an extra time) = **45 + (sum of the 3 shared circles).**
  4S must be a multiple of 4, so 45 + shared ≡ 0 (mod 4) ⇒ shared ≡ 3 (mod 4). The largest achievable shared
  sum that is ≡ 3 (mod 4) is **23** (e.g. 6+8+9) ⇒ 4S = 68 ⇒ **S = 17**, then show one valid filling exists.
- **Method B — guided trial.** Put the big numbers {9,8,7} on the shared circles and adjust — but you still need
  the divisibility insight to know shared = 24 (giving S = 17.25) is impossible.

**The trap (real anchor-keeping error).** **Answering the invariant instead of the question.** The shared-circle
sum is 23; the answer S is 17. CLAUDE.md's M8 anchor wrongly recorded "Q25 = E(23)" — it reported the invariant
(23), not S (17, option B). Always finish by converting the invariant back to the asked quantity, and check a
feasible witness exists.

**Twin recipe.** Numeric/graph forms — line/graph puzzles with shared cells, parity/handshake, conserved-quantity,
pigeonhole, route-inspection — are **generatable** (parameterise the graph/values). **CURATE** the novel-visual
ones (paper-folding, opposite-side 3-D views, gear rotations): these are the `answer:null`-flagged items in the
corpus and are taken from real papers, not faked.

**How verify.py checks it.** For numeric/graph twins: brute-search the configuration space to confirm the claimed
extreme **and exhibit a witness** assignment; difficulty proxy = how hidden the invariant is; distractors = the
invariant's own value (the "answered the wrong quantity" trap) and the naïve extreme that ignores feasibility.

---

### Cross-reference
- Mechanism → file that owns its correctness: `tutor/mechanisms/m{1..8}_*.py` (Phase 3, not yet written).
- Anchor provenance and page numbers: `content/questions.jsonl` + `content/reading-log.md`.
- The two CLAUDE.md anchor-value corrections surfaced during ingestion are recorded in `content/reading-log.md`
  (2025 Q25 → B/17; 2013 UP Q8 → C/7); both are the "answered the auxiliary value" traps named on the M8 and
  M4 cards above.
