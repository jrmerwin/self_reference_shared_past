# Decision Record — Objectivity of the Growth Set

Adjudication of the frozen predictions F1–F5 against `rows_R1.csv` (834,850 rows;
32 seeds × 50 self-weights × 14 stages), `summary_R1.csv` (22,400 stage-rows),
`rows_R4_w6.csv`, `rows_R4_w2.csv`. Raw values in `decision_results.json`.

Verdicts are recorded against the predictions **exactly as written in §4**. Where a
prediction's threshold and the mechanism it was testing come apart, both are stated —
the verdict follows the written threshold, not the intent. Interpretation is deferred
to the separate section at the end, per §6.5.

Measures are as fixed in §3 and were not switched: concordance = per-node agreement of
the two observers' resolvability verdicts over **self-referential nodes only**, read at
**stage start, before any expansion move of that stage**; `ω = w/d(v)` with live degree;
`φ` = frozen fraction of the neighbourhood at the same instant.

---

## F1 (primary) — **FAIL** (conjunction), clause A pass / clause B fail

| clause | measured | target | verdict |
|---|---|---|---|
| A: concordance in `ω ∈ [1.0, 1.5]` | **0.9857** (n = 72,878) | ≥ 0.98 | **PASS** |
| B: concordance in `ω ∈ [0, 0.4]`, `φ < 0.25` | **0.9506** (n = 22,773) | ≤ 0.80 | **FAIL** |

**The number that decided it: 0.9506 against a 0.80 ceiling.**

Two facts recorded alongside, both from the same rows:

- Concordance for **`ω > 1.0` is exactly 1.000000 across 713,841 rows** — zero
  discordant rows, not a rounded 1.0. At **`ω = 1.0` exactly** it is **0.9377**
  (n = 16,683). The gap is the P0.2 escape: at `w = d` with `S = 0` the lower tie is
  not strictly exceeded and the node is resolvable. Clause A's shortfall from 1.0
  (0.9857) is entirely this boundary, which its bin `[1.0, 1.5]` includes.
- Concordance is **not flat in ω** — it runs 0.979 → 0.934 → **1.000** with a step at
  `ω = 1`. The pre-registered *Fail* diagnosis in §4 ("concordance flat in ω —
  mechanism is not the band condition — my analysis is wrong") therefore **does not
  apply**. F1 fails on threshold calibration, not on mechanism.

Why clause B's threshold was unreachable, as a measurement fact: at low `ω` the band
`2S ∈ (d−w, d+w]` is narrow, so `|A|` is nearly empty and the two observers agree
*trivially* by both answering "resolvable". In the clause-B cell the incompleteness
density is `|A_A|/n = 0.0410`, `|A_B|/n = 0.0353`, and the **pooled Jaccard is 0.2145**.
Concordance 0.95 and Jaccard 0.21 describe the same rows. This is the §7
measure-switching trap, anticipated in preflight B2 and recorded before the sweep ran.

## F2 (sharpness) — **FAIL** (conjunction), slope clause pass / residual clause fail

4-parameter logistic `p(x) = lo + (hi−lo)/(1+exp(−k(x−x₀)))`; normalized slope
`≡ k·σ(x)`; residual = RMSE against bin means with n ≥ 30. Both fits use identical rows,
differing only in the x-coordinate.

| coordinate | k | σ(x) | **normalized slope** | x₀ | **RMSE** | R² |
|---|---|---|---|---|---|---|
| **ω** | 162.55 | 7.015 | **1140.23** | 1.036 | 0.00886 | 0.846 |
| **w** | 0.356 | 14.431 | **5.13** | 12.92 | **0.00313** | 0.927 |

- steeper normalized slope in ω: **PASS** — 1140.23 vs 5.13, a factor of **222**.
- lower residual in ω: **FAIL** — 0.00886 vs 0.00313.

**The number that decided it: RMSE 0.00886 (ω) > 0.00313 (w).**

Recorded mechanically: the residual clause inverts because the pooled `w` curve is
nearly *flat* (fitted `k = 0.356`, amplitude ≈ 0.03), and a flat curve is fitted with
small RMSE by a near-flat logistic. Low residual here indicates absence of a transition,
not a better-located one. The fitted ω midpoint `x₀ = 1.036` sits on the analytic
threshold `ω = 1`; the fitted w midpoint `x₀ = 12.92` sits at no privileged value. The ω
curve's residual is inflated by the sub-threshold dip (upward-variation fraction 0.593
vs 0.868 for w), i.e. by genuine non-monotone structure the logistic cannot represent.

## F3 (control) — **NULL — not measurable in-sweep**

**No row in 834,850 has `φ = 1.0`.** The neighbourhood freeze fraction is **capped at
`φ_max = 0.500`** in this substrate: every absorbed node is simultaneously given a fresh
unfrozen absorber neighbour, so a node's neighbourhood cannot become fully frozen under
notebook 2's expansion rule.

Closest achievable: `φ ≥ 0.500` → concordance **0.997582** (n = 19,850).

The identity itself was established constructively in **P0.3: concordance 1.0000 over
5625 `(d, S, w)` configurations, 0 failures**. Per §7 this is a bookkeeping identity and
is not quoted as evidence for anything.

## F4 (recovery) — **FAIL** as written; **the §4 conditional fires**

| quantity | value |
|---|---|
| cell `φ<0.25, ω<0.4` at `w=3`, frontier nodes only | **0.6899** (n = 1,819) |
| target | 0.44 ± 0.10 |
| same cell, all self-referential nodes | 0.8565 (n = 4,014) |
| nb2-style stagewise `agree_frontier` at `w=3` | 0.5651 |

**The number that decided it: 0.6899 against a 0.34–0.54 window.**

Two controls were run to determine whether this is a campaign effect or a definitional
one. Both used **notebook 2's original, unmodified code exec'd straight from the
`.ipynb`**, on its original substrate (n=50, radius 0.32, w=3), 24 trials:

| K | mean `agree_frontier` |
|---|---|
| **4** (notebook 2's published setting) | **0.4020** |
| 3 | 0.5202 |
| **2** (mandated by pre-registration §5) | **0.6751** |

`agree_on` scores a node only when **all** observers carry the same label, so the
statistic is mechanically K-dependent. The paper's ≈0.44 is a **K = 4** number
(notebook 2's own stored output records 0.435); §5 of this pre-registration fixes **two**
observers. At matched K = 2 the original code yields 0.6751, and this campaign measured
**0.6899** in the corresponding cell — agreement to 0.015. The target was therefore
unreachable at the mandated K, and the campaign reproduces the paper's dynamics once K
is matched.

**The §4 conditional — "If the paper's original `w` puts it in the objective regime
(ω ≥ 1), report that" — fires, but only under the mandated β-branching:**

- On the original substrate alone (stage 0, before any spawning), `w=3` gives median
  `ω = 0.25` — firmly below the band, the private regime.
- Across the full campaign population, `w=3` gives median `ω = 1.0000` with **59.9% of
  node-stage rows at `ω ≥ 1`**, because β = 1.3 branching (`[MOD-2]`, mandated by §5)
  makes **39.6% of all rows degree ≤ 2** spawned children, for which `ω = 3/d ≥ 1`.
- Notebook 2's published §6 run has **no** branching and never grows its
  self-referential set, so its frontier nodes are original-substrate nodes with d ≈ 16,
  i.e. `ω ≈ 0.19`. **The paper's 0.44 is a genuine low-ω, private-regime number.**

## F5 (divergence) — **NULL for the prediction; the §4 registered possibility is CONFIRMED**

The prediction ("divergence monotone non-decreasing in stage and positively correlated
with 1−J") **cannot be evaluated**: divergence is identically zero, so the correlation is
undefined (zero variance).

| measure | R1 (22,400 stage-rows) | R4 w=6 (320) | R4 w=2 (320) |
|---|---|---|---|
| max `symdiff_nodes_AB` | **0** | **0** | **0** |
| `trunk_common` always true | **yes** | **yes** | **yes** |
| observers share one graph object | — | **always** | **always** |
| stage-rows where `A_A ≠ A_B` | **2,489** (11.1%) | 79 (24.7%) | **140 (43.8%)** |
| mean `|A_A △ A_B|` when non-zero | — | 3.25 | 3.18 |
| minimum Jaccard observed | **0.0** | — | — |

**The numbers that decided it: 140/320 stage-rows with `A_A ≠ A_B`, and 0/320 with any
substrate divergence.**

The observers disagree about which nodes are unresolvable in up to 44% of stage-rows —
by a mean of 3.2 nodes, and in the limit by *everything* (Jaccard reaches 0.0) — and the
substrate does not diverge in a single instance. This is structural, not statistical.
Preflight §A4 established the cause directly: notebook 2's `run()` chooses growth sites
as `to_absorb = {v ∈ frontier : v adjacent to past}` with `frontier = set(sr) − past`.
Neither `A_A`, nor `A_B`, nor `w` appears anywhere in that choice. Verified by
construction: **the graph-size trajectory is bit-identical for `w ∈ {1,3,12,26,50}`** on
a fixed seed. Per §4's instruction, this is reported as a finding; no rewrite was
attempted, per §0.

## R4 target regime — not attainable

§5 asks for a `w` "in the degraded regime (concordance ≈ 0.6)". **No such `w` exists in
the swept space.** The global minimum pooled concordance over all 50 self-weights is
**0.9546** (at `w = 2`); restricted to stages 0–1, where genuine label privacy still
exists (preflight B1), the minimum is **0.8178** (at `w = 6`). R4 was therefore run at
**both argmin candidates** rather than at a single silently-substituted value.

## R3 (degree binning) — the discriminating test — **the ω collapse holds**

Terciles of live degree; F2's fit repeated within each bin.

| degree bin | n | mean d | **ω midpoint x₀** | **w midpoint x₀** |
|---|---|---|---|---|
| d ≤ 2 | 330,250 | 2.00 | 1.332 | 1.41 |
| 2 < d ≤ 9 | 234,750 | 4.17 | 0.925 | 7.59 |
| d > 9 | 269,850 | 16.37 | 1.037 | 15.66 |
| **CV across bins** | | | **0.157** | **0.710** |

The ω midpoint stays near 1 in every degree bin; the w midpoint tracks the bin's degree
and shifts by an order of magnitude. **CV(x₀) is 4.5× smaller in ω than in w.** In
`R3_degree_bins.png` the three ω curves superpose and the three w curves are visibly
separated, each saturating near its own bin's degree. Degree normalization is the correct
coordinate; the pooled w ramp of F2 is the §7 pooling artifact, as warned.

## R2 (surface)

Concordance over `(ω, φ)`; cells with n < 30 suppressed. `φ` is capped at 0.5 (see F3).

| ω \ φ | (0, 0.25] | (0.25, 0.5] |
|---|---|---|
| (0.0, 0.2] | 0.9686 | 1.0000 |
| (0.2, 0.4] | 0.9427 | 0.9998 |
| (0.4, 0.6] | 0.9174 | 0.9962 |
| (0.6, 0.8] | **0.8887** | 0.9995 |
| (0.8, 1.0] | 0.9105 | 0.9970 |
| (1.0, 1.5] | **1.0000** | **1.0000** |
| (1.5, 2.0] | 1.0000 | 1.0000 |
| (2.0, 3.0] | 1.0000 | 1.0000 |
| (3.0, 10.0] | 1.0000 | 1.0000 |

Two independent routes to objectivity are visible: `ω ≥ 1` (exact, for any φ), and
freezing a quarter to a half of the neighbourhood (φ > 0.25 lifts every sub-threshold
cell above 0.996).

---

## Summary

| prediction | verdict | deciding number |
|---|---|---|
| **F1** primary | **FAIL** (A pass, B fail) | 0.9506 vs ≤ 0.80 ceiling |
| **F2** sharpness | **FAIL** (slope pass, residual fail) | RMSE 0.00886 (ω) > 0.00313 (w) |
| **F3** control | **NULL** — not measurable (no φ = 1.0 rows; φ ≤ 0.5) | P0.3 gives 1.0000 / 5625 |
| **F4** recovery | **FAIL**; §4 conditional fires | 0.6899 vs 0.44 ± 0.10; K=4→0.4020, K=2→0.6751 |
| **F5** divergence | **NULL**; registered possibility **CONFIRMED** | 140/320 disagreements, 0/320 divergences |
| R3 (mechanism) | ω collapse holds | CV(x₀) 0.157 (ω) vs 0.710 (w) |

**Three of five frozen predictions fail as written and two are null. No prediction passed
outright.** The mechanism those predictions were built to test is nonetheless supported by
the R3 collapse and by the exact `ω > 1` result.

---
---

# Implications for the substrate-side vs observer-side reading

*Written after the above, and separated from it as §6.5 requires.*

The growth set is objective exactly where the analysis said it would be and private exactly
where it said it would be, but the campaign cannot use that fact to discriminate the two
readings, because notebook 2 has already decided the question in its implementation. The
band result is as sharp as a result of this kind can be — concordance is *exactly* 1.000000
across 713,841 node-stage rows with `ω > 1`, the threshold sits at `ω = 1.036` by fit, and
the collapse holds within every degree bin (CV of the midpoint 0.157 in ω against 0.710 in
w) — so `ω = w/d` is confirmed as the governing coordinate and `A` is confirmed to be
observer-dependent below it, with two observers reaching Jaccard as low as 0.0 on the same
graph. That is the substantive yield, and it is a correction to the paper: `A` is not
observer-independent in general, only for `ω > 1`, and the paper's own §6 configuration
(`w = 3`, `d ≈ 16`, `ω ≈ 0.19`) sits deep in the private regime where its 0.44 frontier
agreement was measured. But the substrate-side reading cannot be *tested* here, because
notebook 2 does not let the incompleteness set act: growth sites are `frontier ∩ N(past)`,
a purely structural rule in which `A_A`, `A_B` and `w` never appear, and the graph-size
trajectory is consequently bit-identical across a fifty-fold range of `w`. Two observers
who disagree about which nodes are unresolvable — in 44% of stage-rows at `w = 2`, by a
mean of 3.2 nodes — still expand at identical sites, on one shared graph object, with an
identical frozen trunk, in every one of 320 R4 stage-rows. The substrate-side reading is
therefore not a finding of this campaign but an assumption of its instrument, and the
observer-side reading is not disconfirmed but unrepresentable. Deciding between them
requires the fork that F5 anticipated and §0 deferred: per-observer graphs with expansion
driven by each observer's own `A`, which notebook 1's `step_forward` already implements for
a single observer and which no notebook combines with the multi-observer freeze. Until that
exists, the honest claim is the conditional one — *if* growth is driven by the observer's
own incompleteness set, then below `ω = 1` observers must fork, and the shared past of §6 is
a consequence of the shared substrate that notebook 2 assumes rather than evidence for it.
