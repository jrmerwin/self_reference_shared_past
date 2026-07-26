# Decision Record — `w`-dependence of β_c, and the two-arm fork test

**Campaign halted at instrument certification. W1–W3 and K1–K5 are all NULL — NOT RUN.**

Pre-registration `PREREGISTRATION.md`, SHA-256
`99d0925394bf4ae4d8ec44ddd84fb4282fd69f48ac0fad74d4f966523a064e49`, hash-locked in commit
`ad565c4` and verified live on `origin/main` before the first run executed.

§6: *"Certification is blocking. If C2 fails, stop."* C2 failed. Full evidence in
[`certification.md`](certification.md).

---

## Certification

| gate | verdict | deciding number |
|---|---|---|
| **C1** | reported (not pass/fail) | `w` = 3; ⟨d⟩ toy 12.510, registry 78.058; ratio **6.239** |
| **C2** | **FAIL** | notebook gives P(β=1.0) = **0.25 (3/12)**, Table 1 reports **0.17 (2/12)**; likewise 0.83 vs 0.92 at β = 1.3 and 1.4 |
| **C3a** (Table 2) | **PASS** | all six rows exact, incl. final \|A\| = 498.1 / 497.3 / 488.8 / 492.5 |
| **C3b** (Table 3) | **FAIL** | baseline β_c: paper 0.906, measured 0.811 (as committed) / 0.997 (caption's 64 seeds) |

**The `w` plumbing itself certified clean**: per-seed outcome *sequences* — not just counts
— are identical between the original notebook and the plumbed variant at every one of the
11 β values. The instrument edit is correct. What fails is that the notebook it faithfully
copies does not reproduce the published table.

Environment ruled out: identical results under Python 3.12.4 / numpy 2.4.4 / networkx 3.4.2
and Python 3.11.7 / numpy 1.26.4 / networkx 3.1, with identical substrate fingerprints
(60 nodes, 416 edges, degree sum 832 at seed 0).

## Frozen predictions — all NULL

| | verdict | why |
|---|---|---|
| **W1** β_c decreases monotonically with `w`, plateaus above d_max | **NULL — not run** | blocked by C2 |
| **W2** toy/registry β_c gap collapses at matched ω̄ | **NULL — not run** | blocked by C2 |
| **W3** small-`w` boundary: `P_sustain < 0.1` at β = 1.6 | **NULL — not run** | blocked by C2 |
| **K1** Arm S frustration > 0 | **NULL — not run** | blocked by C2 |
| **K2** Arm O divergence positive by stage 5 | **NULL — not run** | blocked by C2 |
| **K3** fossil test | **NULL — not run** | blocked by C2 |
| **K4** Remark 3 stability, Arm S vs Arm O | **NULL — not run** | blocked by C2 |
| **K5** arms coincide at `w` > d_max | **NULL — not run** | blocked by C2 |

No `rows_runA.csv`, `rows_runB.csv`, `beta_c_vs_w.png`,
`beta_c_vs_omegabar_both_substrates.png` or `arm_divergence.png` exist. Deliverables 2 and 3
are absent by design, not by omission.

## Disclosure trigger — did NOT fire

§3's disclosure trigger is conditional on W1 passing. **W1 was not run, so the trigger did
not fire and no disclosure about β_c = 1.08 / 0.906 being `w`-dependent is made here.**
Whether those numbers are properties of (substrate, `w`) pairs remains untested.

What C1 *does* establish, without any sweep, is the setup for that question: both published
β_c values were produced at the single unexamined default `w` = 3, at ω̄ = 0.2398 (toy) and
ω̄ = 0.0384 (registry) — a factor of 6.24 apart. The two systems have never been compared at
matched ω̄. That remains the open question W2 was written to settle.

## One finding that stands independent of the halt

**C3a is a clean positive control.** The sterile-basin script reproduces Table 2 to the last
decimal across all six conditions, including the discriminating final-|A| spread
(498.1 / 497.3 / 488.8 / 492.5) that distinguishes σ from its matched control. The same
harness, same methodology and same session reproduced one published table exactly and failed
to reproduce two others. That asymmetry is why the C2 and C3b results are reported as real
discrepancies rather than as harness error.

The qualitative content of Table 3 also reproduces under both configurations tried:
baseline, pinned and contact conditions cluster tightly; the strong adjacent rule moves the
threshold sharply and **by the same amount for σ and its matched universal-S control**. The
paper's Proposition 2 — that σ is not singled out — is unaffected by the numerical
discrepancy in the crossings.

---
---

# What this means, and what it does not

*Written after the record above and separated from it.*

The campaign did not fail; it stopped where it was designed to stop, and the stop is the
result. C2 exists to answer one question before any sweep is allowed to qualify a published
number — is the committed notebook the engine that produced the committed table? — and the
answer is no, in three of eleven rows, deterministically, in two independent environments,
with no plausible configuration variant closing the gap. The discrepancy is small and moves
β_c only from 1.081 to 1.075, so nothing in the paper's argument turns on it; the phase
transition is real, the transition is sharp, and β_c sits just above the unit replacement
threshold either way. But the size of the gap is not what C2 tests. A `w`-sweep whose
purpose is to say "β_c = 1.08 is a property of `w`, not of the substrate" would have been
building that claim on a notebook that does not produce 1.08, and the claim would have
inherited the discrepancy silently. That is precisely the substitution the blocking clause
was written to prevent, and it caught it on the first campaign where it could have mattered.
The finding that the sterile script reproduces Table 2 exactly, in the same session, is what
converts this from "the harness is suspect" into "these two artifacts disagree" — a
certification that never passes anything is not evidence, and this one passed the table it
could. What is now open is a question of record, not of physics: which run produced Table 1,
and which produced Table 3. Once either is settled — by confirming the notebook's own
0.25 / 0.83 / 0.83 as correct, or by supplying the code state behind the published values —
Run A and Run B execute unchanged against a certified instrument, and the ω̄ = 0.2398 versus
0.0384 comparison that C1 has already set up can finally be made.
