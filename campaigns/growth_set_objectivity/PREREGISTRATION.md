# Pre-registration: Objectivity of the Growth Set as a Function of Self-Weight

**Repo:** `self_reference_shared_past`
**Base:** notebook 2 (multi-observer shared-history dynamics, §6 of the paper)
**Status:** freeze and hash-lock this document before executing any run.

> **Provenance note, added at repository creation (2026-07-25), not part of the
> pre-registration.** This document is transcribed verbatim as issued. It was issued in
> full before any run and governed the campaign throughout — every threshold, measure and
> pass/fail rule below was fixed in advance and none was altered afterwards. However, the
> document existed only in the issuing conversation at the time and was **not** itself
> written to a file and hash-locked before execution, as its own Status line requires. That
> is a real gap in the chain of custody and is stated rather than concealed. Its SHA-256 is
> recorded in `MANIFEST.sha256` as of this commit. Deviations from the runs specified in §5
> are recorded in `decision_record.md`, not here.

---

## 0. What this tests, and what it does not

The paper treats the incompleteness set `A` as observer-independent. It is not, in general.
Resolvability depends on the neighbor label sum `S`, and `S` is private wherever the
neighborhood is unfrozen. This campaign measures **when the growth set is objective and when
it is private**, as a function of the self-weight `w`, the node degree `d`, and the frozen
fraction of the neighborhood.

**In scope:** whether two observers with different initial labels identify the same
unresolvable nodes, and therefore expand at the same sites.

**Out of scope:** anything requiring localized/endogenous observers. The paper's observer is
a global labeling `ℓ: V → {0,1}`, not a subgraph. Claims about "A's model of B" require a
different construction and are explicitly deferred. Do not extend the observer model in this
campaign.

---

## 1. The analytic condition to be verified (not assumed)

For `v ∈ S` with degree `d`, neighbor label sum `S = Σ_{u~v} ℓ(u)`, and self-weight `w`, the
evidence multiset has size `d + w` and sum `S + w·a` where `a = ℓ(v)`.

A fixed-point-free 2-cycle (Lemma 1) requires `c(v)|_{a=0} = 0` and `c(v)|_{a=1} = 1`, giving

```
2S < d + w        and        2S ≥ d − w
```

i.e. approximately `|d − 2S| ≤ w`, with the boundary cases set by the rounding convention.

Two consequences to be checked, not presumed:

- Since `0 ≤ S ≤ d`, we always have `|d − 2S| ≤ d`. So **`w ≥ d` forces unresolvability
  regardless of neighbors** — the objective regime.
- For `w < d` the condition depends on `S`, hence on neighbor labels, hence on the observer.

**The natural per-node coordinate is `ω(v) = w / d(v)`, not `w`.** Degrees are heterogeneous;
pooling over degrees will smear the transition.

---

## 2. Preflight (mandatory, blocking)

Do these before any sweep. If any fails, stop and report rather than proceeding.

**P0.1 — Read, do not reimplement.** Locate the existing resolvability test in the repo. Use
it as-is. Report the exact rounding convention it uses (Python `round` and `numpy.round` are
both banker's rounding — half-to-even — which is *not* half-up and will move the boundary
cases). Do not substitute your own rounding.

**P0.2 — Brute-force validation of the band.** Over a grid of `d ∈ [3, 20]`, `S ∈ [0, d]`,
`w ∈ [1, 25]`, construct a node with that exact configuration, call the repo's resolvability
function, and compare against the analytic condition in §1. Report the exact set of
disagreements. If disagreements are not confined to the rounding-tie boundary, **the analytic
condition is wrong and this entire campaign is void — stop and report.**

**P0.3 — Frozen-neighborhood identity (instrument check).** For any node all of whose
neighbors are frozen, `S` is common to both observers, so both must return identical
resolvability. Construct such nodes explicitly and assert concordance = 1.000 for both
observers at every `w` tested. This is a bookkeeping identity, not a result. If it fails
anywhere, there is a bug in the freeze bookkeeping — stop and report.

---

## 3. Declared measures

Timing is declared explicitly, because the prior campaign lost a prediction to exactly this
error class (the valve transfer function logged population at epoch end rather than at
trigger).

- **Incompleteness set** `A_X` for observer `X`: read at **stage start, before any expansion
  move of that stage is applied.** Never post-expansion.
- **Frozen fraction** `φ(v)`: fraction of `v`'s neighbors that are frozen, evaluated at the
  same instant as `A_X`, on the same graph.
- **Degree** `d(v)`: live degree at that instant, not birth degree.
- **`ω(v) = w / d(v)`**, computed per node.
- **Set agreement:** Jaccard `J = |A_A ∩ A_B| / |A_A ∪ A_B|`, over self-referential nodes only.
- **Per-node concordance:** fraction of self-referential nodes on which A and B return the
  same resolvability verdict. Report alongside Jaccard; they differ when sets are imbalanced.

Every reported statistic must carry its measure and timing in the column name.

---

## 4. Frozen predictions

State pass/fail before running. Record failures with the same prominence as passes.

**F1 (primary).** Per-node concordance → 1.0 for `ω(v) ≥ 1` and degrades below it.
*Pass:* concordance ≥ 0.98 in the bin `ω ∈ [1.0, 1.5]`, and ≤ 0.80 in the bin `ω ∈ [0, 0.4]`
restricted to `φ(v) < 0.25`.
*Fail:* concordance flat in `ω` (mechanism is not the band condition — my analysis is wrong).

**F2 (sharpness).** The transition is sharp in `ω` and smeared in `w`. Fit a logistic to
concordance vs `ω` and vs `w` separately. *Pass:* the `ω` fit has a steeper normalized slope
and lower residual than the `w` fit. This is the discriminating test that degree
normalization is the right coordinate.

**F3 (control).** Concordance = 1.000 at `φ(v) = 1.0` for all `ω`. Same identity as P0.3,
re-measured in-sweep. Any deviation is a bug, not a finding.

**F4 (recovery).** The paper's §6 frontier agreement (≈0.44, chance) should be recovered as
the low-`φ`, low-`ω` corner of the surface. *Pass:* the cell `φ < 0.25, ω < 0.4` yields
label agreement within ±0.10 of 0.44 under the paper's original `w`. If the paper's original
`w` puts it in the objective regime (`ω ≥ 1`), report that — it means the 0.44 has a
different cause than the band condition, which is itself informative.

**F5 (divergence).** Where `A_A ≠ A_B`, the two observers expand at different sites and the
substrates diverge. Measure, per stage: node-set symmetric difference, and whether the
frozen trunk stays common. *Pass:* divergence is monotone non-decreasing in stage and
positively correlated with `1 − J`. *Registered possibility:* divergence may be zero if the
notebook applies expansion to a single shared graph — if so, **report that as a finding**,
because it means the implementation already encodes the substrate-side reading and forking is
not representable without a rewrite.

---

## 5. Runs

Fixed across all runs unless stated: `β = 1.3` (super-critical in the toy), two observers with
independent random initial labels on a common seed graph, `n0 = 60`, generic geometric-graph
substrate as in Table 1 of the paper.

**R1 — `w` sweep.** `w ∈ {1, 2, 3, ..., 2·d_max}`, ≥ 32 seeds per `w`. Record per-node rows:
`seed, stage, node_id, d, w, omega, phi, resolvable_A, resolvable_B, frozen`. Long format, one
row per self-referential node per stage. Aggregate afterwards; do not aggregate in the loop.

**R2 — surface.** From R1 rows, bin on `(ω, φ)` and report concordance per cell with cell
counts. Do not report cells with n < 30.

**R3 — degree binning.** From R1 rows, split by `d` into at least three bins and re-fit F2
within each. The `ω` collapse should hold within every degree bin; the `w` curve should shift
between bins. This is the strongest single test of the mechanism.

**R4 — divergence.** Run ≥ 16 seeds for ≥ 20 stages at a `w` chosen from R1 in the degraded
regime (concordance ≈ 0.6), tracking substrate divergence per F5.

Seeds fixed and recorded. All runs deterministic and resumable.

---

## 6. Deliverables

1. `preflight_report.md` — P0.1 convention, P0.2 disagreement set, P0.3 assertion result.
2. `rows_R1.csv` — the long-format per-node table. This is the primary artifact.
3. `concordance_vs_omega.png`, `concordance_vs_w.png`, `surface_omega_phi.png`.
4. `decision_record.md` — each of F1–F5 marked pass / fail / null, with the number that
   decided it, written **before** any interpretation.
5. A one-paragraph statement of what the result implies for the substrate-side vs
   observer-side reading, written last and clearly separated from the decision record.

---

## 7. Known traps

- **Timing.** Reading `A_X` after expansion inverts the result. Assert the ordering in code.
- **Measure switching.** `w` vs `ω`, Jaccard vs concordance, node-count vs
  self-referential-node-count. Fix each in this document and never switch mid-analysis.
- **Degree pooling.** Reporting concordance vs `w` pooled over degrees will show a smooth
  ramp that looks like a weak effect. That ramp is an artifact of mixing thresholds.
- **The `φ = 1` control is not a result.** It is guaranteed by construction. If it is quoted
  as evidence for anything, the write-up has drifted.
- **Do not extend the observer model.** If the analysis seems to require observers with
  extent, stop — that is the deferred paper, not this run.
