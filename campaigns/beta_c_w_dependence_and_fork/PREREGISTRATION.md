# Pre-registration: `w`-dependence of β_c, and the two-arm fork test

**Repo:** `self_reference_shared_past`
**Depends on:** the growth-set objectivity campaign (verified predicate: unresolvable ⟺
`2S ≤ d + w` and `2S > d − w`; objectivity boundary at `w > d`; ω = w/d confirmed as the
governing coordinate, degree-tercile CV 0.157 vs 0.710).
**Status:** commit the repo, hash-lock this document, push it, *then* run. Not before.

---

## 0. Why these two runs

The growth-set campaign established that observers disagree about the growth set below
`w = d`. It could not test the consequences, because notebook 2's growth rule is
`frontier ∩ N(past)` — geometric, with `A_X` and `w` appearing nowhere. Trajectories were
bit-identical across `w ∈ {1,3,12,26,50}`.

Run A asks whether `w` — unreachable from outside in both notebooks, and therefore fixed at
one unexamined default for every published β_c — controls the phase transition.

Run B grafts notebook 1's resolution-driven growth into notebook 2's multi-observer setting,
which poses the fork question for the first time.

---

## 1. Instrument certification (blocking)

`w` is buried as a default argument of `conclusion()` and never forwarded by `required()`.
Plumb it through as an explicit parameter in both notebooks.

**C1.** Report the original default value of `w`, and the degree distribution of the toy
substrate (n0 = 60, generic geometric graph) and of the 137-registry. Report mean, median, max
for each. These set ω for every published result.

**C2 (bit-exactness).** At the original default `w`, the modified notebook 1 must reproduce
Table 1 of the paper bit-exactly — same seeds, same survival counts per β, same interpolated
β_c ≈ 1.08. Instruments are engines: if this fails, no data from the variant may be used.
Report the comparison row by row.

**C3.** Same bit-exactness check for the sterile-basin script against Table 3
(baseline β_c 0.906, σ pinned 0.915, contact 0.914).

---

## 2. Declared measures

- **β_c**: 50% crossing of `P_sustain(β)`, linear interpolation, same procedure as Table 1.
  Do not switch to a logistic fit midway; if you want one, report both and declare which is
  primary before running.
- **ω̄ = w / ⟨d⟩**, substrate mean degree. Report both `w` and `ω̄` on every row.
- **|A|**: incompleteness set size, read at **stage start, before that stage's expansion.**
- **Exhaustion**: `|A| = 0`, same definition as the paper.
- Seeds ≥ 32 per cell for Run A, ≥ 16 per cell for Run B. Fixed and recorded.

---

## 3. Run A — β × w sweep

Grid: `β ∈ {0.6, 0.7, ..., 1.6}` as in Table 1, crossed with `w ∈ {1, 2, 3, 5, 8, 12, 20, 30}`.
Toy substrate first, then the 137-registry.

**W1.** β_c decreases monotonically with `w`, then plateaus once `w > d_max`.
*Mechanism:* larger `w` widens the band `|d − 2S| ≤ w`, so more SR nodes are unresolvable per
stage, so more resolutions occur and more seeds are drawn — incompleteness is easier to
sustain. Above `d_max` every SR node is always unresolvable and `A` can only empty when the SR
set does, so the dependence should saturate.
*Pass:* β_c(w=1) − β_c(w=30) ≥ 0.15, monotone within seed noise.
*Fail:* β_c flat in `w` — the published values are `w`-independent and this run is a null.

**W2 (the discriminating test).** The toy/registry β_c gap (1.08 vs 0.906) is a degree effect,
not a substrate effect. Registry σ has degree 136; toy degrees are single-digit. At equal `w`,
ω̄ differs by more than an order of magnitude, so the two systems have never been compared at
matched ω̄.
*Procedure:* plot β_c against ω̄ for both substrates. To reach matched ω̄ the registry needs
`w` roughly `⟨d⟩_registry / ⟨d⟩_toy` times larger — compute the factor from C1 and extend the
registry grid accordingly.
*Pass:* the two curves collapse — β_c values agree within overlapping bootstrap CIs at matched
ω̄.
*Fail:* they do not collapse; the gap is a genuine substrate difference and the paper's
framing stands.

**W3 (boundary).** At `w` small enough that `A` is generically empty, all runs exhaust
regardless of β.
*Pass:* there exists a tested `w` with `P_sustain < 0.1` at β = 1.6.

**Disclosure trigger.** If W1 passes, β_c = 1.08 and 0.906 are properties of (substrate, `w`)
pairs, not of substrates. That qualifies published numbers in ai.viXra:2606.0082. Write the
disclosure note in the decision record at the time of the result, before any interpretation,
and do not fold it into a narrative about what `w` "really" means.

---

## 4. Run B — two-arm fork test

Graft notebook 1's resolution-driven growth rule into notebook 2's multi-observer engine, so
that expansion sites are determined by `A_X` rather than by `frontier ∩ N(past)`.

**Operating point.** Choose `w` by maximizing the mean per-stage symmetric difference
`|A_A △ A_B|` — not by minimizing concordance, which the prior campaign showed is dominated by
the trivially-resolvable majority (global min 0.9546 while Jaccard reached 0.0). Report the
selection curve. K = 2 observers, per §5 of the paper.

**Two arms, both implemented, neither privileged:**

- **Arm S (substrate-side).** One graph. Expand at `A_A ∪ A_B`. Both observers' absorbers are
  appended to the shared substrate; where they carry conflicting values, both land.
- **Arm O (observer-side).** Each observer expands on its own copy at its own `A_X`. Divergence
  is permitted.

**K1 (Arm S).** No fork is representable; disagreement appears as frustration instead.
*Measure:* count nodes receiving two absorbers with conflicting labels, per stage. *Pass:*
node sets identical across observers at every stage (guaranteed by construction — this is an
instrument check), and frustration count > 0 at the chosen `w`.

**K2 (Arm O).** Forks occur. *Measure:* node-set symmetric difference per stage. *Pass:*
divergence strictly positive by stage 5 and monotone non-decreasing, positively correlated
with `1 − J(A_A, A_B)`.

**K3 (fossil test).** In Arm O, does each fork retain the other observer's *frozen* structure
while losing its live edge? *Measure:* `|frozen_A ∩ frozen_B|` and `|live_A ∩ live_B|`
separately, per stage. *Prediction:* the frozen intersection stays large and stops growing at
the divergence point; the live intersection goes to zero. *Registered alternative:* if the
frozen intersection also decays, there is no fossil — the fork is total and the earlier
"shared trunk" reading is wrong.

**K4 (Remark 3).** §6's shared-past stability is architectural, not merely usual.
*Measure:* run Proposition 3's agreement statistic in both arms. *Prediction:* stability holds
in Arm S and degrades in Arm O, because Arm O has no single past to freeze against.
*This is the operational content of the substrate-vs-observer distinction.* Report it as a
comparison, not as a verdict on which reading is correct.

**K5 (control).** At `w > d_max`, the growth set is objective (0 discordant rows in 713,841),
so both arms must coincide exactly. *Pass:* Arm S and Arm O trajectories bit-identical at high
`w`. Failure indicates a bug in the graft, not a finding.

---

## 5. Deliverables

1. `certification.md` — C1 values, C2/C3 bit-exactness comparisons row by row.
2. `rows_runA.csv`, `rows_runB.csv` — long format, one row per (seed, stage, cell).
3. `beta_c_vs_w.png`, `beta_c_vs_omegabar_both_substrates.png`, `arm_divergence.png`.
4. `decision_record.md` — W1–W3 and K1–K5 each marked pass / fail / null with the deciding
   number, written before interpretation.
5. Disclosure note if the W1 trigger fires.

## 6. Traps

- **Certification is blocking.** If C2 fails, stop. A variant that cannot reproduce Table 1 is
  not the engine that produced Table 1.
- **Timing.** `|A|` at stage start, before expansion. Fourth instance of this error class in
  the program — assert the ordering in code, do not rely on reading order.
- **Selection statistic.** Use symmetric difference for the Run B operating point. Concordance
  is the wrong measure here and was already shown to be.
- **Do not privilege an arm.** Arm S and Arm O are declared alternatives. Reporting one as
  "the correct implementation" converts an experiment into an assumption.
- **`w` is not free.** Once Run A reports β_c(w), resist re-selecting `w` downstream to make
  other results land. If `w` gets chosen twice for two different reasons, it has become a
  fitted parameter and must be declared as one.
