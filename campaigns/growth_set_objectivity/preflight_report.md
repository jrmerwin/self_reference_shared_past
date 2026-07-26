# Preflight Report — Objectivity of the Growth Set

**Status: PREFLIGHT PASSES. Campaign is not void. Proceed to §5 runs.**

Executed 2026-07-25. All results below are from `src/preflight.py`, raw numbers in
`preflight_results.json`.

**Environment.** `c:/Users/merwijas/miniconda3/python.exe` — Python 3.12.4, numpy 2.4.4,
networkx 3.4.2. Chosen as the closest available interpreter to the notebooks' recorded
kernel (3.12.3). The rounding convention (P0.1) was cross-checked on a second interpreter
(Python 3.11.7 / numpy 1.26.4) and is identical, so no boundary case depends on the
numpy major version.

---

## §A — Discrepancies between the pre-registration and the repo (read first)

These were found while locating the resolvability test. None is blocking, but three of
them change what §5 can mean, so they are recorded before any result.

**A1. The repo named in the pre-registration does not exist.** There is no
`self_reference_shared_past` repo on this machine. The notebooks live in
`dataScience/DEU_SR/`, which is untracked and is excluded by the home-directory
`.gitignore` (that repo admits only `dataScience/DEU_voids/`). Work was done in
`DEU_SR/objectivity_campaign/`. Nothing was committed or pushed.

**A2. Notebook 2 contains no resolvability test.** The declared base,
`shared_past_mechanism.ipynb`, defines `Observer.conclusion`, `.required`, `.settle` —
and nothing else. It has no `resolvable()`, no `incompleteness()`, and never computes an
incompleteness set. Its "frontier" is `set(sr) - past`, a structural set difference.

The resolvability test exists only in **notebook 1**, `unified_selfreference_mechanism.ipynb`:

```python
def resolvable(self, v):
    """Does a within-stage fixed point label exist for v?"""
    for cand in (0, 1):
        old = self.label[v]; self.label[v] = cand
        req = self.required(v); self.label[v] = old
        if req == cand:
            return True
    return False
```

Per P0.1 this was taken **as-is**. The campaign engine is therefore notebook 2's Observer
(which uniquely has the `frozen` bookkeeping the campaign needs) with notebook 1's
`resolvable()`/`incompleteness()` grafted on unmodified. This is a merge of two notebooks,
not a reimplementation; the merge is verified bit-exact in P0.1c.

**A3. `w` is unreachable from outside the notebooks.** Both notebooks write the self-weight
as a *default argument of `conclusion()`* — `def conclusion(self, v, sw=3)` — which
`required()` calls as `self.conclusion(v)`, never forwarding `sw`. There is no way to
sweep `w` without an edit. `[MOD-1]` promotes it to a constructor argument defaulting to 3.
This is the only change to any predicate.

**A4. Notebook 2's expansion is independent of resolvability — and of the observers.**
In `run()`, growth sites are `to_absorb = frontier nodes adjacent to past`, where
`frontier = set(sr) - past`. Neither `A_A` nor `A_B` nor `w` appears anywhere in the
choice of where to expand. Verified empirically: the graph-size trajectory is bit-identical
for `w ∈ {1, 3, 12, 26, 50}` on a fixed seed —
`[60, 66, 73, 87, 100, 110, 112, 115, 117, 118, 121, 123, 125, 128]`.

This is the **registered possibility in F5, realized in its strongest form**. Consequences
are stated in the decision record; no rewrite was attempted, per §0 and F5.

**A5. Bindings the pre-registration left open.** `β = 1.3` is fixed by §5 but notebook 2's
`run()` has no β at all; the Poisson(β) branching was lifted verbatim from notebook 1's
`step_forward()` (`[MOD-2]`). Table 1 of the paper is not available on this machine, so the
substrate is bound to notebook 1's `run_to_outcome` defaults, which are the only place
`n0=60` appears in the repo: `build(n=60, frac=0.25, radius=0.30)`. Stage count is bound to
notebook 2's `stages=14` for R1 and to `20` for R4 per §5.

---

## P0.1 — Rounding convention

The convention is **banker's rounding (half-to-even)**, as the pre-registration warned.
`conclusion()` ends in `int(round(np.mean(vals)))`; `np.mean` returns `np.float64`, and
`round()` on a `np.float64` dispatches to numpy's half-to-even `__round__`.

| probe | value |
|---|---|
| `round(np.float64(0.5))` | `0` |
| `round(np.float64(1.5))` | `2` |
| `round(np.float64(2.5))` | `2` |
| `int(round(np.mean([0,1])))` | `0` |
| `type(np.mean([0,1]))` | `float64` |

Exact ties therefore round **down at 0.5** and **up at 1.5**. Since the evidence mean is
in [0,1], the only reachable tie is 0.5, which resolves to **0**. No substitute rounding
was introduced anywhere.

### P0.1c — `[MOD-1]` bit-exactness

Notebook 1's original `Observer` class was `exec`'d directly from the `.ipynb` JSON and run
against the campaign engine at `sw=3` on identical label states, 40 substrates:

**1600 node-verdicts compared, 0 mismatches.** `[MOD-1]` is bit-exact at the default.

---

## P0.2 — Brute-force validation of the band

Grid `d ∈ [3,20] × S ∈ [0,d] × w ∈ [1,25]` = **5625 configurations**. Each configuration was
materialised as an actual star graph with the exact `(d, S)` and passed to the repo's
`resolvable()`.

| comparison | disagreements |
|---|---|
| vs §1 as written — `2S < d+w` and `2S ≥ d−w` | **216 / 5625** |
| &nbsp;&nbsp;of which on the upper tie `2S == d+w` | 108 |
| &nbsp;&nbsp;of which on the lower tie `2S == d−w` | 108 |
| &nbsp;&nbsp;**not on any tie** | **0** |
| vs half-to-even-corrected — `2S ≤ d+w` and `2S > d−w` | **0 / 5625** |

**Every disagreement lies exactly on a rounding tie, and both boundaries flip.** The
campaign is therefore **not void**: the analytic condition is correct, and the exact
predicate the code implements is

```
unresolvable(d, S, w)  ⟺  2S ≤ d + w   AND   2S > d − w
```

which reproduces all 5625 configurations with zero error. This corrected form is used for
every downstream comparison. Note both inequalities moved in the *same* direction (the
band shifts up by one unit of `2S`), not symmetrically.

### The §1 consequence `w ≥ d ⟹ unresolvable` is **false as stated**

§1 asks that this be checked, not presumed. It fails in **18 configurations**, and they are
exactly `(d, S=0, w=d)` for every `d ∈ [3,20]`:

> at `w = d` with an all-zero neighbourhood, the lower tie `2S = d − w = 0` is not
> strictly exceeded, so the node is **resolvable**.

The correct statement is **`w > d` forces unresolvability**; at `w = d` exactly one
neighbourhood configuration escapes (`S = 0`). This lands precisely on `ω = 1.0`, the left
edge of F1's pass bin `ω ∈ [1.0, 1.5]`, so it is not merely pedantic — it is carried into
the F1 reading.

---

## P0.3 — Frozen-neighbourhood identity (instrument check)

Two observers with **different random initial labels** (seeds 0 and 12345) but a **shared
frozen neighbourhood** were constructed across the same 5625 `(d, S, w)` grid, settled, and
compared.

**Concordance = 1.0000 over 5625 configurations. 0 failures.**

The freeze bookkeeping is sound. As §7 insists, this is a bookkeeping identity and is not
evidence for anything.

---

## Substrate characterisation

`build(n=60, frac=0.25, radius=0.30)` over the 32 sweep seeds:

| mean d | median d | p99 d | **max d** |
|---|---|---|---|
| 12.51 | 12 | 23 | **25** |

`d_max = 25` fixes the R1 sweep range at **`w ∈ {1, …, 50}`** per §5.

---

## Additional preflight findings (non-blocking, but they govern how F1/F2 read)

Neither is a bug; both are properties of the instrument that §7's spirit requires be fixed
in writing before analysis.

**B1. Observer label privacy collapses after ~2 stages.** The fraction of nodes on which
the two observers carry different labels, per stage, at `w=3`, seed 0:

| stage | 0 | 1 | 2 | 3 | … | 13 |
|---|---|---|---|---|---|---|
| label-difference fraction | 0.717 | 0.571 | **0.068** | 0.073 | … | 0.101 |
| mean φ | 0.021 | 0.124 | 0.156 | 0.152 | … | 0.111 |

`settle(10)` on a shared graph with a shared frozen anchor is strongly contracting: the two
labelings converge to ~93% agreement by stage 2 **while φ is still ~0.15**. So any
concordance → 1 observed at stage ≥ 2 is attributable to label convergence, *not* to the
freeze fraction. Genuine label privacy exists only at stages 0–1. This is a confound for the
(ω, φ) surface and is reported as such rather than designed around.

**B2. Concordance is not monotone in ω, and diverges from Jaccard at low ω.** At small `w`
the band `2S ∈ (d−w, d+w]` is narrow, so almost every node is resolvable for *both*
observers and concordance is high *trivially* — agreement on a near-empty `A`. At `w=3`,
seed 0, stage 0: concordance `0.867` but Jaccard `0.33`. This is exactly the §7
measure-switching trap. Both are reported at every point; **Jaccard is the sensitive
statistic in the low-ω regime and concordance is not.**

---

**B3. Notebook 2's headline claim is contradicted by its own stored output, via the §7
timing trap.** Found while running the F4 recovery control. Notebook 2's cell 6 prints:

> `Mean agreement on earliest-frozen CORE (all stages, all trials): 0.884`
> `Minimum core agreement observed anywhere:                        0.000`
> *"The core sits at 1.000 and does not decay: the resolved past is stably shared."*

The narrative says 1.000; the number directly above it says the minimum is 0.000, and the
`min_core_agree` column reads `0.00` in 5 of 6 trials. Re-running the original code
reproduces this exactly (mean core agreement 0.8876 vs the stored 0.884).

The cause is a read-before-settle in `run()`: the anchor is frozen (`o.frozen[anchor]=0`)
but each observer's *label* at the anchor is not refreshed until the next `settle()`, and
the stage-0 trace is recorded in between. Verified directly — labels at the anchor
immediately after the freeze are `[0, 0, 1, 1]` across the four observers, giving
`agree_core = 0.0`; after one `settle()` they are `[0, 0, 0, 0]`, giving `1.0`.
Per-stage, `agree_core` is `0.00` at stage 0 and `1.00` at every stage thereafter in every
trial (trial 2 reads 1.00 at stage 0 only because its four observers happened to coincide).

So the narrative claim is correct for stages ≥ 1, and both the reported mean (0.884) and
minimum (0.000) are artifacts of a single mistimed stage-0 read. This is precisely the
error class §7 names first — *"Timing. Reading `A_X` after expansion inverts the result.
Assert the ordering in code."* — present in the declared base. It is the reason this
campaign asserts its measurement ordering in code (`[MOD-3]`) rather than trusting
placement.

## Verdict

P0.1 ✅ convention identified (half-to-even), no substitution.
P0.1c ✅ 0/1600 mismatches.
P0.2 ✅ 0/5625 non-tie disagreements — **campaign not void**; §1's `w ≥ d` corollary
corrected to `w > d`.
P0.3 ✅ concordance 1.0000, 0 failures.

Proceed to R1–R4.
