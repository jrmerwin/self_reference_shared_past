"""F4 control: is the paper's ~0.44 frontier agreement a K=4 number?

§5 of the pre-registration fixes TWO observers. Notebook 2's published run uses
K=4. `agree_on` scores a node only if ALL observers carry the same label, so the
statistic is mechanically K-dependent and the comparison to 0.44 is not
apples-to-apples unless K matches.

This runs notebook 2's ORIGINAL, UNMODIFIED code (exec'd straight out of the
.ipynb) at K=4 and K=2 to separate the K effect from any campaign effect.
"""
import json, os
import numpy as np

NB2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "shared_past_mechanism.ipynb")
nb = json.load(open(NB2, encoding="utf-8"))
ns = {}
src2 = "".join(nb["cells"][2]["source"]).split('print("Substrate')[0]
src4 = "".join(nb["cells"][4]["source"]).split("# run several trials")[0]
exec(compile(src2, "nb2_cell2", "exec"), ns)
exec(compile(src4, "nb2_cell4", "exec"), ns)
run, build = ns["run"], ns["build"]

print("notebook 2, ORIGINAL code, original substrate (n=50, radius=0.32, w=3):")
for K in (4, 3, 2):
    fr, pa, co = [], [], []
    for trial in range(24):
        t = run(*build(50, 0.25, trial), K=K, stages=14, seed=trial)
        fr += [x for x in t["agree_frontier"] if not np.isnan(x)]
        pa += [x for x in t["agree_past"] if not np.isnan(x)]
        co += [x for x in t["agree_core"] if not np.isnan(x)]
    print(f"   K={K}:  mean agree_frontier = {np.mean(fr):.4f}   "
          f"agree_past = {np.mean(pa):.4f}   agree_core = {np.mean(co):.4f}   "
          f"(24 trials)")
print("\nThe paper's §6 figure quotes the K=4 frontier number (~0.44).")
