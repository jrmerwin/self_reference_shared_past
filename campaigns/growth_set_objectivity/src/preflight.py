"""Blocking preflight P0.1 / P0.2 / P0.3. Writes preflight_report.md."""
import json, sys, os
import numpy as np
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import Observer, build, probe_resolvable

NB1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                   "unified_selfreference_mechanism.ipynb")
OUT = {}

# ---------------------------------------------------------------- P0.1
print("=" * 70); print("P0.1  rounding convention")
r = {}
r["round(np.float64(0.5))"] = repr(round(np.float64(0.5)))
r["round(np.float64(1.5))"] = repr(round(np.float64(1.5)))
r["round(np.float64(2.5))"] = repr(round(np.float64(2.5)))
r["int(round(np.mean([0,1])))"] = repr(int(round(np.mean([0, 1]))))
r["int(round(np.mean([0,1,1,1,0,0])))"] = repr(int(round(np.mean([0, 1, 1, 1, 0, 0]))))
r["int(round(np.mean([1,1,1,0,0,0,0,0,1,1,1,1])))"] = repr(
    int(round(np.mean([1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]))))
r["type(np.mean([0,1]))"] = type(np.mean([0, 1])).__name__
r["type(round(np.mean([0,1])))"] = type(round(np.mean([0, 1]))).__name__
for k, v in r.items():
    print(f"   {k:45s} = {v}")
half_to_even = (round(np.float64(0.5)) == 0 and round(np.float64(1.5)) == 2
                and round(np.float64(2.5)) == 2)
print(f"   -> banker's / half-to-even: {half_to_even}")
OUT["P0.1"] = {"probes": r, "half_to_even": bool(half_to_even)}

# P0.1c: bit-exactness of [MOD-1] against the ORIGINAL notebook class.
print("\nP0.1c  [MOD-1] bit-exactness vs the original nb1 Observer")
nb = json.load(open(NB1, encoding="utf-8"))
src = "".join(nb["cells"][2]["source"])
src = src.split("# Demonstrate a genuine diagonal")[0]        # defs only
ns = {}
exec(compile(src, "nb1_cell2", "exec"), ns)
OrigObserver, orig_build = ns["Observer"], ns["build"]

mismatch = 0; checked = 0
for seed in range(40):
    g, sr = orig_build(40, 0.25, seed)
    a = OrigObserver(g, sr, seed); a.settle(8)
    b = Observer(g, sr, seed, sw=3); b.settle(8)      # our sw default
    b.label = dict(a.label)                           # same label state
    for v in g.nodes():
        checked += 1
        if a.resolvable(v) != b.resolvable(v):
            mismatch += 1
print(f"   node-verdicts compared: {checked}   mismatches: {mismatch}")
OUT["P0.1c"] = {"checked": checked, "mismatches": mismatch}
assert mismatch == 0, "[MOD-1] is not bit-exact at sw=3 -- STOP"

# ---------------------------------------------------------------- P0.2
print("\n" + "=" * 70); print("P0.2  brute-force validation of the band")


def analytic_unresolvable(d, S, w):
    """Pre-registration §1: 2S < d+w  AND  2S >= d-w."""
    return (2 * S < d + w) and (2 * S >= d - w)


rowsP2 = []
disagree = []
for d in range(3, 21):
    for S in range(0, d + 1):
        for w in range(1, 26):
            res, _ = probe_resolvable(d, S, w)
            code_unres = not res
            ana_unres = analytic_unresolvable(d, S, w)
            rowsP2.append((d, S, w, code_unres, ana_unres))
            if code_unres != ana_unres:
                disagree.append({
                    "d": d, "S": S, "w": w,
                    "code_unresolvable": bool(code_unres),
                    "analytic_unresolvable": bool(ana_unres),
                    "two_S_minus_d_plus_w": 2 * S - (d + w),   # 0 => upper tie
                    "two_S_minus_d_minus_w": 2 * S - (d - w),  # 0 => lower tie
                })
print(f"   configurations tested: {len(rowsP2)}")
print(f"   disagreements:         {len(disagree)}")
upper_tie = [x for x in disagree if x["two_S_minus_d_plus_w"] == 0]
lower_tie = [x for x in disagree if x["two_S_minus_d_minus_w"] == 0]
other = [x for x in disagree
         if x["two_S_minus_d_plus_w"] != 0 and x["two_S_minus_d_minus_w"] != 0]
print(f"     on upper tie 2S == d+w : {len(upper_tie)}")
print(f"     on lower tie 2S == d-w : {len(lower_tie)}")
print(f"     NOT on any tie         : {len(other)}")
if other:
    print("   !! non-tie disagreements -- campaign VOID:")
    for x in other[:20]:
        print("     ", x)

# corrected condition under half-to-even
def analytic_corrected(d, S, w):
    return (2 * S <= d + w) and (2 * S > d - w)


bad2 = [(d, S, w) for (d, S, w, cu, au) in rowsP2 if cu != analytic_corrected(d, S, w)]
print(f"   disagreements vs half-to-even-corrected condition "
      f"(2S <= d+w AND 2S > d-w): {len(bad2)}")
OUT["P0.2"] = {"n_configs": len(rowsP2), "n_disagree": len(disagree),
               "upper_tie": len(upper_tie), "lower_tie": len(lower_tie),
               "non_tie": len(other),
               "n_disagree_corrected": len(bad2),
               "examples": disagree[:12]}

# w >= d forces unresolvability?  (§1 consequence, to be checked not presumed)
viol = [(d, S, w) for (d, S, w, cu, au) in rowsP2 if w >= d and not cu]
print(f"   §1 claim 'w >= d forces unresolvable' -- violations: {len(viol)}"
      + (f"   e.g. {viol[:6]}" if viol else ""))
OUT["P0.2_wged"] = {"violations": len(viol), "examples": viol[:12]}

# ---------------------------------------------------------------- P0.3
print("\n" + "=" * 70); print("P0.3  frozen-neighbourhood identity")
fails = []; n_checked = 0
for d in range(3, 21):
    for S in range(0, d + 1):
        for w in range(1, 26):
            verdicts = []
            for obs_seed in (0, 12345):
                g = nx.star_graph(d)
                o = Observer(g, {0}, seed=obs_seed, sw=w)   # private random labels
                for i in range(1, d + 1):
                    o.frozen[i] = 1 if i <= S else 0        # SHARED frozen past
                o.settle(10)                                # leaves take frozen vals
                verdicts.append(o.resolvable(0))
            n_checked += 1
            if verdicts[0] != verdicts[1]:
                fails.append((d, S, w, verdicts))
conc = 1.0 if not fails else 1.0 - len(fails) / n_checked
print(f"   configurations: {n_checked}   concordance = {conc:.4f}   failures: {len(fails)}")
if fails:
    print("   !! freeze bookkeeping bug:", fails[:10])
OUT["P0.3"] = {"n_configs": n_checked, "concordance": conc, "failures": len(fails)}

# ---------------------------------------------------------------- substrate
print("\n" + "=" * 70); print("substrate degree stats (n0=60, radius=0.30)")
degs = []
for s in range(32):
    g, _ = build(60, 0.25, s, radius=0.30)
    degs += [dd for _, dd in g.degree()]
degs = np.array(degs)
print(f"   mean d = {degs.mean():.2f}   median = {np.median(degs):.0f}   "
      f"max = {degs.max()}   p99 = {np.percentile(degs,99):.0f}")
OUT["substrate"] = {"mean_d": float(degs.mean()), "max_d": int(degs.max()),
                    "median_d": float(np.median(degs)),
                    "p99_d": float(np.percentile(degs, 99))}

json.dump(OUT, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "preflight_results.json"), "w"), indent=2)
print("\nwrote preflight_results.json")
