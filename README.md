# AMC-buddy

A vertical AI maths tutor for **one** student — Frank, an Australian Year 6 student — preparing
for the **2026 Australian Mathematics Competition (AMC), Upper Primary division** (Years 5–6,
30 questions / 60 minutes / 135 marks).

Frank already earns a High Distinction (~top 3%). The goal is a **Prize** (~1 in 300), which is
decided almost entirely by the hard tail **Q21–30** — especially the integer-answer **Q26–30**.
Everything in this repo targets that tail and the *thinking* behind it.

> **This is a tutor, not a photocopier.** It explains what Frank gets wrong and generates *fresh,
> same-mechanism* practice to fix it. It never reproduces a real past question verbatim (the
> parent prints the real papers; a copy Frank can memorise is worthless).

---

## Core idea

1. **Real papers are the only difficulty ruler.** Every generated question is a *parameterised
   twin* of a **specific real anchor**, preserving that anchor's difficulty mechanism (M1–M8).
   Difficulty is never invented from a model's sense of "hard".
2. **Code judges, the model only proposes.** A proposer suggests parameters; **`verify.py` is the
   sole reviewer** — it confirms a *unique* answer **and** a difficulty proxy inside the
   real-paper band before any question is shown. (Building this repo is local coding; no API
   spend is required.)
3. **Everything traces to a real question** — `content/questions.jsonl` (with `source_file` +
   `page`) and the official Solutions.
4. **Two methods, crown the fastest.** For each hard question the tutor gives two methods, crowns
   the one a Year-6 can do fastest, and names the trap it avoids.
5. **Figures can't lie.** M7 geometry is drawn by code from *exact coordinates*; the answer is the
   shoelace area of the *same* coordinates, so figure and answer cannot disagree. True 3-D /
   spatial-insight items are **curated** from real papers, not faked.

---

## Requirements

- **Python 3.9+** (developed on 3.14). **Standard library only** — no third-party dependencies,
  no build step, no network access.

---

## Quick start

Run any tool as a module from the repo root. Each has a self-contained demo:

```bash
# Prove the solvers reproduce real AMC answers (57 official M1–M6 anchors)
python -m tutor.test_anchors

# The reviewer: unique-answer + difficulty-in-band gate (self-demo on a few anchors)
python -m tutor.verify

# Generate 5 verified twins of one mechanism (parameterised proposer -> verifier)
python -m tutor.generate

# Build a full tail mock: student paper + parent answer key (every item verifier-passed)
python -m tutor.mock

# Diagnose a completed paper: weak mechanism, broken step, grounded explanation, drills
python -m tutor.diagnose

# Render an M7 figure from exact coordinates (SVG + ASCII) and the curated M7/M8 set
python -m tutor.figures
```

There is no test-framework dependency: `tutor/test_anchors.py` is a self-checking script that
exits non-zero if any official anchor fails to reproduce.

---

## Repository layout

```
AMC--buddy/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md          # the pipeline map + trace table
│   └── AMC-KNOWLEDGE-BASE.md    # the 8 mechanism cards (trigger · 2 methods · trap · twin recipe)
├── content/
│   ├── questions.jsonl          # every real Upper Primary question, tagged + sourced (360 rows)
│   ├── reading-log.md           # what was read, when, with per-page index + findings
│   ├── profile.json             # per-mechanism mastery profile (written by diagnose.py)
│   └── figures/                 # generated M7 SVGs
└── tutor/
    ├── mechanisms/m1..m6_*.py   # per mechanism: solve(params) · generate(seed) · difficulty(params)
    ├── anchors.py               # REGISTRY: each official anchor -> (mechanism, params); FLAGGED set
    ├── verify.py                # THE REVIEWER: uniqueness + difficulty-in-band gate
    ├── generate.py              # propose a twin -> verify -> emit (never verbatim)
    ├── mock.py                  # full mock = student paper + parent key
    ├── diagnose.py              # working -> broken step -> grounded explanation -> drills
    ├── figures.py               # M7 geometry from exact coordinates + curated M7/M8 set
    └── test_anchors.py          # proof: official answers == solve(params)
```

Source PDFs (real AMC papers + official Solutions + the AP2 book) live **outside** the repo and
are **read-only** — they are never copied in.

---

## How it works (the pipeline)

```
REAL PAPERS (read-only PDFs)
      │  read + mechanism-tag every question
      ▼
content/questions.jsonl ───── the difficulty ruler + traceability anchor
      │
      ▼
docs/AMC-KNOWLEDGE-BASE.md ── one card per mechanism: trigger · 2 methods (★ fastest) · trap
      │
      ▼
tutor/mechanisms/mX.py ────── solve() generate() difficulty()  (code is the authority)
      │
      ▼
tutor/verify.py  ◀── THE REVIEWER: unique answer + difficulty in the real-paper band
      │
      ▼
tutor/generate.py ─────────── propose a parameterised twin of a specific anchor → gate → emit
      │
      ├──► tutor/mock.py       student paper + parent key (mechanism · answer · ★ method · trap)
      ├──► tutor/diagnose.py   broken step → grounded explanation → 3–5 verified drills
      └──► tutor/figures.py    M7 figures from exact coordinates · curated M7/M8 real-paper set
```

### The 8 discriminator mechanisms

Every Q16–30 is tagged with the mechanism that makes it hard:

| | Mechanism | Generatable? |
|---|---|---|
| **M1** | Place-value extreme value | yes (code-verified) |
| **M2** | Stacked-constraint number | yes |
| **M3** | Non-commutative operation ordering | yes |
| **M4** | Working backwards | yes |
| **M5** | Organised enumeration / modular bucketing | yes |
| **M6** | Sequence / pattern / recurrence | yes |
| **M7** | Geometry dissection (coordinate-computable) | via coordinate-drawn figures |
| **M8** | Logic / extreme-value / invariant | numeric/graph: yes · novel-visual: **curated** |

Full cards (recognition trigger, two methods with the ★ crowned fastest, the trap, the twin
recipe, and how `verify.py` checks each) are in `docs/AMC-KNOWLEDGE-BASE.md`.

### The verifier contract (`verify.py`)

A candidate `(mechanism, params, marks)` passes only if **both** hold:

- **Unique answer** — `solve(params)` returns a single well-defined value (and where a family
  could have multiple satisfiers, exactly one exists).
- **Difficulty in band** — `difficulty(params)` lies inside the band *learnt from the real
  anchors* for that mechanism + mark level (`learn_bands()`); difficulty is never invented.

Generation additionally guarantees a twin **never reproduces the anchor**: its parameters and its
answer must both differ from the real question's.

### Generatable vs curated

A family can be auto-generated only if it has a free parameter *independent of the difficulty
proxy* (e.g. `digit_extremes` varies the digit set while keeping the digit *count* that fixes the
band). Single-parameter families (stepping-stones, sparse-grid, …) would collapse onto the
anchor's own answer, so they are **curated, not generated** — see `figures.curated_worksheet()`,
which lists real M7/M8 questions by `source_file` + `page` + answer for Frank to drill on the
actual papers.

---

## The corpus

`content/questions.jsonl` — one JSON row per real Upper Primary question:

```json
{"year":2024,"q":26,"marks":6,"band":"Q26-30","mechanism":"M1","answer":"792",
 "answer_provenance":"official","source_file":"Upper Primary 2024-2025 Past Papers.pdf",
 "page":24,"stem_summary":"two 3-digit numbers from digits 1-6; max minus min of the sum",
 "note":"place-value bins"}
```

- **360 questions across 12 years**: 2009–2013 (AP2 book) + 2018–2025 (30 each).
- **240 official answers** (2009–2013 worked solutions; 2022/2024/2025 keys) + **120 computed**
  (2018–2021 have no published key — answers were solved in code and marked
  `answer_provenance:"computed"`, with every tail answer code-verified).
- **16 pure-visual/spatial items** carry `answer:null` with a "verify against figure" flag rather
  than a guess.

---

## Status (build phases)

The project is built in phases; each was completed and reviewed before the next.

- **Phase 1 — Data foundation** ✅ corpus (360 questions), `docs/ARCHITECTURE.md`,
  `docs/AMC-KNOWLEDGE-BASE.md`, `content/reading-log.md`.
- **Phase 2 — Solvers + verifier** ✅ `mechanisms/m1..m6`, `verify.py`. **Proven: 57/57**
  modellable official M1–M6 anchors reproduce the official answer (`python -m tutor.test_anchors`).
- **Phase 3 — Generation + mock** ✅ `generate.py`, `mock.py` (every emitted item verifier-gated
  and non-verbatim).
- **Phase 4 — Diagnosis** ✅ `diagnose.py` (broken step → grounded two-method explanation →
  verified drills → persisted profile).
- **Phase 5 — Figures + curated set** ✅ `figures.py` (coordinate-exact M7 SVGs + curated M7/M8
  real-paper worksheet).

### Notes and known limits

- **Two anchor-value corrections** were found while reading official solutions and are recorded in
  `content/reading-log.md`: **2025 Q25 → B (17)** (not 23, which is the shared-cell invariant) and
  **2013 UP Q8 → 7 (C)** (not 14, which is an intermediate of the reverse chain). Both are the
  "answered the auxiliary value" trap, now named on the M8 and M4 cards.
- **3 official anchors are deliberately flagged (not reproduced):** 2025 Q18 (figurate-dot rule
  unobtainable from an answer-key-only source — the natural reading gives the trap value 78), 2025
  Q29 (45×45 double spiral) and 2012 Q29 (free tri-rhomb shapes). They are listed transparently
  rather than faked.
- **Not yet built:** an M8 numeric/graph solver+generator, and a single `python -m tutor` entry
  point. M7/M8 are otherwise handled via figures + curation.

---

## Non-negotiable rules (for contributors / future sessions)

1. Real papers + official Solutions are the only difficulty ruler. Every twin is a parameterised
   copy of a specific real anchor, preserving its mechanism.
2. Every shown question passes `verify.py` first (unique answer + difficulty in band). No human
   review of individual generated questions — the verifier is the reviewer.
3. The model is only a proposer (twins) and explainer (solutions); code judges correctness and
   difficulty. Keep proposals small; never brute-force-generate-and-discard.
4. Everything is traceable to a row in `content/questions.jsonl` (with `source_file` + `page`) or
   the knowledge base. One responsibility per file (see the trace table in `docs/ARCHITECTURE.md`).
5. Never reproduce a real past question verbatim.
6. Figures are drawn from exact coordinates (figure and answer cannot disagree); novel-visual
   spatial items are curated from real papers, not faked.
7. All student-facing content is English.
