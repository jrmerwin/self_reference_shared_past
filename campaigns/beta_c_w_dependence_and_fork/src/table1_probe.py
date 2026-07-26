"""Run notebook 1's ORIGINAL Table-1 sweep and report P_sustain per beta.

Used to determine whether the mismatch between the notebook and the paper's
Table 1 is an environment artifact (networkx's random_geometric_graph changing
between versions) or a real discrepancy. Run under several interpreters.
"""
import json, os, sys, platform
import numpy as np, networkx as nx, scipy

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
nb = json.load(open(os.path.join(REPO, "unified_selfreference_mechanism.ipynb"),
                    encoding="utf-8"))
ns = {}
for idx, cut in [(2, "# Demonstrate a genuine diagonal"),
                 (6, "# Show the frontier advancing"),
                 (8, "betas = np.round")]:
    exec(compile("".join(nb["cells"][idx]["source"]).split(cut)[0], f"c{idx}", "exec"), ns)

print(f"python {platform.python_version()}  numpy {np.__version__}  "
      f"networkx {nx.__version__}  scipy {scipy.__version__}")

# substrate fingerprint: does the graph itself differ between environments?
g0, sr0 = ns["build"](60, 0.25, 0, radius=0.30)
print(f"  substrate seed 0: nodes={g0.number_of_nodes()} edges={g0.number_of_edges()} "
      f"degsum={sum(d for _,d in g0.degree())} sr_min={min(sr0)} sr_sum={sum(sr0)}")

PAPER = {0.6: 0.00, 0.7: 0.00, 0.8: 0.00, 0.9: 0.08, 1.0: 0.17, 1.1: 0.58,
         1.2: 0.75, 1.3: 0.92, 1.4: 0.92, 1.5: 0.92, 1.6: 0.92}
betas = np.round(np.arange(0.6, 1.61, 0.1), 2)
P = {}
print(f"  {'beta':>5} {'n_sus':>7} {'P':>6} {'paper':>7} {'match':>6}")
for beta in betas:
    outs = [ns["run_to_outcome"](beta, seed=s)[0] for s in range(12)]
    n = sum(x == "SUSTAINED" for x in outs)
    P[float(beta)] = n / 12
    m = round(n / 12, 2) == PAPER[float(beta)]
    print(f"  {beta:>5.1f} {n:>5}/12 {n/12:>6.2f} {PAPER[float(beta)]:>7.2f} {str(m):>6}")

bs = np.array(list(P.keys())); ps = np.array(list(P.values()))
above = np.where(ps >= 0.5)[0]; i = above[0]
bc = bs[i-1] + (0.5 - ps[i-1]) * (bs[i] - bs[i-1]) / (ps[i] - ps[i-1])
print(f"  beta_c = {bc:.4f}   (notebook stored 1.075, paper says ~1.08)")
print(f"  reproduces Table 1 exactly: {all(round(P[float(b)],2)==PAPER[float(b)] for b in betas)}")
