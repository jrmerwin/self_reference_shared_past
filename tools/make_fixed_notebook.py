"""Build shared_past_mechanism_fixed.ipynb from the as-published notebook.

Applies the ERRATA E1 timing fix and nothing else, then executes the result so
its stored outputs are real. Run from the repository root:

    python tools/make_fixed_notebook.py
"""
import os
import nbformat
from nbclient import NotebookClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "shared_past_mechanism.ipynb")
DST = os.path.join(ROOT, "shared_past_mechanism_fixed.ipynb")

ANCHOR = """    past.add(anchor); gen[anchor] = 0
"""

FIX = """    past.add(anchor); gen[anchor] = 0
    # ---- ERRATA E1 FIX (the only change from the as-published notebook) ----
    # Freezing writes to o.frozen only. Each observer's LABEL at the anchor is
    # not refreshed until the settle() at the end of the first iteration, but
    # the stage-0 trace is recorded before that -- so stage 0 scored private
    # pre-freeze labels instead of the frozen consensus, driving agree_core to
    # 0.00 at stage 0 and dragging the reported mean and minimum down with it.
    # Settle here, before the loop, so the first trace reads the frozen past.
    for o in observers: o.settle(10)
    # ------------------------------------------------------------------------
"""

NOTE = """## ⚠️ This is the corrected copy — see [`ERRATA.md`](ERRATA.md)

This notebook is `shared_past_mechanism.ipynb` with **one change**, marked
`ERRATA E1 FIX` in the `run()` cell below. The as-published notebook is preserved
unchanged in this repository and in git history.

**The defect.** The as-published Cell 6 printed *"The core sits at 1.000 and does not
decay"* directly above *"Minimum core agreement observed anywhere: 0.000"*, and reported a
mean core agreement of 0.884.

**The cause.** The anchor is frozen before the stage loop, but freezing writes only to
`o.frozen`; each observer's *label* at the anchor was not refreshed until the `settle()` at
the end of the first iteration. The stage-0 trace was recorded in between, so it scored the
observers' private pre-freeze labels — `[0,0,1,1]` rather than the frozen `[0,0,0,0]`.

**The effect.** Stage 0 alone was corrupted; every stage from 1 onward already read 1.000.
The paper's §6 wording — "the earliest-frozen core sits at full agreement *at every
subsequent stage*" — is therefore correct as published. This was a defect in the notebook's
reported output, not in the paper's claim.

**After the fix**, core agreement is 1.000 at every stage including stage 0, so the mean and
the minimum both read 1.000 and Cell 6's narrative line matches its own numbers.
"""


def main():
    nb = nbformat.read(SRC, as_version=4)

    target = [i for i, c in enumerate(nb.cells)
              if c.cell_type == "code" and "def run(" in c.source]
    assert len(target) == 1, f"expected exactly one run() cell, found {target}"
    i = target[0]
    assert nb.cells[i].source.count(ANCHOR) == 1, "anchor line not uniquely found"
    nb.cells[i].source = nb.cells[i].source.replace(ANCHOR, FIX)

    nb.cells.insert(1, nbformat.v4.new_markdown_cell(NOTE))

    client = NotebookClient(nb, timeout=900, kernel_name="python3",
                            resources={"metadata": {"path": ROOT}})
    client.execute()
    nbformat.write(nb, DST)
    print(f"wrote {DST}")

    for c in nb.cells:
        if c.cell_type == "code":
            for o in c.get("outputs", []):
                if o.get("output_type") == "stream":
                    print("".join(o["text"]))


if __name__ == "__main__":
    main()
