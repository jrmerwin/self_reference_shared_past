"""R2 / R3 and the F1-F5 adjudication. Writes figures + decision_results.json.

Fixed measure definitions (§3, §7 -- never switched below):
  concordance = fraction of SELF-REFERENTIAL nodes on which A and B return the
                same resolvability verdict, measured at STAGE START.
  A_X         = {v self-referential : resolvable_X == 0} at stage start.
  Jaccard J   = |A_A n A_B| / |A_A u A_B| over self-referential nodes.
  omega       = w / d(v), live degree at stage start.
  phi         = frozen fraction of v's neighbourhood at stage start.

F2 fit model (declared here, before fitting):
  4-parameter logistic  p(x) = lo + (hi-lo) / (1 + exp(-k (x - x0))),  lo,hi in [0,1]
  normalized slope  ==  k * sigma(x)   (sigma = std of x over the fitted rows;
                                        dimensionless, comparable across coords)
  residual          ==  RMSE of the fit against bin means, bins with n >= 30 only
"""
import json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OM, PHI = "omega_w_over_d", "phi_frozen_frac_at_stage_start"
MIN_N = 30
R = {}

df = pd.read_csv(os.path.join(ROOT, "rows_R1.csv"))
sm = pd.read_csv(os.path.join(ROOT, "summary_R1.csv"))
df["conc"] = (df.resolvable_A_at_stage_start == df.resolvable_B_at_stage_start).astype(int)
df["lblagree"] = (df.label_A_at_stage_start == df.label_B_at_stage_start).astype(int)
df["unres_A"] = 1 - df.resolvable_A_at_stage_start
print(f"rows_R1: {len(df):,}   seeds={df.seed.nunique()}  w={df.w.min()}..{df.w.max()}  "
      f"stages={df.stage.min()}..{df.stage.max()}")
R["dataset"] = {"n_rows": int(len(df)), "n_seeds": int(df.seed.nunique()),
                "w_min": int(df.w.min()), "w_max": int(df.w.max()),
                "n_stages": int(df.stage.nunique())}


def logistic4(x, lo, hi, k, x0):
    return lo + (hi - lo) / (1.0 + np.exp(-k * (x - x0)))


def binmeans(d, xcol, edges):
    b = pd.cut(d[xcol], edges)
    g = d.groupby(b, observed=True).agg(n=("conc", "size"), y=("conc", "mean"))
    g = g[g.n >= MIN_N].copy()
    g["x"] = [iv.mid for iv in g.index]
    return g


def fit(d, xcol, edges, label):
    g = binmeans(d, xcol, edges)
    if len(g) < 5:
        return {"label": label, "ok": False, "reason": f"only {len(g)} usable bins"}
    x, y, n = g.x.values, g.y.values, g.n.values
    sig = float(d[xcol].std())
    p0 = [y.min(), y.max(), 5.0 / max(sig, 1e-9), float(np.median(x))]
    try:
        popt, _ = curve_fit(logistic4, x, y, p0=p0, maxfev=200000,
                            bounds=([0, 0, -1e4, x.min() - 5 * sig],
                                    [1, 1, 1e4, x.max() + 5 * sig]))
    except Exception as e:
        return {"label": label, "ok": False, "reason": repr(e)}
    pred = logistic4(x, *popt)
    rmse = float(np.sqrt(np.mean((y - pred) ** 2)))
    ss = float(1 - np.sum((y - pred) ** 2) / max(np.sum((y - y.mean()) ** 2), 1e-12))
    lo, hi, k, x0 = popt
    # monotonicity of the observed bin means (F2 assumes a transition, not a U)
    dy = np.diff(y)
    mono = float(np.sum(np.abs(dy[dy > 0])) / max(np.sum(np.abs(dy)), 1e-12))
    return {"label": label, "ok": True, "lo": float(lo), "hi": float(hi),
            "k": float(k), "x0": float(x0), "sigma_x": sig,
            "normalized_slope": float(k * sig), "rmse": rmse, "r2": ss,
            "n_bins": int(len(g)), "frac_upward_variation": mono,
            "bins": [{"x": float(a), "y": float(b), "n": int(c)}
                     for a, b, c in zip(x, y, n)]}


OM_EDGES = np.arange(0, 4.21, 0.2)
W_EDGES = np.arange(0.5, 50.6, 2.0)

# ---------------------------------------------------------------- F1
print("\n" + "=" * 72); print("F1  concordance vs omega")
hi_bin = df[(df[OM] >= 1.0) & (df[OM] <= 1.5)]
lo_bin = df[(df[OM] >= 0.0) & (df[OM] <= 0.4) & (df[PHI] < 0.25)]
f1a, f1b = hi_bin.conc.mean(), lo_bin.conc.mean()
print(f"   omega in [1.0,1.5]                  : conc = {f1a:.4f}  (n={len(hi_bin):,})   "
      f"target >= 0.98 -> {'PASS' if f1a >= 0.98 else 'FAIL'}")
print(f"   omega in [0,0.4] & phi<0.25         : conc = {f1b:.4f}  (n={len(lo_bin):,})   "
      f"target <= 0.80 -> {'PASS' if f1b <= 0.80 else 'FAIL'}")
# the same two cells with Jaccard-style sensitivity (preflight B2)
for nm, d_ in (("omega[1.0,1.5]", hi_bin), ("omega[0,0.4],phi<0.25", lo_bin)):
    uA, uB = d_.unres_A.sum(), (1 - d_.resolvable_B_at_stage_start).sum()
    both = ((d_.unres_A == 1) & (d_.resolvable_B_at_stage_start == 0)).sum()
    uni = uA + uB - both
    print(f"     [{nm}] mean |A| density: A={uA/len(d_):.4f} B={uB/len(d_):.4f}  "
          f"pooled J={both/uni if uni else float('nan'):.4f}")
R["F1"] = {"conc_omega_1_0_to_1_5": float(f1a), "n_hi": int(len(hi_bin)),
           "conc_omega_0_to_0_4_phi_lt_0_25": float(f1b), "n_lo": int(len(lo_bin)),
           "pass_hi": bool(f1a >= 0.98), "pass_lo": bool(f1b <= 0.80)}

# ---------------------------------------------------------------- F2
print("\n" + "=" * 72); print("F2  sharpness: omega vs w")
fo = fit(df, OM, OM_EDGES, "omega")
fw = fit(df, "w", W_EDGES, "w")
for f in (fo, fw):
    if f["ok"]:
        print(f"   {f['label']:6s}: k={f['k']:9.4f}  sigma={f['sigma_x']:7.4f}  "
              f"norm_slope={f['normalized_slope']:9.4f}  x0={f['x0']:7.4f}  "
              f"RMSE={f['rmse']:.5f}  R2={f['r2']:.4f}  bins={f['n_bins']}  "
              f"upward_frac={f['frac_upward_variation']:.3f}")
    else:
        print(f"   {f['label']:6s}: FIT FAILED -- {f['reason']}")
f2_slope = fo["ok"] and fw["ok"] and abs(fo["normalized_slope"]) > abs(fw["normalized_slope"])
f2_resid = fo["ok"] and fw["ok"] and fo["rmse"] < fw["rmse"]
print(f"   steeper normalized slope in omega : {f2_slope}")
print(f"   lower residual in omega           : {f2_resid}")
print(f"   F2 -> {'PASS' if (f2_slope and f2_resid) else 'FAIL'}")
R["F2"] = {"omega": fo, "w": fw, "steeper_in_omega": bool(f2_slope),
           "lower_residual_in_omega": bool(f2_resid),
           "pass": bool(f2_slope and f2_resid)}

# ---------------------------------------------------------------- F3
print("\n" + "=" * 72); print("F3  control: phi == 1.0")
d1 = df[df[PHI] >= 1.0]
if len(d1):
    c3 = d1.conc.mean()
    print(f"   n={len(d1):,}  concordance={c3:.6f}  -> {'PASS' if c3 == 1.0 else 'FAIL'}")
    bad = d1[d1.conc == 0]
    print(f"   violating rows: {len(bad)}")
    g = d1.groupby(pd.cut(d1[OM], OM_EDGES), observed=True).agg(
        n=("conc", "size"), c=("conc", "mean"))
    g = g[g.n >= MIN_N]
    print(f"   min per-omega-bin concordance at phi=1: "
          f"{g.c.min() if len(g) else float('nan'):.6f} over {len(g)} bins")
    R["F3"] = {"n": int(len(d1)), "concordance": float(c3),
               "violations": int(len(bad)), "pass": bool(c3 == 1.0),
               "min_bin_conc": float(g.c.min()) if len(g) else None}
else:
    print("   NO ROWS with phi == 1.0 -- control is NOT MEASURABLE in-sweep (F3 = NULL).")
    print(f"   phi distribution: max={df[PHI].max():.4f}  "
          f"p99={df[PHI].quantile(0.99):.4f}  mean={df[PHI].mean():.4f}")
    top = df[df[PHI] >= df[PHI].quantile(0.99)]
    print(f"   closest achievable: phi >= p99 ({df[PHI].quantile(0.99):.3f}) -> "
          f"concordance = {top.conc.mean():.6f}  (n={len(top):,})")
    print("   P0.3 established the identity constructively over 5625 configurations.")
    R["F3"] = {"n": 0, "pass": None, "verdict": "NULL - not measurable in-sweep",
               "phi_max": float(df[PHI].max()), "phi_p99": float(df[PHI].quantile(0.99)),
               "conc_at_top_phi_pct": float(top.conc.mean()), "n_top": int(len(top))}

# F1 addendum: does the P0.2 'w == d, S == 0' escape explain the 1.43% shortfall?
eq = df[np.isclose(df[OM], 1.0)]
gt = df[df[OM] > 1.0]
print(f"\n   [F1 addendum, from P0.2] concordance at omega == 1.0 exactly : "
      f"{eq.conc.mean():.6f} (n={len(eq):,})")
print(f"   [F1 addendum]             concordance at omega  > 1.0        : "
      f"{gt.conc.mean():.6f} (n={len(gt):,})")
R["F1_addendum"] = {"conc_at_omega_eq_1": float(eq.conc.mean()), "n_eq": int(len(eq)),
                    "conc_at_omega_gt_1": float(gt.conc.mean()), "n_gt": int(len(gt))}

# ---------------------------------------------------------------- F4
print("\n" + "=" * 72); print("F4  recovery of the paper's ~0.44 frontier agreement")
W_PAPER = 3
dp = df[df.w == W_PAPER]
om_paper = dp[OM].mean()
cell = dp[(dp[PHI] < 0.25) & (dp[OM] < 0.4)]
cell_front = cell[cell.in_structural_frontier == 1]
la_all = cell.lblagree.mean() if len(cell) else np.nan
la_front = cell_front.lblagree.mean() if len(cell_front) else np.nan
nb2_front = sm[sm.w == W_PAPER].agree_frontier_label.mean()
print(f"   paper's w={W_PAPER}: mean omega = {om_paper:.4f}  "
      f"({'OBJECTIVE regime omega>=1' if om_paper >= 1 else 'below the band, omega<1'})")
print(f"   cell phi<0.25 & omega<0.4, all self-ref nodes : label agreement = "
      f"{la_all:.4f}  (n={len(cell):,})")
print(f"   cell phi<0.25 & omega<0.4, frontier nodes only: label agreement = "
      f"{la_front:.4f}  (n={len(cell_front):,})")
print(f"   nb2-style stagewise agree_frontier at w=3     : {nb2_front:.4f}")
ok4 = abs(la_front - 0.44) <= 0.10
print(f"   F4 (frontier-only vs 0.44 +/- 0.10) -> {'PASS' if ok4 else 'FAIL'}")
R["F4"] = {"omega_at_w3": float(om_paper), "in_objective_regime": bool(om_paper >= 1),
           "label_agree_cell_all": float(la_all), "n_cell": int(len(cell)),
           "label_agree_cell_frontier": float(la_front), "n_cell_front": int(len(cell_front)),
           "nb2_stagewise_agree_frontier_w3": float(nb2_front),
           "pass": bool(ok4)}

# ---------------------------------------------------------------- F5
print("\n" + "=" * 72); print("F5  substrate divergence")
print(f"   summary_R1 symdiff_nodes_AB: max={sm.symdiff_nodes_AB.max()}  "
      f"mean={sm.symdiff_nodes_AB.mean():.4f}  nonzero rows={(sm.symdiff_nodes_AB>0).sum()}")
print(f"   trunk_common all true      : {bool(sm.trunk_common.all())}")
J = sm.jaccard_A_at_stage_start
print(f"   stages with J<1 (A_A!=A_B) : {(J < 1).sum()} / {J.notna().sum()}")
print(f"   corr(symdiff, 1-J)         : UNDEFINED -- symdiff has zero variance "
      f"(std={sm.symdiff_nodes_AB.std():.1f})")
R["F5"] = {"max_symdiff": int(sm.symdiff_nodes_AB.max()),
           "mean_symdiff": float(sm.symdiff_nodes_AB.mean()),
           "nonzero_symdiff_rows": int((sm.symdiff_nodes_AB > 0).sum()),
           "trunk_always_common": bool(sm.trunk_common.all()),
           "stages_with_disagreement": int((J < 1).sum()),
           "stages_measured": int(J.notna().sum()),
           "corr_symdiff_1minusJ": None}

# ---------------------------------------------------------------- R2 surface
print("\n" + "=" * 72); print("R2  (omega, phi) surface")
phi_edges = [0, 0.25, 0.5, 0.75, 0.999, 1.001]
om_edges2 = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 10.0]
df["ob"] = pd.cut(df[OM], om_edges2)
df["pb"] = pd.cut(df[PHI], phi_edges, include_lowest=True)
piv = df.pivot_table(index="ob", columns="pb", values="conc", aggfunc="mean", observed=True)
cnt = df.pivot_table(index="ob", columns="pb", values="conc", aggfunc="size", observed=True)
piv = piv.where(cnt >= MIN_N)
print(piv.round(4).to_string())
print("\ncell counts:"); print(cnt.to_string())
R["R2_surface"] = {"concordance": json.loads(piv.to_json()),
                   "counts": json.loads(cnt.to_json())}

# ---------------------------------------------------------------- R3 degree bins
print("\n" + "=" * 72); print("R3  degree binning")
dcol = "d_live_at_stage_start"
qs = df[dcol].quantile([1/3, 2/3]).values
dbins = [(df[dcol] <= qs[0], f"d<={qs[0]:.0f}"),
         ((df[dcol] > qs[0]) & (df[dcol] <= qs[1]), f"{qs[0]:.0f}<d<={qs[1]:.0f}"),
         (df[dcol] > qs[1], f"d>{qs[1]:.0f}")]
r3 = []
for mask, name in dbins:
    d_ = df[mask]
    a, b = fit(d_, OM, OM_EDGES, f"omega|{name}"), fit(d_, "w", W_EDGES, f"w|{name}")
    r3.append({"bin": name, "n": int(len(d_)), "mean_d": float(d_[dcol].mean()),
               "omega": a, "w": b})
    print(f"   {name:12s} n={len(d_):8,d} mean_d={d_[dcol].mean():5.2f}  "
          f"omega x0={a.get('x0', float('nan')):6.3f} RMSE={a.get('rmse', float('nan')):.5f} | "
          f"w x0={b.get('x0', float('nan')):7.3f} RMSE={b.get('rmse', float('nan')):.5f}")
x0o = [r["omega"]["x0"] for r in r3 if r["omega"]["ok"]]
x0w = [r["w"]["x0"] for r in r3 if r["w"]["ok"]]
cvo = float(np.std(x0o) / abs(np.mean(x0o))) if len(x0o) == 3 else float("nan")
cvw = float(np.std(x0w) / abs(np.mean(x0w))) if len(x0w) == 3 else float("nan")
print(f"   CV of midpoint x0 across degree bins:  omega={cvo:.4f}   w={cvw:.4f}")
print(f"   omega collapses better than w        :  {cvo < cvw}")
R["R3"] = {"bins": r3, "cv_x0_omega": cvo, "cv_x0_w": cvw,
           "omega_collapses_better": bool(cvo < cvw)}

# ---------------------------------------------------------------- figures
def curveplot(f, xlabel, title, path, extra=None):
    fig, ax = plt.subplots(figsize=(8, 5))
    if f["ok"]:
        bx = [b["x"] for b in f["bins"]]; by = [b["y"] for b in f["bins"]]
        bn = [b["n"] for b in f["bins"]]
        ax.scatter(bx, by, s=np.clip(np.array(bn) / 400, 8, 90), zorder=3,
                   color="steelblue", label="bin mean (area ∝ n)")
        xs = np.linspace(min(bx), max(bx), 400)
        ax.plot(xs, logistic4(xs, f["lo"], f["hi"], f["k"], f["x0"]), color="firebrick",
                lw=2, label=(f"logistic: norm.slope={f['normalized_slope']:.2f}, "
                             f"RMSE={f['rmse']:.4f}, R²={f['r2']:.3f}"))
    if extra is not None:
        for lbl, sub in extra:
            ax.plot(sub[0], sub[1], "--", lw=1.2, alpha=0.85, label=lbl)
    ax.set_xlabel(xlabel); ax.set_ylabel("per-node concordance (A vs B verdict)")
    ax.set_title(title); ax.grid(alpha=0.25); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=150); plt.close(fig)
    print("  wrote", os.path.basename(path))


print("\nfigures:")
g_lo = binmeans(df[df[PHI] < 0.25], OM, OM_EDGES)
curveplot(fo, "ω = w / d(v)", "F1/F2 — concordance vs ω (all stages, all φ)",
          os.path.join(ROOT, "concordance_vs_omega.png"),
          extra=[("restricted to φ<0.25", (g_lo.x.values, g_lo.y.values))])
curveplot(fw, "w (self-weight, pooled over degrees)",
          "F2 — concordance vs w  (§7: pooling over d mixes thresholds)",
          os.path.join(ROOT, "concordance_vs_w.png"))

fig, ax = plt.subplots(figsize=(9, 5.5))
m = piv.values.astype(float)
im = ax.imshow(m, aspect="auto", cmap="viridis", vmin=np.nanmin(m), vmax=1.0)
ax.set_xticks(range(len(piv.columns)))
ax.set_xticklabels([str(c) for c in piv.columns], rotation=30, ha="right", fontsize=8)
ax.set_yticks(range(len(piv.index)))
ax.set_yticklabels([str(i) for i in piv.index], fontsize=8)
ax.set_xlabel("φ  (frozen fraction of neighbourhood, at stage start)")
ax.set_ylabel("ω = w / d(v)")
ax.set_title("R2 — concordance surface over (ω, φ);  blank = n < 30")
for i in range(m.shape[0]):
    for j in range(m.shape[1]):
        if not np.isnan(m[i, j]):
            ax.text(j, i, f"{m[i,j]:.3f}\nn={int(cnt.values[i,j])}", ha="center",
                    va="center", fontsize=6.5,
                    color="white" if m[i, j] < 0.93 else "black")
fig.colorbar(im, ax=ax, label="concordance")
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "surface_omega_phi.png"), dpi=150)
plt.close(fig); print("  wrote surface_omega_phi.png")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for r in r3:
    for ax, key, xl in ((axes[0], "omega", "ω = w/d(v)"), (axes[1], "w", "w")):
        if r[key]["ok"]:
            bx = [b["x"] for b in r[key]["bins"]]; by = [b["y"] for b in r[key]["bins"]]
            ax.plot(bx, by, "-o", ms=3, lw=1.3, label=f"{r['bin']} (mean d={r['mean_d']:.1f})")
        ax.set_xlabel(xl); ax.set_ylabel("concordance"); ax.grid(alpha=0.25)
axes[0].set_title(f"R3 — ω collapse across degree bins (CV of x₀ = {cvo:.3f})")
axes[1].set_title(f"R3 — w curves shift with degree (CV of x₀ = {cvw:.3f})")
axes[0].legend(fontsize=8); axes[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "R3_degree_bins.png"), dpi=150)
plt.close(fig); print("  wrote R3_degree_bins.png")

json.dump(R, open(os.path.join(ROOT, "decision_results.json"), "w"), indent=2, default=str)
print("\nwrote decision_results.json")
