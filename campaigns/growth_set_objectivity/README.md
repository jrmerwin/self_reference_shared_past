# Campaign: Objectivity of the Growth Set as a Function of Self-Weight

Run 2026-07-25. **Not part of ai.viXra:2606.0082.** This is post-publication work testing an
assumption the paper makes in §6: that the incompleteness set `A` is observer-independent.

**It is not.** `A` is objective exactly when `ω = w/d(v) > 1` and observer-dependent below
it. Concordance between two observers is *exactly* 1.000000 across 713,841 node-stage rows
with `ω > 1` — zero discordant rows — while below the threshold two observers reach Jaccard
0.0 on the same graph.

Read in this order:

1. [`PREREGISTRATION.md`](PREREGISTRATION.md) — the frozen document, transcribed verbatim,
   with a provenance note on its hash-lock status.
2. [`preflight_report.md`](preflight_report.md) — the blocking P0.1/P0.2/P0.3 gates, the
   discrepancies found between the pre-registration and the code, and two instrument
   properties recorded *before* the sweep ran.
3. [`decision_record.md`](decision_record.md) — F1–F5 marked pass / fail / null with the
   number that decided each, then a clearly separated implications paragraph.

**No prediction passed outright: three failed as written, two were null.** The mechanism
those predictions were built to test is nonetheless supported, by the R3 degree collapse and
the exact `ω > 1` result. The decision record explains each gap between a threshold and the
claim it was testing.

## Findings that bear on the paper

Two defects in `shared_past_mechanism.ipynb` surfaced here and are written up in
[`../../ERRATA.md`](../../ERRATA.md): the Cell 6 core-agreement timing defect (E1) and the
K-dependence of `agree_on` (E2). Neither changes a claim in the paper; E1's wording in §6 is
already correct, and E2 means §6's ≈0.44 understates the frontier structure it reports.

## Files

| file | what it is |
|---|---|
| `rows_R1.csv` | **primary artifact.** 834,850 rows; one row per self-referential node per stage, measured at stage start before expansion. 42.2 MB, committed uncompressed. |
| `summary_R1.csv` | 22,400 stage-rows: per-stage Jaccard, concordance, label agreements, substrate divergence. |
| `rows_R4_w2.csv`, `rows_R4_w6.csv` | R4 divergence runs at both argmin candidates (§5's target regime does not exist; see decision record). |
| `concordance_vs_omega.png` | F1/F2 — the step at ω = 1. |
| `concordance_vs_w.png` | F2 — the pooled `w` curve, flat, showing the §7 degree-pooling artifact. |
| `surface_omega_phi.png` | R2 — concordance over (ω, φ). |
| `R3_degree_bins.png` | R3 — the ω collapse and the `w` shift across degree terciles. The discriminating test. |
| `preflight_results.json`, `decision_results.json` | machine-readable raw values behind both reports. |

## Regenerating

Python 3.12.4, numpy 2.4.4, networkx 3.4.2, scipy, pandas, matplotlib. From this directory:

```bash
cd src
python preflight.py     # blocking gates -> ../preflight_results.json   (~1 min)
python sweep_R1.py      # R1 -> ../rows_R1.csv, ../summary_R1.csv       (~6 min, resumable)
python analyze.py       # R2/R3, F1-F5, figures -> ../decision_results.json
python run_R4.py 6      # R4 -> ../rows_R4_w6.csv
python run_R4.py 2      # R4 -> ../rows_R4_w2.csv
python f4_control.py    # F4's K-dependence control, on notebook 2's original code
```

All runs are seeded and deterministic; `sweep_R1.py` resumes from a partial
`summary_R1.csv`. `f4_control.py` and `preflight.py` read the notebooks directly out of the
repository root and `exec` their original cells, so they verify against the as-published
code rather than against a copy.

`src/engine.py` carries the resolvability predicate. It is copied verbatim from the
notebooks; the four deviations are marked `[MOD-1]`…`[MOD-4]` in-file and justified in the
preflight report. `[MOD-1]`, the only change to a predicate, is verified bit-exact against
notebook 1's original class over 1600 node-verdicts (preflight P0.1c).
