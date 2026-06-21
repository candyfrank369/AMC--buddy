# Architecture — AMC-buddy

A vertical AI tutor for one student (Frank, Year 6) targeting the hard tail (Q21–30, esp. integer
Q26–30) of the 2026 AMC Upper Primary paper. The product **explains mistakes** and **generates fresh
same-mechanism practice** — it never reproduces a real past question. `CLAUDE.md` is the source of truth;
this file is the map.

## Pipeline (data → reviewer → student)

```
  REAL PAPERS (read-only PDFs)
        │  read + tag (LLM proposes tag, human-verifiable against official solutions)
        ▼
  content/questions.jsonl ───────── every real UP question: mechanism (M1–M8), official/computed answer,
        │                            source_file + page  (the difficulty ruler + traceability anchor)
        │
        ▼
  docs/AMC-KNOWLEDGE-BASE.md ─────── one card per mechanism M1–M8: trigger · 2 methods (★ fastest) ·
        │                            the trap · twin recipe · how verify.py checks it
        ▼
  tutor/mechanisms/mX_*.py ───────── per mechanism: solve() generate() difficulty()
        │                            (code is the authority on correctness AND difficulty)
        ▼
  tutor/verify.py  ◀── THE REVIEWER: unique-answer check + difficulty-proxy-in-band gate +
        │              distractors must be NAMED typical mistakes.  Fail → discard & re-propose.
        ▼
  tutor/generate.py ─────────────── LLM proposes a parameterised twin of a SPECIFIC anchor →
        │                            verify.py gates it → emit.  figures.py draws M7 from exact coords.
        ▼
  tutor/mock.py  (student paper + parent key)      tutor/diagnose.py  (Frank's working → broken step → drills)
```

Roles: **LLM = proposer + explainer only.** **Code = judge** of correctness and difficulty. No human review
of individual generated questions — `verify.py` is the reviewer.

## Trace table (symptom → the one file that owns it)
| Symptom | Owner file |
|---------|-----------|
| generated question too easy / no unique answer | `tutor/verify.py` + that `tutor/mechanisms/mX_*.py` |
| wrong answer key | the `solve()` in `tutor/mechanisms/mX_*.py` |
| figure doesn't match its question | `tutor/figures.py` |
| diagnosis blames the wrong topic | `tutor/diagnose.py` + the tag in `content/questions.jsonl` |
| teaching method wrong / too advanced | the card in `docs/AMC-KNOWLEDGE-BASE.md` |
| a claim about a real question can't be sourced | `content/reading-log.md` + the row's `page` |

## The 8 discriminator mechanisms (full cards live in docs/AMC-KNOWLEDGE-BASE.md)
M1 place-value extreme · M2 stacked-constraint number · M3 non-commutative op ordering ·
M4 working backwards · M5 organised enumeration / modular bucketing · M6 sequence/pattern/recurrence ·
M7 geometry dissection (coordinate-computable) · M8 logic / extreme-value / invariant.
Generatability: M1–M6 fully code-verifiable; M7 via coordinate-drawn figures; M8 generate numeric/graph ones, CURATE novel-visual ones.

## Corpus status (content/questions.jsonl) — COMPLETE
360 real UP questions across all 12 available years: 2009, 2010, 2011, 2012, 2013, 2018, 2019, 2020, 2021,
2022, 2024, 2025 (30 each).
Provenance: 240 official (2009–2013 AP2 worked solutions + 2022/2024/2025 keys), 120 computed+code-verified (2018–2021).
16 pure-visual/spatial items carry `answer:null` with a verify-against-figure flag (not guessed).
Mechanism tags (all bands): M7 ×38, M5 ×37, M8 ×34, M2 ×19, M6 ×13, M4 ×8, M1 ×3, M3 ×1.
(Routine arithmetic / non-discriminator mid questions are intentionally left untagged — see notes in the rows.)

## Build phases (stop + report after each)
1. **Data foundation** — persist the corpus + reading log + this map. *(COMPLETE: all 12 UP papers, 360 questions.)*
2. **Knowledge base** — the 8 mechanism cards.
3. **Mechanism engines + reviewer** — `mechanisms/m1..m8`, `verify.py`.
4. **Generation + figures** — `generate.py`, `figures.py`.
5. **Student tools** — `mock.py`, `diagnose.py`.

## CLI surface (planned)
`python -m tutor.mock` · `python -m tutor.generate` · `python -m tutor.diagnose`. MCP/web wrapper later.
