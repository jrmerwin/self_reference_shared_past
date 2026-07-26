"""R4 -- substrate divergence per F5.

>=16 seeds, >=20 stages, at a w chosen from R1 in the degraded regime.
Measures, per stage: node-set symmetric difference between the two observers'
substrates, whether the frozen trunk stays common, and 1-J.

Also records |A_A symdiff A_B| -- the disagreement that WOULD drive divergent
expansion if expansion were A-driven. That column is a counterfactual diagnostic,
not a pre-registered measure; it is here to quantify how much causal signal
notebook 2's structural expansion discards.
"""
import csv, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import build, Observer, agree_on

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
W_STAR = int(sys.argv[1]) if len(sys.argv) > 1 else 12
SEEDS = list(range(16))
STAGES = 20
BETA = 1.3

COLS = ["seed", "w", "stage", "n_nodes_A", "n_nodes_B", "symdiff_nodes_AB",
        "trunk_common", "jaccard_A", "one_minus_J", "concordance",
        "counterfactual_A_symdiff_size", "shared_graph_object"]


def one(seed, w):
    g, sr = build(60, 0.25, seed, radius=0.30)
    G = g; sr = set(sr)
    obs = [Observer(G, sr, seed=seed * 100 + k, sw=w) for k in range(2)]
    rngs = [np.random.default_rng(seed * 977 + 13 * k + 1) for k in range(2)]
    spawn = np.random.default_rng(seed * 31 + 7)
    for o in obs:
        o.settle(10)
    past = set(); anchor = min(sr)
    for o in obs:
        o.absorbed.add(anchor); o.frozen[anchor] = 0
    past.add(anchor)

    out = []
    for st in range(STAGES):
        frontier = set(sr) - past
        A = [o.incompleteness() for o in obs]
        srlive = [v for v in sr if v in G]
        srset = set(srlive)
        AA, AB = A[0] & srset, A[1] & srset
        uni = AA | AB
        jac = (len(AA & AB) / len(uni)) if uni else np.nan
        conc = (sum(1 for v in srlive if (v in AA) == (v in AB)) / len(srlive)) if srlive else np.nan
        out.append({
            "seed": seed, "w": w, "stage": st,
            "n_nodes_A": obs[0].G.number_of_nodes(),
            "n_nodes_B": obs[1].G.number_of_nodes(),
            "symdiff_nodes_AB": len(set(obs[0].G.nodes()) ^ set(obs[1].G.nodes())),
            "trunk_common": int(obs[0].frozen == obs[1].frozen),
            "jaccard_A": jac,
            "one_minus_J": (1 - jac) if jac == jac else np.nan,
            "concordance": conc,
            "counterfactual_A_symdiff_size": len(AA ^ AB),
            "shared_graph_object": int(obs[0].G is obs[1].G),
        })
        if not frontier or G.number_of_nodes() > 4000:
            break

        adjacent = [v for v in frontier if any(u in past for u in G.neighbors(v))]
        to_abs = set(adjacent) if adjacent else set(list(frontier)[:1])
        nxt = max(G.nodes()) + 1; ne = []; kids = []
        for v in to_abs:
            for u in list(G.neighbors(v))[:2]:
                ne.append((nxt, u))
            ne.append((v, nxt)); base = nxt; nxt += 1
            for _ in range(spawn.poisson(BETA)):
                ne.append((base, nxt))
                nb = list(G.neighbors(v))
                if nb:
                    ne.append((nxt, nb[spawn.integers(len(nb))]))
                kids.append(nxt); nxt += 1
        G.add_edges_from(ne); sr |= set(kids)

        sv = {}; ref = obs[0]
        for v in to_abs:
            pn = [ref.frozen[u] for u in G.neighbors(v) if u in ref.frozen]
            sv[v] = int(round(np.mean(pn))) if pn else 0
        for k, o in enumerate(obs):
            o.G = G; o.selfref |= set(kids)
            for nn in range(max(o.label) + 1, max(G.nodes()) + 1):
                if nn not in o.label:
                    o.label[nn] = 0
            for c in kids:
                o.label[c] = int(rngs[k].integers(2))
            for v in to_abs:
                o.absorbed.add(v); o.frozen[v] = sv[v]
            o.settle(10)
        past |= to_abs
    return out


rows = []
for s in SEEDS:
    rows += one(s, W_STAR)
p = os.path.join(ROOT, f"rows_R4_w{W_STAR}.csv")
with open(p, "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=COLS); wr.writeheader(); wr.writerows(rows)

import pandas as pd
d = pd.DataFrame(rows)
print(f"R4 at w={W_STAR}, {len(SEEDS)} seeds, {STAGES} stages -> {len(d)} stage-rows")
print(f"  mean concordance           : {d.concordance.mean():.4f}")
print(f"  max symdiff_nodes_AB       : {d.symdiff_nodes_AB.max()}")
print(f"  trunk_common always true   : {bool(d.trunk_common.all())}")
print(f"  shared graph object always : {bool(d.shared_graph_object.all())}")
print(f"  stages with A_A != A_B     : {(d.counterfactual_A_symdiff_size>0).sum()} / {len(d)}")
print(f"  mean |A_A sym A_B| when >0 : "
      f"{d.loc[d.counterfactual_A_symdiff_size>0,'counterfactual_A_symdiff_size'].mean():.2f}")
sub = d.dropna(subset=["one_minus_J"])
if len(sub) > 2 and sub.symdiff_nodes_AB.std() > 0:
    print(f"  corr(symdiff, 1-J)         : {sub.symdiff_nodes_AB.corr(sub.one_minus_J):.4f}")
else:
    print("  corr(symdiff, 1-J)         : UNDEFINED (symdiff has zero variance)")
print(f"wrote {p}")
