# Instrument Certification — C1 / C2 / C3

**VERDICT: C2 FAILED. Campaign stopped at certification. Run A and Run B were not
executed.**

Pre-registration §6: *"Certification is blocking. If C2 fails, stop. A variant that cannot
reproduce Table 1 is not the engine that produced Table 1."* That condition is met, so no
sweep was run and no `rows_runA.csv` / `rows_runB.csv` exist.

The failure is **not** in the `w` plumbing. The plumbed variant is bit-exact against the
original notebook at every β. What fails is the step above it: **the original notebook,
run unmodified, does not reproduce the paper's Table 1.**

Pre-registration hash-locked before any run:
`99d0925394bf4ae4d8ec44ddd84fb4282fd69f48ac0fad74d4f966523a064e49`, commit `ad565c4`,
pushed to `origin/main` and verified live before the first run executed.

---

## C1 — the original default `w`, and the degree distributions that set ω

**Original default self-weight: `w = 3`**, from `def conclusion(self, v, sw=3)` in both
notebooks. `required()` never forwards it, so every published β_c was produced at this one
value and no other value was reachable without editing the source.

| substrate | nodes | mean `d` | median | max | min |
|---|---|---|---|---|---|
| toy (n0 = 60, radius 0.30, 32 seeds) | 1920 sampled | **12.510** | 12.0 | 25 | 1 |
| 137-registry (5347 edges; S=81, I=40, G=16) | 137 | **78.058** | 73.0 | **136** | 73 |

σ: id 69, degree 136, multiplicity 1 — matches the paper's §5 description exactly.

```
<d>_registry / <d>_toy = 6.239
```

**ω̄ at the published default `w = 3`: toy 0.2398, registry 0.0384.** The two published β_c
values were therefore obtained at ω̄ values a factor of 6.24 apart — which is precisely the
comparison W2 was designed to make, and it cannot be made without the sweep that C2 blocks.

Note the registry's minimum degree is 73: it is a dense, near-complete graph in which every
node is a hub. The toy substrate's minimum degree is 1. These are not comparable substrates
at equal `w`.

## C2 — bit-exactness against Table 1: **FAIL**

12 seeds per β (0–11), `run_to_outcome` defaults (n0 = 60, radius 0.30, stage budget 30,
cap 12000), exactly as Table 1's caption specifies.

| β | paper Table 1 | original notebook | plumbed variant (`w`=3) | per-seed sequences identical | variant = paper |
|---|---|---|---|---|---|
| 0.6 | 0.00 | 0.00 (0/12) | 0.00 (0/12) | ✅ | ✅ |
| 0.7 | 0.00 | 0.00 (0/12) | 0.00 (0/12) | ✅ | ✅ |
| 0.8 | 0.00 | 0.00 (0/12) | 0.00 (0/12) | ✅ | ✅ |
| 0.9 | 0.08 | 0.08 (1/12) | 0.08 (1/12) | ✅ | ✅ |
| **1.0** | **0.17** (2/12) | **0.25 (3/12)** | **0.25 (3/12)** | ✅ | ❌ |
| 1.1 | 0.58 | 0.58 (7/12) | 0.58 (7/12) | ✅ | ✅ |
| 1.2 | 0.75 | 0.75 (9/12) | 0.75 (9/12) | ✅ | ✅ |
| **1.3** | **0.92** (11/12) | **0.83 (10/12)** | **0.83 (10/12)** | ✅ | ❌ |
| **1.4** | **0.92** (11/12) | **0.83 (10/12)** | **0.83 (10/12)** | ✅ | ❌ |
| 1.5 | 0.92 | 0.92 (11/12) | 0.92 (11/12) | ✅ | ✅ |
| 1.6 | 0.92 | 0.92 (11/12) | 0.92 (11/12) | ✅ | ✅ |

**Two separate results, and they must not be conflated.**

**(a) The plumbing is clean.** The per-seed outcome sequence — not merely the count — is
identical between the original notebook and the `w`-plumbed variant at **every β**. The
`[W]` edits in `src/engine_w.py` change no predicate, no RNG draw and no branch. Threading
`w` is certified correct.

**(b) The notebook does not reproduce Table 1.** Three of eleven rows differ, each by
exactly one seed out of twelve, in both directions (one extra survivor at β = 1.0, one
fewer at β = 1.3 and 1.4).

### This is not an environment artifact

The sweep was run under two independent stacks:

| | Python | numpy | networkx | scipy | substrate seed 0 | result |
|---|---|---|---|---|---|---|
| miniconda | 3.12.4 | 2.4.4 | 3.4.2 | 1.17.1 | 60 nodes / 416 edges / degsum 832 | 0.25, 0.83, 0.83 |
| anaconda | 3.11.7 | 1.26.4 | 3.1 | 1.11.4 | 60 nodes / 416 edges / degsum 832 | 0.25, 0.83, 0.83 |

Identical substrate fingerprints and identical survival counts at every β across a numpy
major version and a networkx minor version. `random_geometric_graph` did not drift. The
notebook is deterministic and reproducible; it simply does not produce Table 1.

### Both artifacts are internally self-consistent — with each other, they disagree

| source | P(β=1.0) | P(β=1.1) | interpolated β_c |
|---|---|---|---|
| notebook, rerun here | 0.25 | 0.583 | **1.0750** |
| notebook's own **stored** Cell 8 output | — | — | **1.075** |
| paper Table 1 | 0.17 | 0.58 | **1.0805** → quoted as ≈1.08 |

The rerun matches the notebook's stored output to the digit. The paper's β_c ≈ 1.08 is the
correct interpolation **of the paper's own table**. So each artifact is coherent on its own
terms, and the committed notebook is not the source of the committed table. Either the
table was transcribed from a different run or a superseded code state, or β_c ≈ 1.08 is a
rounding of 1.075 and the three table cells are transcription errors. **This certification
cannot distinguish those, and does not guess.**

The gap is small — one seed in twelve, three times — and it does not move β_c materially
(1.075 vs 1.081). It is reported because C2 required bit-exactness and did not get it.

## C3 — the sterile-basin script: **Table 2 PASS, Table 3 FAIL**

Run unmodified, as committed. C2's blocking clause bars use of the notebook-1 *variant*;
the sterile script is a different instrument and was certified separately.

### C3a — Table 2, fixed-β stress test at β = 1.3, 32 seeds, max_res 1200: **exact**

| condition | P_sustain | mean resolutions | mean final \|A\| | paper |
|---|---|---|---|---|
| Baseline, no capture | 1.00 | 1200.0 | **498.1** | 1.00 / 1200.0 / 498.1 ✅ |
| σ pinned, no capture | 1.00 | 1200.0 | **497.3** | 1.00 / 1200.0 / 497.3 ✅ |
| σ contact, γ = 1 | 1.00 | 1200.0 | **488.8** | 1.00 / 1200.0 / 488.8 ✅ |
| Matched universal-S contact, γ = 1 | 1.00 | 1200.0 | **492.5** | 1.00 / 1200.0 / 492.5 ✅ |
| σ adjacent, γ = 0.5 | 0.00 | 398.1 | 0.0 | 0.00 / 398.1 / 0.0 ✅ |
| Matched universal-S adjacent, γ = 0.5 | 0.00 | 398.1 | 0.0 | 0.00 / 398.1 / 0.0 ✅ |

**All six rows reproduce to the last decimal, including the discriminating
498.1 / 497.3 / 488.8 / 492.5 spread.** The committed script *is* the engine that produced
Table 2. This is what a passing certification looks like, and it is the reason the C2
result can be trusted as a real discrepancy rather than a harness error: the same
methodology reproduces one published table exactly and another not at all.

### C3b — Table 3, refined threshold check: **not reproduced**

Table 3's caption specifies "64 seeds per β and a higher resolution cap near the relevant
crossings". The committed script's sweep block uses 20 seeds and `max_res=1000`. Both were
tried.

| condition | paper | as committed (20 seeds, cap 1000) | caption (64 seeds, cap 2000) |
|---|---|---|---|
| Baseline, no capture | **0.906** | 0.811 | 0.997 |
| σ pinned, no capture | **0.915** | 0.800 | 0.993 |
| σ contact, γ = 1 | **0.914** | 0.818 | 0.997 |
| Matched universal-S contact, γ = 1 | **0.914** | 0.811 | 0.997 |
| σ adjacent, γ = 0.5 | **1.820** | 1.757 | 1.831 |
| Matched universal-S adjacent, γ = 0.5 | **1.820** | 1.757 | 1.831 |

The published values sit **between** the two configurations tried, so the exact
configuration behind Table 3 is not recoverable from the committed script. The β grid
`[0.5, 0.7, 0.9, 1.1, …]` has 0.2 spacing, so every crossing here is an interpolation
across a wide interval and is sensitive to both seed count and cap. Note the caption's
phrase is ambiguous — "higher resolution cap" could mean a larger `max_res` (the reading
tried above) or a finer β grid near the crossing. Neither reading was tuned further; two
configurations were tried and reported.

The **qualitative** content of Table 3 does reproduce under both configurations, and it is
the content the paper's Proposition 2 rests on: baseline, pinned and contact conditions
cluster tightly together, and the strong adjacent rule moves the threshold sharply upward
by the same amount for σ and for its matched universal-S control. σ is not singled out.
That conclusion is unaffected.

### Diagnostic: which configuration produces Table 1? None of the obvious ones

A small, pre-listed set of plausible configuration differences was tried, to distinguish
"transcription error" from "different code state". This is a **diagnostic, not a fit** —
nothing found here would have been carried into a downstream run, and C2 is blocking
regardless of the outcome.

| variant | β_c | reproduces Table 1 | β where it differs |
|---|---|---|---|
| as committed (seeds 0–11, r = 0.30, settle 6) | 1.0750 | ❌ | 1.0, 1.3, 1.4 |
| seeds 1–12 | 1.0750 | ❌ | 1.0, 1.3, 1.4 |
| radius 0.32 (`build`'s own default) | 1.1000 | ❌ | 7 of 11 rows |
| settle = 8 | 1.1000 | ❌ | 7 of 11 rows |
| stage budget 25 | 1.0500 | ❌ | 0.9, 1.0, 1.3, 1.4 |

**No variant reproduces Table 1.** The three alternatives that change substrate or
relaxation (radius 0.32, settle 8, stages 25) move the result *further* from the published
table, not closer, and shift β_c to 1.10 / 1.10 / 1.05. Shifting the seed block to 1–12
changes nothing at all. The committed configuration remains the closest to Table 1 of
everything tried, and it is the configuration Table 1's own caption specifies.

The search was stopped here deliberately. Continuing until something matched would be
fitting a configuration to a target, which is the failure mode the pre-registration's §6
"`w` is not free" clause exists to prevent — applied here to a different parameter.

---

## Consequence

Run A and Run B are not executable under this pre-registration as written. The blocking
clause is unambiguous and the condition triggering it is met.

Note what C2's failure does *not* say. It does not show the mechanism is wrong, and it does
not invalidate β_c ≈ 1.08 as an approximate value — the notebook's own 1.075 rounds to 1.08.
It shows that the committed notebook and the published Table 1 are not the same run, which
is exactly the property C2 exists to test, and which must be resolved before a `w`-sweep
built on that notebook can be said to qualify a published number.

**What would unblock the campaign**, in the order that costs least:

1. **Confirm the intended Table 1.** If 0.25 / 0.83 / 0.83 is correct and the published
   0.17 / 0.92 / 0.92 are transcription errors, then the notebook is the engine, C2 passes
   against corrected values, and Run A proceeds unchanged. β_c moves 1.081 → 1.075 and no
   claim in the paper changes.
2. **Or supply the code state that produced Table 1**, if a different one exists. C2 then
   re-runs against that.
3. **Or amend the pre-registration** to certify against the notebook's stored output rather
   than the paper's table, disclosing that Table 1 and the notebook disagree. This is a
   weaker certification and should be an explicit decision, not a silent relaxation — which
   is why it was not taken here.

The same question applies to Table 3, independently.
