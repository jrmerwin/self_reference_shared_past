# self_reference_shared_past

Code accompanying **"Incompleteness as Expansion: A Self-Reference Mechanism for Shared
Reality, the Arrow of Time, and the Open Future"**, Jason Merwin,
[ai.viXra:2606.0082](https://ai.vixra.org/abs/2606.0082), submitted 2026-06-30 05:52:42 UTC.

---

## Artifacts

| file | paper section | implements |
|---|---|---|
| [`unified_selfreference_mechanism.ipynb`](unified_selfreference_mechanism.ipynb) | §§2–4, Table 1 | the observer, the resolvability test, the independent definitions of `A` and `B`, the generative stepping rule, and the β-sweep. Verifies the diagonal lemma directly (exhibits the 2-cycle), checks `A = B` across independent random instances (12/12 exact, with persistent nonempty incompleteness), and reproduces the survival sweep of Table 1 from fixed seeds. |
| [`shared_past_mechanism.ipynb`](shared_past_mechanism.ipynb) | §6 | multi-observer shared-history dynamics; measures agreement separately on the contested frontier and the resolved past, bucketed by freeze generation, and exhibits the shared core under shared-history freezing. |
| [`sterile_final_pre_paper_test.py`](sterile_final_pre_paper_test.py) | §5, Tables 2–3 | the sterile-basin control on the native DEU registry: identifies σ, constructs matched universal-S controls, runs fixed-β stress tests at β = 1.3, and reruns the refined threshold check with 64 seeds per β. |

Read [`ERRATA.md`](ERRATA.md) before using `shared_past_mechanism.ipynb`. It documents a
defect in that notebook's Cell 6 output and a K-dependence in its agreement statistic. The
paper's own §6 wording is unaffected by the first and imprecise about the second.

[`shared_past_mechanism_fixed.ipynb`](shared_past_mechanism_fixed.ipynb) is the corrected
notebook. The original is unchanged, both on disk and in history.

## Provenance

**Dates are not fabricated.** Nothing in this repository has been backdated, no
`GIT_COMMITTER_DATE` or `--date` override has been used, and no history has been rewritten.
Every commit date is the true date of committing. Hash-locked timestamping is the
credibility mechanism of this program; a repository that lied about its own dates would be
worth less than no repository. The history is therefore in two parts, and the split is
real:

| | date | |
|---|---|---|
| repository created, `shared_past_mechanism.ipynb` uploaded | **2026-06-25** | five days **before** publication |
| paper published | 2026-06-30 | |
| `unified_selfreference_mechanism.ipynb` and `sterile_final_pre_paper_test.py` added | **2026-07-25** | twenty-five days **after** publication |
| errata, corrected notebook, campaign, manifest added | 2026-07-25 | |

§8 of the paper describes three artifacts and cites this repository for all of them. Only
one was uploaded before publication. The other two were present and unchanged on the
author's machine throughout — their filesystem timestamps still read their original
authoring dates, 2026-06-12 and 2026-06-22 — but they were not committed here until
2026-07-25. For that interval the citation resolved to an incomplete repository. That is
stated rather than concealed.

**The artifacts are the as-published files.** All three were verified byte-identical to the
working copies from which the paper's numbers were taken, before and after commit. Stored
execution outputs are intact in both notebooks. No reconstruction was required and none was
performed:

```
c6406300fcb0d7e455ca4172cdc21dd9  shared_past_mechanism.ipynb
46333078ea79e71b1aeae0c598af9101  unified_selfreference_mechanism.ipynb
c6d2182ead2907486adb14502eda3f72  sterile_final_pre_paper_test.py
```

The `shared_past_mechanism.ipynb` digest is of the file as uploaded on 2026-06-25; it was
checked against the working copy and matches, and the file has not been modified since.

A later campaign (below) grafted notebook 1's resolvability predicate onto notebook 2's
observer and added self-weight plumbing. It did so in a separate engine module and left
every notebook untouched.

`.gitattributes` sets `* -text` so end-of-line conversion cannot silently alter these files
on checkout and invalidate the digests above.

The README preceding this one held an earlier draft of the abstract than the one published
on viXra — it describes the sterile-basin result as the closing control, where the published
abstract instead closes on the transfer into the DEU registry. It remains in history.

## Verifying integrity

[`MANIFEST.sha256`](MANIFEST.sha256) covers every committed artifact.

```bash
git clone https://github.com/jrmerwin/self_reference_shared_past.git
cd self_reference_shared_past
sha256sum -c MANIFEST.sha256          # GNU coreutils / Git Bash
shasum -a 256 -c MANIFEST.sha256      # macOS
```

Regenerate with [`tools/make_manifest.sh`](tools/make_manifest.sh), which enumerates
git-tracked files via `git ls-files`, so the manifest cannot silently omit a committed file
or include an untracked one.

## Running

Python 3.12 with `numpy`, `networkx`, `scipy`, `matplotlib`, `pandas`. The notebooks were
authored under Python 3.12.3; the campaign was run under 3.12.4 / numpy 2.4.4 /
networkx 3.4.2.

```bash
jupyter lab unified_selfreference_mechanism.ipynb
python sterile_final_pre_paper_test.py
```

`sterile_final_pre_paper_test.py` writes its CSV/JSON output to `OUTDIR`, set at the top of
the file to `/mnt/data` (the sandbox path it was authored in). Change it before running.

## Post-publication work

[`campaigns/growth_set_objectivity/`](campaigns/growth_set_objectivity/) contains a
pre-registered campaign, run 2026-07-25, testing whether the incompleteness set `A` is
observer-independent as §6 treats it. It is not part of the paper. Its principal result is
that `A` is objective exactly when `ω = w/d(v) > 1` — concordance is exactly 1.000000 over
713,841 node-stage rows above that threshold — and observer-dependent below it, where two
observers reach Jaccard 0.0 on the same graph. The pre-registration, preflight report,
decision record, primary data table and figures are all included. See its
[decision record](campaigns/growth_set_objectivity/decision_record.md) for what passed,
what failed, and what could not be measured.

## Not in this repository

`frontier_identity_machinery_skeleton.ipynb` sits alongside these files in the author's
working directory but is **not** part of this paper. It is a machinery-validation skeleton
for the DEU registry's S/I/G typing, and its own header states that its typing is a
structural proxy and that every number in it is diagnostic and carries no physical meaning.
Including it here would misrepresent it as supporting the paper's results.

## Citation

```bibtex
@misc{merwin2026incompleteness,
  author = {Jason Merwin},
  title  = {Incompleteness as Expansion: A Self-Reference Mechanism for Shared Reality,
            the Arrow of Time, and the Open Future},
  year   = {2026},
  note   = {ai.viXra:2606.0082},
  url    = {https://ai.vixra.org/abs/2606.0082}
}
```
