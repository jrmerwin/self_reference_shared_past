"""
Engine for the "Objectivity of the Growth Set" campaign.

PROVENANCE (P0.1 discipline: read, do not reimplement)
-----------------------------------------------------
All resolvability logic below is COPIED VERBATIM from the DEU_SR notebooks.
The only edits are the four marked [MOD-n] blocks, each of which is declared
and justified in preflight_report.md. No predicate logic was rewritten.

  nb1 = DEU_SR/unified_selfreference_mechanism.ipynb   (code cells 2, 4, 6)
  nb2 = DEU_SR/shared_past_mechanism.ipynb             (code cells 2, 4)

Observer.conclusion / .required / .settle / build()   <- nb2 cell 2 verbatim
Observer.resolvable / .incompleteness                 <- nb1 cell 2 verbatim
                                                         (nb2 HAS NO resolvability
                                                          test; see preflight §A)
beta-branching in step                                <- nb1 cell 6 step_forward
shared-past freeze + absorb                           <- nb2 cell 4 run()
"""
import numpy as np
import networkx as nx
from collections import defaultdict


class Observer:
    """nb2 cell 2 Observer, with nb1's resolvable()/incompleteness() grafted on."""

    # [MOD-1] added `sw` ctor arg so the self-weight can be swept. nb1/nb2 both
    # hardcode sw=3 as a *default argument of conclusion()* which `required()`
    # never forwards, so w is unreachable from outside without this. Default 3
    # reproduces the notebooks bit-for-bit (asserted in preflight P0.1c).
    def __init__(self, G, selfref, seed=0, sw=3):
        self.G = G
        self.selfref = set(selfref)
        r = np.random.default_rng(seed)
        self.label = {v: int(r.integers(2)) for v in G.nodes()}
        self.absorbed = set()
        self.frozen = {}                      # frozen[v] = fixed past value
        self.sw = sw                          # [MOD-1]

    def conclusion(self, v, sw=None):
        # verbatim nb2 cell 2, except the [MOD-1] default-resolution line.
        sw = self.sw if sw is None else sw    # [MOD-1]
        nb = list(self.G.neighbors(v))
        vals = [self.label[u] for u in nb]
        if v in self.selfref and v not in self.absorbed:
            vals += [self.label[v]] * sw
        return int(round(np.mean(vals))) if vals else self.label[v]

    def required(self, v):
        # verbatim nb2 cell 2 (nb2 adds the frozen short-circuit that nb1 lacks)
        if v in self.frozen:
            return self.frozen[v]             # the past is fixed
        c = self.conclusion(v)
        return (1 - c) if (v in self.selfref and v not in self.absorbed) else c

    def resolvable(self, v):
        """Does a within-stage fixed point label exist for v?"""
        # verbatim nb1 cell 2
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
        # verbatim nb1 cell 2
        return {v for v in self.G.nodes() if not self.resolvable(v)}

    def settle(self, it=10):
        # verbatim nb2 cell 2
        for _ in range(it):
            self.label = {v: (self.frozen[v] if v in self.frozen else self.required(v))
                          for v in self.G.nodes()}


def build(n=60, frac=0.25, seed=1, radius=0.30):
    """verbatim nb1 cell 2 build() (identical to nb2's but with the radius arg)."""
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


def agree_on(observers, nodeset):
    """Fraction of nodes in nodeset where ALL observers carry the same label."""
    # verbatim nb2 cell 2 -- used only for F4 (label agreement, the paper's 0.44)
    if not nodeset:
        return None
    nl = defaultdict(list)
    for o in observers:
        for v in nodeset:
            nl[v].append(o.label.get(v))
    shared = [v for v in nodeset if len([x for x in nl[v] if x is not None]) >= 2]
    if not shared:
        return None
    return sum(1 for v in shared if len(set(nl[v])) == 1) / len(shared)


# ---------------------------------------------------------------------------
# Multi-observer shared-history run loop.
#   structure  = nb2 cell 4 run()
#   [MOD-2] beta-branching lifted from nb1 cell 6 step_forward() (the pre-reg
#           fixes beta=1.3; nb2's run() has no beta at all).
#   [MOD-3] per-node measurement emitted at STAGE START, before any expansion
#           move of that stage is applied (pre-reg §3 timing).
#   [MOD-4] K=2 observers carry private RNGs so beta-children get private
#           labels (nb1 behaviour); absorbers get label 0 for every observer
#           (nb2 behaviour).
# ---------------------------------------------------------------------------
def run_measured(seed, w, beta=1.3, n0=60, frac=0.25, stages=14,
                 radius=0.30, node_cap=4000, emit=True):
    """Two observers on a shared, forced history. Returns (rows, summary).

    rows: long format, one dict per SELF-REFERENTIAL node per stage, measured
          at stage start before expansion.
    """
    g, sr = build(n0, frac, seed, radius=radius)
    G = g
    sr = set(sr)

    obs = [Observer(G, sr, seed=seed * 100 + k, sw=w) for k in range(2)]
    rngs = [np.random.default_rng(seed * 977 + 13 * k + 1) for k in range(2)]
    spawn_rng = np.random.default_rng(seed * 31 + 7)   # structural, shared
    for o in obs:
        o.settle(10)

    past = set()
    gen = {}
    anchor = min(sr)                                   # shared seed (common origin)
    for o in obs:
        o.absorbed.add(anchor)
        o.frozen[anchor] = 0
    past.add(anchor)
    gen[anchor] = 0

    rows = []
    summary = {"stage": [], "agree_frontier": [], "agree_past": [], "agree_core": [],
               "n_nodes": [], "jaccard_A": [], "concordance": [],
               "symdiff_nodes": [], "trunk_common": []}

    for st in range(stages):
        frontier = set(sr) - past
        core = {v for v, gg in gen.items() if gg <= 1}

        # ---- [MOD-3] MEASURE FIRST. No expansion has been applied this stage.
        assert all(o.G is G for o in obs), "observers must share the graph instance"
        A = [o.incompleteness() for o in obs]
        srlive = [v for v in sr if v in G]
        frozen_ref = obs[0].frozen                     # freeze is shared by construction

        for v in srlive:
            nbrs = list(G.neighbors(v))
            d = len(nbrs)
            nfroz = sum(1 for u in nbrs if u in frozen_ref)
            rows.append({
                "seed": seed, "stage": st, "node_id": int(v),
                "d_live_at_stage_start": d,
                "w": w,
                "omega_w_over_d": (w / d) if d else np.nan,
                "phi_frozen_frac_at_stage_start": (nfroz / d) if d else np.nan,
                "resolvable_A_at_stage_start": int(v not in A[0]),
                "resolvable_B_at_stage_start": int(v not in A[1]),
                "frozen_self": int(v in frozen_ref),
                # labels carried at the same instant, for F4's per-node label
                # agreement inside the (phi, omega) cell
                "label_A_at_stage_start": int(obs[0].label[v]),
                "label_B_at_stage_start": int(obs[1].label[v]),
                "in_structural_frontier": int(v in frontier),
                "beta": beta,
            })

        srset = set(srlive)
        AA, AB = A[0] & srset, A[1] & srset
        uni = AA | AB
        jac = (len(AA & AB) / len(uni)) if uni else np.nan
        conc = (sum(1 for v in srlive if (v in AA) == (v in AB)) / len(srlive)) if srlive else np.nan

        summary["stage"].append(st)
        summary["agree_frontier"].append(agree_on(obs, frontier) or np.nan)
        summary["agree_past"].append(agree_on(obs, past) or np.nan)
        summary["agree_core"].append(agree_on(obs, core) or np.nan)
        summary["n_nodes"].append(G.number_of_nodes())
        summary["jaccard_A"].append(jac)
        summary["concordance"].append(conc)
        # F5: with a single shared graph these are structurally pinned; recorded anyway.
        summary["symdiff_nodes"].append(
            len(set(obs[0].G.nodes()) ^ set(obs[1].G.nodes())))
        summary["trunk_common"].append(
            int(obs[0].frozen == obs[1].frozen))

        if not frontier or G.number_of_nodes() > node_cap:
            break

        # ---- expansion (nb2 cell 4) ------------------------------------
        adjacent = [v for v in frontier if any(u in past for u in G.neighbors(v))]
        to_absorb = set(adjacent) if adjacent else set(list(frontier)[:1])
        nxt = max(G.nodes()) + 1
        new_edges = []
        new_children = []
        for v in to_absorb:
            for u in list(G.neighbors(v))[:2]:
                new_edges.append((nxt, u))
            new_edges.append((v, nxt))
            base = nxt
            nxt += 1
            # [MOD-2] beta-branching, nb1 cell 6 step_forward
            for _ in range(spawn_rng.poisson(beta)):
                new_edges.append((base, nxt))
                nb = list(G.neighbors(v))
                if nb:
                    new_edges.append((nxt, nb[spawn_rng.integers(len(nb))]))
                new_children.append(nxt)
                nxt += 1
        G.add_edges_from(new_edges)
        sr |= set(new_children)

        # SHARED FREEZE: one value per node, for all observers (nb2 cell 4)
        shared_vals = {}
        ref = obs[0]
        for v in to_absorb:
            pn = [ref.frozen[u] for u in G.neighbors(v) if u in ref.frozen]
            shared_vals[v] = int(round(np.mean(pn))) if pn else 0

        for k, o in enumerate(obs):
            o.G = G
            o.selfref |= set(new_children)
            # nb2's backfill runs FIRST: its `range(max(label)+1, ...)` assumes the
            # new ids are one contiguous block above the old max, which holds only
            # before any child label is written. Then [MOD-4] overwrites children.
            for nn in range(max(o.label) + 1, max(G.nodes()) + 1):
                if nn not in o.label:
                    o.label[nn] = 0
            for c in new_children:                      # [MOD-4] private labels
                o.label[c] = int(rngs[k].integers(2))
            for v in to_absorb:
                o.absorbed.add(v)
                o.frozen[v] = shared_vals[v]
            o.settle(10)

        for v in to_absorb:
            gen[v] = st + 1
        past |= to_absorb

    return (rows if emit else []), summary


# ---------------------------------------------------------------------------
# Isolated single-node probe: used by P0.2/P0.3 to interrogate the REPO's
# resolvable() at an exact (d, S, w) configuration. Star graph, centre = v.
# ---------------------------------------------------------------------------
def probe_resolvable(d, S, w, frozen_neighbors=False, seed=0, self_label=0):
    """Build a node of degree d with neighbour label sum S, call repo resolvable()."""
    g = nx.star_graph(d)                      # node 0 = centre, 1..d = leaves
    o = Observer(g, {0}, seed=seed, sw=w)
    o.label = {0: self_label}
    for i in range(1, d + 1):
        o.label[i] = 1 if i <= S else 0
    if frozen_neighbors:
        for i in range(1, d + 1):
            o.frozen[i] = o.label[i]
    return o.resolvable(0), o
