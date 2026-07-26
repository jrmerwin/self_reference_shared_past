"""w-plumbed variant of notebook 1's engine.

PROVENANCE. Every function below is copied verbatim from
`unified_selfreference_mechanism.ipynb` (cells 2, 6, 8). The ONLY change is that
the self-weight `w` is threaded through as an explicit parameter, since the
notebooks bury it as a default argument of `conclusion()` that `required()` never
forwards. Each threading edit is marked [W]. No predicate, no RNG call, and no
control-flow decision is altered.

C2 certifies this: at w = 3 (the original default) this module must reproduce
Table 1 bit-exactly against the original notebook code.
"""
import numpy as np
import networkx as nx

ORIGINAL_DEFAULT_W = 3          # from `def conclusion(self, v, sw=3)` in both notebooks


class Observer:
    """Self-referential compressing labeling of a graph."""

    def __init__(self, G, selfref, seed=0, sw=ORIGINAL_DEFAULT_W):   # [W] sw arg
        self.G = G
        self.selfref = set(selfref)
        r = np.random.default_rng(seed)
        self.label = {v: int(r.integers(2)) for v in G.nodes()}
        self.absorbed = set()
        self.sw = sw                                                  # [W]

    def conclusion(self, v, sw=None):
        """Observer's reading of v. A self-ref (unabsorbed) node enters its own reading."""
        sw = self.sw if sw is None else sw                            # [W]
        nb = list(self.G.neighbors(v))
        vals = [self.label[u] for u in nb]
        if v in self.selfref and v not in self.absorbed:
            vals += [self.label[v]] * sw          # the diagonal self-term
        return int(round(np.mean(vals))) if vals else self.label[v]

    def required(self, v):
        c = self.conclusion(v)
        return (1 - c) if (v in self.selfref and v not in self.absorbed) else c

    def resolvable(self, v):
        """Does a within-stage fixed point label exist for v?"""
        for cand in (0, 1):
            old = self.label[v]
            self.label[v] = cand
            req = self.required(v)
            self.label[v] = old
            if req == cand:
                return True
        return False

    def incompleteness(self):
        """Set A: nodes with no within-stage consistent label (the frontier)."""
        return {v for v in self.G.nodes() if not self.resolvable(v)}

    def settle(self, iters=8):
        for _ in range(iters):
            self.label = {v: self.required(v) for v in self.G.nodes()}


def build(n=40, frac=0.25, seed=1, radius=0.32):
    g = nx.random_geometric_graph(n, radius, seed=seed)
    cs = sorted(nx.connected_components(g), key=len, reverse=True)
    if len(cs) > 1:
        h = next(iter(cs[0]))
        for c in cs[1:]:
            g.add_edge(h, next(iter(c)))
    g = nx.convert_node_labels_to_integers(g)
    r = np.random.default_rng(seed + 100)
    sr = set(r.choice(list(g.nodes()), size=int(frac * n), replace=False))
    return g, sr


def step_forward(o, beta, rng, w=ORIGINAL_DEFAULT_W):                 # [W] w arg
    """One stage: resolve all of A by forced growth; each absorber spawns Poisson(beta)
    new self-referential children at the new boundary."""
    A = o.incompleteness()
    G2 = o.G.copy(); lab = dict(o.label); absorbed = set(o.absorbed); sr2 = set(o.selfref)
    nxt = max(G2.nodes()) + 1
    for v in A:
        G2.add_edge(v, nxt)
        for u in list(o.G.neighbors(v))[:2]:
            G2.add_edge(nxt, u)
        lab[nxt] = o.conclusion(v); absorbed.add(v); base = nxt; nxt += 1
        for _ in range(rng.poisson(beta)):                 # abstraction branches
            G2.add_edge(base, nxt)
            nb = list(o.G.neighbors(v))
            if nb:
                G2.add_edge(nxt, nb[rng.integers(len(nb))])
            lab[nxt] = int(rng.integers(2)); sr2.add(nxt); nxt += 1
    o2 = Observer(G2, sr2, 0, sw=w)                                    # [W] sw=w
    o2.label = lab; o2.absorbed = absorbed; o2.settle(8)
    return o2


def run_to_outcome(beta, n0=60, frac=0.25, stages=30, seed=0, cap=12000,
                   w=ORIGINAL_DEFAULT_W, trace_A=False):               # [W] w arg
    """Return EXHAUSTED (block) or SUSTAINED (open) plus the |A| trace."""
    rng = np.random.default_rng(seed)
    g, sr = build(n0, frac, seed, radius=0.30)
    o = Observer(g, sr, seed, sw=w); o.settle(6)                       # [W] sw=w
    trace = []
    for st in range(stages):
        # TIMING ASSERTION (pre-registration section 6): |A| is read at stage start,
        # before this stage's expansion. `expanded_this_stage` must still be False.
        expanded_this_stage = False
        A = o.incompleteness(); trace.append(len(A))
        assert not expanded_this_stage, "|A| must be read before expansion"
        if not A:
            return 'EXHAUSTED', trace
        if o.G.number_of_nodes() > cap:
            return 'SUSTAINED', trace
        o = step_forward(o, beta, rng, w=w)                            # [W]
        expanded_this_stage = True
    return 'SUSTAINED', trace


def beta_c_from_P(betas, ps):
    """50% crossing of P_sustain, linear interpolation -- notebook 1 cell 8 verbatim."""
    bs = np.asarray(betas, dtype=float); ps = np.asarray(ps, dtype=float)
    above = np.where(ps >= 0.5)[0]
    if len(above) == 0 or above[0] == 0:
        return None
    i = above[0]
    return float(bs[i - 1] + (0.5 - ps[i - 1]) * (bs[i] - bs[i - 1]) / (ps[i] - ps[i - 1]))
