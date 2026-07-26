"""DIAGNOSTIC ONLY -- characterise the Table 1 gap. Not a certification, not a fit.

C2 established that notebook 1, run unmodified in two independent environments,
deterministically yields P_sustain = 0.25 / 0.83 / 0.83 at beta = 1.0 / 1.3 / 1.4
where the paper's Table 1 reports 0.17 / 0.92 / 0.92.

This probes a small, pre-listed set of plausible configuration differences to see
whether any reproduces Table 1. It is reported as a diagnostic. If one matches,
that identifies the configuration the table came from; if none does, that is
recorded and nothing is tuned further. No parameter found here is carried into any
downstream run -- C2 is blocking regardless of the outcome.
"""
import json, os, sys
import numpy as np, networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from engine_w import Observer, build, step_forward

PAPER = {0.6: 0.00, 0.7: 0.00, 0.8: 0.00, 0.9: 0.08, 1.0: 0.17, 1.1: 0.58,
         1.2: 0.75, 1.3: 0.92, 1.4: 0.92, 1.5: 0.92, 1.6: 0.92}
BETAS = [round(b, 2) for b in np.arange(0.6, 1.61, 0.1)]


def run_to_outcome(beta, seed, radius=0.30, settle=6, stages=30, cap=12000,
                   n0=60, frac=0.25, w=3):
    rng = np.random.default_rng(seed)
    g, sr = build(n0, frac, seed, radius=radius)
    o = Observer(g, sr, seed, sw=w); o.settle(settle)
    for st in range(stages):
        A = o.incompleteness()
        if not A:
            return 'EXHAUSTED'
        if o.G.number_of_nodes() > cap:
            return 'SUSTAINED'
        o = step_forward(o, beta, rng, w=w)
    return 'SUSTAINED'


VARIANTS = [
    ("as committed (seeds 0-11, r=0.30, settle=6)", dict(), range(0, 12)),
    ("seeds 1-12",                                  dict(), range(1, 13)),
    ("radius 0.32 (build's own default)",           dict(radius=0.32), range(0, 12)),
    ("settle=8 (matches step_forward's settle)",    dict(settle=8), range(0, 12)),
    ("stage budget 25",                             dict(stages=25), range(0, 12)),
]

results = []
for name, kw, seeds in VARIANTS:
    P = {}
    for beta in BETAS:
        outs = [run_to_outcome(beta, s, **kw) for s in seeds]
        P[beta] = sum(o == 'SUSTAINED' for o in outs) / len(list(seeds))
    exact = all(round(P[b], 2) == PAPER[b] for b in BETAS)
    diffs = [b for b in BETAS if round(P[b], 2) != PAPER[b]]
    ps = np.array([P[b] for b in BETAS]); bs = np.array(BETAS, dtype=float)
    ab = np.where(ps >= 0.5)[0]
    bc = (bs[ab[0]-1] + (0.5 - ps[ab[0]-1]) * (bs[ab[0]] - bs[ab[0]-1]) /
          (ps[ab[0]] - ps[ab[0]-1])) if len(ab) and ab[0] > 0 else float('nan')
    results.append({"variant": name, "P": P, "reproduces_table1": exact,
                    "mismatched_betas": diffs, "beta_c": float(bc)})
    print(f"{name:<48} exact={str(exact):<5} beta_c={bc:.4f}  "
          f"mismatch at beta={diffs}")
    print("      " + " ".join(f"{b}:{P[b]:.2f}" for b in BETAS))

json.dump(results, open(os.path.join(HERE, "..", "diag_table1.json"), "w"),
          indent=2, default=str)
print("\nany variant reproducing Table 1 exactly:",
      any(r["reproduces_table1"] for r in results))
