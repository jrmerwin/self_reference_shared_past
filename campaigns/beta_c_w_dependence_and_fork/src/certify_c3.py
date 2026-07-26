"""C3 only: sterile-basin script against Table 3.

Run separately from C2. C2's blocking clause bars use of the notebook-1 *variant*;
C3 certifies a different instrument (the sterile script, used unmodified) and is
therefore still in scope.
"""
import importlib.util, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.join(HERE, "..")
REPO = os.path.join(CAMP, "..", "..")

spec = importlib.util.spec_from_file_location(
    "ster", os.path.join(REPO, "sterile_final_pre_paper_test.py"))
ster = importlib.util.module_from_spec(spec); sys.modules["ster"] = ster
spec.loader.exec_module(ster)

PAPER_T3 = {"baseline_no_capture": 0.906,
            "sigma_pinned_no_capture": 0.915,
            "sigma_contact_gamma1": 0.914,
            "matched_universal_contact_gamma1_rep": 0.914,
            "sigma_adjacent_gamma0.5": 1.820,
            "matched_universal_adjacent_gamma0.5_rep": 1.820}
PAPER_T2 = {"baseline_no_capture": (1.00, 1200.0, 498.1),
            "sigma_pinned_no_capture": (1.00, 1200.0, 497.3),
            "sigma_contact_gamma1": (1.00, 1200.0, 488.8),
            "matched_universal_contact_gamma1_rep": (1.00, 1200.0, 492.5),
            "sigma_adjacent_gamma0.5": (0.00, 398.1, 0.0),
            "matched_universal_adjacent_gamma0.5_rep": (0.00, 398.1, 0.0)}

C0 = ster.NONSTERILE_UNIVERSAL_S[0]
conds = [ster.Condition("baseline_no_capture"),
         ster.Condition("sigma_pinned_no_capture", pin_target=ster.SIGMA),
         ster.Condition("sigma_contact_gamma1", target=ster.SIGMA, mode="contact", gamma=1.0),
         ster.Condition("matched_universal_contact_gamma1_rep", target=C0, mode="contact", gamma=1.0),
         ster.Condition("sigma_adjacent_gamma0.5", target=ster.SIGMA, mode="adjacent", gamma=0.5),
         ster.Condition("matched_universal_adjacent_gamma0.5_rep", target=C0, mode="adjacent", gamma=0.5)]

out = {}

# ---- Table 2 (fixed beta = 1.3), as committed: 32 seeds, max_res 1200
print("=" * 78); print("C3a  Table 2 -- fixed-beta stress test at beta = 1.3")
fixed_seeds = list(range(11000, 11032))
t0 = time.time()
fixed = ster.run_fixed_beta_block(conds, 1.3, fixed_seeds, max_res=1200)
print(f"   ({time.time()-t0:.1f}s, {len(fixed_seeds)} seeds)")
print(f"   {'condition':<42} {'P (paper)':>11} {'nres (paper)':>16} {'finalA (paper)':>18}")
t2rows = []; ok2 = True
for r in fixed:
    p, n, a = PAPER_T2[r["condition"]]
    m = abs(r["P_sustain"] - p) < 0.005 and abs(r["mean_nres"] - n) < 0.05 and \
        abs(r["mean_final_A"] - a) < 0.05
    ok2 &= m
    t2rows.append({"condition": r["condition"], "P": r["P_sustain"], "paper_P": p,
                   "nres": r["mean_nres"], "paper_nres": n,
                   "final_A": r["mean_final_A"], "paper_final_A": a, "match": bool(m)})
    print(f"   {r['condition']:<42} {r['P_sustain']:>5.2f} ({p:.2f}) "
          f"{r['mean_nres']:>8.1f} ({n:.1f}) {r['mean_final_A']:>9.1f} ({a:.1f})  "
          f"{'OK' if m else 'MISMATCH'}")
print(f"   Table 2 reproduced: {ok2}")
out["C3a_table2"] = {"rows": t2rows, "pass": bool(ok2), "seeds": len(fixed_seeds)}

# ---- Table 3 (beta_c crossings), as committed: 20 seeds, max_res 1000
print("\n" + "=" * 78); print("C3b  Table 3 -- refined threshold check")
betas = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3, 2.6, 3.0]
for label, seeds, mr in [("as committed (20 seeds, max_res=1000)", list(range(12000, 12020)), 1000),
                         ("paper caption (64 seeds, max_res=2000)", list(range(12000, 12064)), 2000)]:
    t0 = time.time()
    sweep = ster.run_beta_sweep(conds, betas, seeds, max_res=mr)
    print(f"\n   {label}   ({time.time()-t0:.1f}s)")
    print(f"   {'condition':<42} {'paper':>7} {'measured':>10} {'match':>7}")
    rows = []; ok = True
    for cond in conds:
        rs = [r for r in sweep if r["condition"] == cond.name]
        bc = ster.beta_crossing(rs)
        try:
            bcf = float(bc)
        except (TypeError, ValueError):
            bcf = float("nan")
        tgt = PAPER_T3[cond.name]
        m = abs(bcf - tgt) < 0.0005
        ok &= m
        rows.append({"condition": cond.name, "paper": tgt, "measured": str(bc),
                     "match": bool(m),
                     "P_by_beta": {str(r["beta"]): r["P_sustain"] for r in rs}})
        print(f"   {cond.name:<42} {tgt:>7.3f} {str(bc):>10} {str(m):>7}")
    print(f"   Table 3 reproduced: {ok}")
    out["C3b_" + ("committed" if "committed" in label else "caption64")] = {
        "rows": rows, "pass": bool(ok), "seeds": len(seeds), "max_res": mr}

json.dump(out, open(os.path.join(CAMP, "c3_results.json"), "w"), indent=2, default=str)
print("\nwrote c3_results.json")
