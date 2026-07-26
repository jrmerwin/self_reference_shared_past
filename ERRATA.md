# Errata

Defects found after publication of [ai.viXra:2606.0082](https://ai.vixra.org/abs/2606.0082),
during the growth-set objectivity campaign of 2026-07-25
([`campaigns/growth_set_objectivity/`](campaigns/growth_set_objectivity/)).

Both concern `shared_past_mechanism.ipynb` and the §6 shared-past result. Neither affects
`A = B`, the β-sweep of Table 1, or the sterile-basin controls of §5.

---

## E1 — Cell 6 reports a corrupted core-agreement statistic

**Severity: code-output defect. The paper's claim is correct as written.**

### What is wrong

`shared_past_mechanism.ipynb` Cell 6 prints, in this order:

```
Mean agreement on earliest-frozen CORE (all stages, all trials): 0.884
Minimum core agreement observed anywhere:                        0.000

The core sits at 1.000 and does not decay: the resolved past is stably shared.
```

The narrative line asserts 1.000 directly beneath a reported minimum of 0.000. Cell 4's
`min_core_agree` column reads `0.00` in five of six trials. As printed, the notebook
contradicts itself.

### Root cause — verified

A measurement-timing error in `run()`, not a defect in the mechanism.

The anchor is frozen before the stage loop begins:

```python
for o in observers: o.absorbed.add(anchor); o.frozen[anchor] = 0
```

but freezing writes only to `o.frozen`. Each observer's *label* at the anchor is not
refreshed until the next `o.settle(10)`, which happens at the **end** of the first
iteration. The stage-0 trace is recorded in between, so `agree_core` at stage 0 scores the
observers' private pre-freeze labels rather than the frozen consensus value.

Verified directly on the original code, four observers, seed 0:

| | labels at anchor | `agree_core` |
|---|---|---|
| after `settle`, before freeze takes effect | `[0, 0, 1, 1]` | — |
| immediately after freeze, no re-settle *(what stage 0 measures)* | `[0, 0, 1, 1]` | **0.0** |
| after one `settle()` | `[0, 0, 0, 0]` | **1.0** |

Per-stage, `agree_core` is `0.00` at stage 0 and `1.00` at every stage thereafter, in every
trial. Trial 2 reads `1.00` at stage 0 only because its four observers happened to coincide
by chance. The reported mean of 0.884 and minimum of 0.000 are both artifacts of this
single mistimed read; over stages ≥ 1 the mean is exactly 1.000.

### Effect on the paper — none

§6 states:

> "the earliest-frozen core sits at full agreement **at every subsequent stage**"

This wording is **already correct**. "Subsequent" excludes the stage-0 read, which is the
only corrupted point. The paper's claim holds exactly as published; it is the notebook's
Cell 6 summary statistics and its accompanying narrative line that are wrong.

Stated explicitly, because the distinction matters: **this is a defect in the notebook's
reported output, not an error in the paper's claim.** No correction to §6 is required.

### Fix

`shared_past_mechanism_fixed.ipynb` settles the observers immediately after the anchor is
frozen, before the stage loop is entered, so the stage-0 trace measures the frozen
consensus. With the fix, `agree_core` is 1.000 at every stage including stage 0, mean
1.000, minimum 1.000. The original notebook is unchanged in commit 1 and in history.

---

## E2 — `agree_on` decays combinatorially with the observer count K

**Severity: statistic is K-dependent; the paper reports it as a property of the frontier.**

### What is wrong

```python
return sum(1 for v in shared if len(set(nl[v])) == 1) / len(shared)
```

`agree_on` scores a node only when **all K** observers carry the same label. Under
independent labels the chance baseline is therefore

```
P(all K agree) = 2^(1-K)
```

— **0.500 at K = 2**, 0.250 at K = 3, **0.125 at K = 4**. The statistic is not comparable
across K, and a raw value cannot be read as "how much observers agree" without stating K.

§6 quotes the frontier agreement as ≈0.44. That is a **K = 4** number. `run()` defaults to
`K=4`, and the notebook's stored Cell 6 output records `0.435`.

### Measured, on the original unmodified code

24 trials, original substrate (n = 50, radius 0.32, w = 3):

| K | mean `agree_frontier` | chance `2^(1-K)` | **excess over chance** |
|---|---|---|---|
| 2 | 0.6751 | 0.500 | **0.175** |
| 3 | 0.5202 | 0.250 | 0.270 |
| 4 | 0.4020 | 0.125 | **0.277** |

The raw statistic falls with K while the excess over chance **rises**. Read naively, the
frontier looks *more* contested as observers are added; measured against baseline, the
frontier's structure is *stronger* at K = 4 than at K = 2. The paper's ≈0.44, taken as a
frontier property, understates the effect it is reporting — the number is mostly the
combinatorial baseline, not the signal.

### Recommendation for any future revision

Report either

- **pairwise mean agreement** — the mean over observer pairs of the fraction of nodes on
  which that pair agrees, which has a K-independent chance baseline of 0.5; or
- **excess over chance** — `agree_on − 2^(1-K)`, stated together with K.

Either makes the frontier and past statistics comparable across observer counts. If the raw
`agree_on` value is retained, K must be stated alongside it.

### Note on a related comparison

The growth-set campaign was pre-registered at K = 2 and asked to recover the paper's ≈0.44.
It could not, and this is why: at K = 2 the original code yields 0.6751, and the campaign
measured 0.6899 in the corresponding cell — agreement to 0.015. The campaign reproduces the
paper's dynamics; the 0.44 target was simply unreachable at the mandated observer count.
This is recorded in the campaign's decision record as F4.
