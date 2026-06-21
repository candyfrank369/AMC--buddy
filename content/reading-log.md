# Reading log

What has been read from the source materials, when, and what came out of it.
Every claim about a real AMC question must trace back to a row here + the page in `content/questions.jsonl`.

Source root (READ-ONLY): `/Users/candywan/Documents/C & F/Frank study/数学/Math in 2026/2025～2026AMC/`

## Source files — FULLY READ (Upper Primary coverage)
- [x] **Upper Primary 2024-2025 Past Papers.pdf** — UP 2024 + UP 2025 papers + official key (read 2026-06-19)
- [x] **2022 AMC paper UP OMR.pdf** — UP 2022 paper (read 2026-06-19)
- [x] **2022 AMC Test papers and Solutions.pdf** — UP 2022 official answer key (read 2026-06-19; UP only)
- [x] **2021 AMC Upper Primary.pdf** — UP 2021 paper, answers computed (read 2026-06-19)
- [x] **2020 AMC UPrimary.pdf** — UP 2020 paper, answers computed (read 2026-06-19)
- [x] **2019 AMC UPrimary ONLINE.pdf** — UP 2019 paper, answers computed (read 2026-06-19)
- [x] **Upper Primary 2018_web.pdf** — UP 2018 paper, answers computed (read 2026-06-19)
- [x] **AP2 2020 online.pdf** — UP 2009–2013 papers + official worked solutions + Classification index (read 2026-06-19/20; UP sections only — Middle Primary out of scope)
- [ ] **2024 AMC solutions_ReadOnly.pdf** — NOT required for the corpus (2024 answers already from the official key); reserved as Phase-2 teaching material.

| Date | File | Pages | Division | What was extracted | Answer provenance |
|------|------|-------|----------|--------------------|-------------------|
| 2026-06-19 | Upper Primary 2024-2025 Past Papers.pdf | 1–12 | UP 2024 | All 30 questions → questions.jsonl (Q16–30 mechanism-tagged) | official (key p.25) |
| 2026-06-19 | Upper Primary 2024-2025 Past Papers.pdf | 13–25 | UP 2025 | All 30 questions → questions.jsonl (Q16–30 mechanism-tagged) | official (key p.25) |
| 2026-06-19 | 2022 AMC Test papers and Solutions.pdf | 74–75 | UP 2022 | Official answer key (all divisions) | official |
| 2026-06-19 | 2022 AMC paper UP OMR.pdf | 1–12 | UP 2022 | All 30 questions → questions.jsonl | official (key above) |
| 2026-06-19 | 2021 AMC Upper Primary.pdf | 1–12 | UP 2021 | All 30 questions; answers computed + code-verified (tail) | computed |
| 2026-06-19 | 2020 AMC UPrimary.pdf | 1–12 | UP 2020 | All 30 questions; answers computed + code-verified (tail) | computed |
| 2026-06-19 | 2019 AMC UPrimary ONLINE.pdf | 1–11 | UP 2019 | All 30 questions; answers computed + code-verified (tail) | computed |
| 2026-06-19 | Upper Primary 2018_web.pdf | 1–11 | UP 2018 | All 30 questions; answers computed + code-verified (tail) | computed |
| 2026-06-19 | AP2 2020 online.pdf | 159–164 | (index) | Classification of Questions (by AC strand) — cross-check for mechanism tags | n/a |
| 2026-06-19 | AP2 2020 online.pdf | 71–76 (book 62–67) | UP 2013 | All 30 questions → questions.jsonl | official |
| 2026-06-19 | AP2 2020 online.pdf | 149–156 (book 140–147) | UP 2013 | Official worked solutions → answers + teaching methods | official |
| 2026-06-20 | AP2 2020 online.pdf | 45–51 (book 36–42) | UP 2009 | All 30 questions → questions.jsonl | official |
| 2026-06-20 | AP2 2020 online.pdf | 117–124 (book 108–115) | UP 2009 | Official worked solutions → answers (all hand-computes matched) | official |
| 2026-06-20 | AP2 2020 online.pdf | 52–58 (book 43–49) | UP 2010 | All 30 questions → questions.jsonl | official |
| 2026-06-20 | AP2 2020 online.pdf | 125–134 (book 116–125) | UP 2010 | Official worked solutions → answers | official |
| 2026-06-20 | AP2 2020 online.pdf | 59–64 (book 50–55) | UP 2011 | All 30 questions → questions.jsonl | official |
| 2026-06-20 | AP2 2020 online.pdf | 135–141 (book 126–132) | UP 2011 | Official worked solutions → answers | official |
| 2026-06-20 | AP2 2020 online.pdf | 65–70 (book 56–61) | UP 2012 | All 30 questions → questions.jsonl | official |
| 2026-06-20 | AP2 2020 online.pdf | 142–148 (book 133–139) | UP 2012 | Official worked solutions → answers (Q21 corrected 9→11 by solution) | official |

## Page index (within "Upper Primary 2024-2025 Past Papers.pdf")
- **2024:** cover p.1 · Q1–5 p.2 · Q6–8 p.3 · Q9–11 p.4 · Q12–14 p.5 · Q15–17 p.6 · Q18–20 p.7 · Q21–23 p.8 · Q24–25 p.9 · Q26–27 p.10 · Q28–30 p.11 · answer-sheet p.12
- **2025:** cover p.13 · Q1–4 p.15 · Q5–8 p.16 · Q9–11 p.17 · Q12–14 p.18 · Q15–17 p.19 · Q18–20 p.20 · Q21–24 p.21 · Q25–27 p.22 · Q28–30 p.23 · answer-sheet p.24
- **Official Answer Key (2024 + 2025):** p.25

## Findings / discrepancies (CLAUDE.md anchor errors — both grab an auxiliary value instead of the answer)
1. **2025 Q25:** CLAUDE.md M8 anchor lists `E(23)`; official key (p.25) gives **B (17)**.
   Lines {1,3,8},{3,4,5},{6,7,8},{2,5,9}; three shared circles ⇒ `4S = 45 + (shared sum)`; largest shared
   sum ≡3 (mod 4) is 23 ⇒ S = 17. The "23" is the *shared-cell invariant*, not the answer.
2. **2013 UP Q8:** CLAUDE.md M4 anchor lists `=14`; official solution gives **7 (C)**.
   Reverse 6 → +2=8 → ×2=16 → −2=**14** → ÷2=**7**. The "14" is the *intermediate* step, not the answer.
→ Both anchors in CLAUDE.md should be corrected (value only; the mechanism/question references are fine).

Confirmed-correct anchors: 2024 Q26=792, 2025 Q26=576, 2024 Q27=270, 2024 Q23=21, 2024 Q29=89, 2024 Q30=41,
2021 Q30=117, 2013 UP Q5=41976 (M1), 2013 UP Q12 area=32 (M7), 2013 UP Q24=3 (M8), 2013 UP Q27=76 (M5).

## Teaching-language corroboration (CLAUDE.md "tail abilities")
- 2013 UP Q27 official solution: *"this argument is a modulo arithmetic argument but presented here in a way
  which will hopefully make it able to be understood by primary students"* — matches tail-ability #3 verbatim.
- 2013 UP Q12 / Q18 solutions explicitly give "without the area formula" / "can be done without calculations"
  least-machinery methods — matches tail-ability #2.

## Corpus COMPLETE — all 12 available UP papers ingested
2009, 2010, 2011, 2012, 2013, 2018, 2019, 2020, 2021, 2022, 2024, 2025 (30 each = 360 rows).
- **Official** answers: 2009–2013 (AP2 worked solutions) + 2022, 2024, 2025 (printed keys) = 240 rows.
- **Computed** + code-verified: 2018–2021 (no official key published) = 120 rows.
- For 2009–2013, every hand-computed answer was cross-checked against the official worked solution and matched
  (the one correction: 2012 Q21, 9→11, made before recording).

## Not needed for the corpus
- 2024 AMC solutions_ReadOnly.pdf (88 pp) — official multi-method solutions for 2024; **teaching material for the
  knowledge base (Phase 2)**, not needed for the corpus (2024 answers already captured from the official key).
- AP2 Middle Primary papers/solutions — out of scope (Upper Primary only).
