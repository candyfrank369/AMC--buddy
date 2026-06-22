# AMC Learning Buddy — Agent Architecture (v1, governing document)

This file governs the project. Every change answers to it.

## 1. Product definition
This is **not** a general maths question generator. It is a **tail-question tutor** for the
Australian Mathematics Competition, Upper Primary. Target student: **Frank** (Year 6, stable
High Distinction, now aiming for **Prize**).

Core goal — NOT volume:
> Use **real AMC tail questions** to diagnose Frank's transferable weaknesses, then train the
> **confirmed** weak skills with high quality.

Priority order: (1) diagnose Q21–30 fine-skill gaps; (2) explain the fastest method, hidden
transformation and real traps of *real* AMC questions; (3) re-confirm a weakness with real /
curated questions; (4) generate mechanism-equivalent practice **only within what code can
verify**. Generating many questions is never the main goal.

## 2. Non-negotiables
1. Real AMC questions are the **only** difficulty yardstick.
2. Code verifies the computable; it must **not** pretend to verify insight quality.
3. Model judgements must output **structured evidence**, never "this is hard / AMC style".
4. No reproducing a real stem verbatim — but "changed the numbers" is not a quality twin.
5. M7/M8 (geometry, spatial, 3D, invariant): short term = real-question explanation + curated
   drill. Do not force auto-generation.
6. **Diagnosis precedes generation.** With no real student data, do not mass-generate.
7. Goal = transferable methods, not memorised templates.

## 3. Division of labour
**Code judges (measurable):** answer uniqueness, enumeration/calculation correctness,
constraint satisfaction, difference from anchor params, brute-force search-space size, case
count, recurrence/cycle correctness, coordinate-geometry area consistency, whether each
distractor equals a *computable* mistake.

**Code must NOT judge:** real hidden insight, Prize-level cognitive pressure, naturalness of the
shortest solution, trap realism, template-obviousness, AMC-style disguise, elegance of a
primary-level geometry solution.

**Model judges (reasoning) — and must emit structured evidence:**
```
{ "core_insight": "...", "anchor_pressure": "...", "new_item_pressure": "...",
  "fast_solution": "...", "brute_force_problem": "...", "trap": "...",
  "verdict": "pass|fail", "reason": "...", "evidence_anchor": "YYYY Qn" }
```
Banned output: "This is hard / This is AMC style / Difficulty is similar."

## 4. Question-bank schema
Coarse M1–M8 is only a tag; diagnosis and training use `fine_skills`. Each real question:
```
{ "year","question","marks","band","coarse_mechanism","fine_skills":[...],
  "core_insight","fast_method","alternate_method","common_traps":[...],
  "requires_diagram":bool,"has_hidden_invariant":bool,
  "generation_policy":"curated_only|code_generatable|model_review_required",
  "difficulty":{ "code_measured":{...}, "model_judged":{...} },
  "source_file","page" }
```

## 5. Difficulty vector (never a single number)
`code_measured`: search_space, case_count, cycle_length, min_steps_lower_bound,
brute_force_feasible, answer_unique.
`model_judged`: hidden_transformation, elegant_solution_exists, trap_quality, template_risk,
frank_level.
Pass = all code-measured pass + all model-judged carry evidence + cognitive pressure near the
anchor + not below Frank's current level.

## 6. Diagnosis flow
**Stage 1 uses REAL questions, never generated.** Input per question: answer, time, confidence,
and the student's working. Output: `weak_skills` (skill, evidence, error_type, severity,
next_action), `not_enough_evidence`, `do_not_generate_yet`.
Error types: concept, strategy, case_split, computation, reading, time_pressure,
diagram_interpretation, off_by_one, over_bruteforce, missed_invariant.

## 7. Re-diagnosis
Never label after one error. A wrong fine-skill must be re-confirmed with 2–3 real/curated
questions before it enters training:
`real diagnosis -> curated re-confirm -> confirmed weakness -> targeted training`.

## 8. Generation strategy (three kinds; each needs a `student_reason`)
1. **Foundation drill** — same sub-skill, slightly easier; repairs a concept/method.
2. **Prize-level twin** — preserves the anchor's core insight, case pressure, trap, time
   pressure.
3. **Disguised transfer** — different surface, same underlying fine-skill (anti-template).
No `student_reason` → no generation. Every generated item stores anchor, target_skill,
generation_type, student_reason, problem, answer, fast_solution, trap, code_verification,
model_review.

## 9. M7/M8 (three layers)
- **Layer 1 (real-question explanation):** 3D nets, folding, cube rotation, spatial views,
  complex visual invariants, non-coordinate geometry. Do not generate; explain real ones with
  multiple methods, mark the visual transformation and trap.
- **Layer 2 (verifiable generation):** coordinate area, lattice counting, simple polygon area,
  simple grid invariant — figure drawn by code, answer from the same coordinates, model checks
  for a Year-6-friendly solution.
- **Layer 3 (sub-skill drills):** shared-node invariant, visual parity, net reconstruction, area
  decomposition, symmetry — short drills only, never posing as a full Q30.

## 10. Weekly loop
real/curated Q26–30 mini-mock → record answers/time/confidence/working → update fine-skill
profile → 3–5 targeted drills on confirmed weaknesses → re-test with a disguised transfer →
weekly report (accuracy, time_profile, improved_skills, persistent_weaknesses, next_week_focus).

## 11. Prohibited
Judging difficulty by marks alone; "changed numbers" twins; treating unique-answer as quality;
mass generation without student data; auto-generating complex M7/M8 and pretending it is
reliable; training Prize with below-level questions; "AMC style" hand-waving; letting the model
free-compose a whole paper without anchor alignment and dual verification.

## 12. Success criteria
Not "can generate 1000 questions." Success = (1) pinpoint *why* Frank erred; (2) map the error
to a fine-skill; (3) state the fastest method of real tail questions; (4) decide which questions
must be real vs may be generated; (5) raise Frank's Q26–30 accuracy *and* speed; (6) never let a
shallow question masquerade as hard.

**One line:** diagnose before generate; real before twin; code verifies correctness, model
verifies insight; handle M7/M8 conservatively; train transferable methods, not a question flood.

---

## Addenda (peer review additions to v1)
**A. Diagnosis input is the real bottleneck.** Frank's working is on paper. Capture per
question = answer + **photo of scratch work** + time + confidence (1–5); the model reads the
photo (vision) to locate the step where the method broke. Diagnosis quality is capped by this.

**B. Frank's own results are the final difficulty calibrator.** `model_judged` difficulty is the
weakest link (the model mistakes a known chestnut for a hard problem). Close the loop: if Frank
solves a "Prize twin" instantly, the label was wrong — feed his measured accuracy/time back to
recalibrate difficulty labels. The student is the ground-truth difficulty sensor.

**C. Every model insight judgement must cite the anchor's official solution** (`evidence_anchor`
+ the published method) rather than free assertion. Treat `template_risk` as **low-confidence**
— reliably detecting "this is a known chestnut" needs a corpus comparison the model cannot do
perfectly.

**D. Distractors are derived, not invented.** Each multiple-choice distractor = the value
produced by a **named** common mistake/trap, computed by code. No "round number" filler options.

**E. Build order / honesty.** The foundation is tagging the real Q21–30 corpus (2009–2024 +
AP2) into this schema — a few hundred questions, read by the model, not a script. It ships by
milestone, not overnight. `frank_level` stays `unknown_until_diagnosed` until Stage-1 diagnosis
exists.
