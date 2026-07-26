"""C1 / C2 / C3 instrument certification. BLOCKING: if C2 fails, stop.

C1  original default w; toy and 137-registry degree distributions.
C2  the w-plumbed notebook-1 variant must reproduce Table 1 bit-exactly at w=3,
    against the ORIGINAL notebook code exec'd out of the .ipynb.
C3  the sterile-basin script must reproduce Table 3.
"""
import importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.join(HERE, "..")
REPO = os.path.join(CAMP, "..", "..")
sys.path.insert(0, HERE)
import engine_w

OUT = {}

# ---------------------------------------------------------------- load originals
def load_nb_defs(path, cuts):
    """exec the notebook's definition cells, stripping trailing demo/driver code."""
    nb = json.load(open(path, encoding="utf-8"))
    ns = {}
    for idx, cut in cuts:
        src = "".join(nb["cells"][idx]["source"])
        if cut:
            src = src.split(cut)[0]
        exec(compile(src, f"nb1_cell{idx}", "exec"), ns)
    return ns


NB1 = os.path.join(REPO, "unified_selfreference_mechanism.ipynb")
orig = load_nb_defs(NB1, [(2, "# Demonstrate a genuine diagonal"),
                          (6, "# Show the frontier advancing"),
                          (8, "betas = np.round")])
orig_run = orig["run_to_outcome"]

# ---------------------------------------------------------------- C1
print("=" * 74); print("C1  original default w, and the degree distributions that set omega")
import inspect
sig = inspect.signature(orig["Observer"].conclusion)
w_default = sig.parameters["sw"].default
print(f"   original default self-weight w = {w_default}   "
      f"(from `def conclusion(self, v, sw={w_default})`)")
assert w_default == engine_w.ORIGINAL_DEFAULT_W

toy_degs = []
for s in range(32):
    g, _ = engine_w.build(60, 0.25, s, radius=0.30)
    toy_degs += [d for _, d in g.degree()]
toy_degs = np.array(toy_degs)

spec = importlib.util.spec_from_file_location(
    "ster", os.path.join(REPO, "sterile_final_pre_paper_test.py"))
ster = importlib.util.module_from_spec(spec); sys.modules["ster"] = ster
spec.loader.exec_module(ster)
reg_degs = np.array([d for _, d in ster.G.degree()])

print(f"   toy substrate (n0=60, radius=0.30, 32 seeds, {len(toy_degs)} nodes):")
print(f"      mean d = {toy_degs.mean():.3f}   median = {np.median(toy_degs):.1f}   "
      f"max = {toy_degs.max()}   min = {toy_degs.min()}")
print(f"   137-registry ({ster.G.number_of_nodes()} nodes, {ster.G.number_of_edges()} edges, "
      f"sectors {dict(ster.SECTORS)}):")
print(f"      mean d = {reg_degs.mean():.3f}   median = {np.median(reg_degs):.1f}   "
      f"max = {reg_degs.max()}   min = {reg_degs.min()}")
print(f"      sigma id={ster.SIGMA}  degree={ster.G.degree(ster.SIGMA)}  "
      f"mult={ster.G.nodes[ster.SIGMA]['mult']}")
ratio = reg_degs.mean() / toy_degs.mean()
print(f"   <d>_registry / <d>_toy = {ratio:.3f}   "
      f"-> W2 needs registry w about {ratio:.1f}x the toy w for matched omega-bar")
print(f"   omega-bar at the published default w=3:   toy {3/toy_degs.mean():.4f}   "
      f"registry {3/reg_degs.mean():.4f}")
OUT["C1"] = {"w_default": int(w_default),
             "toy": {"mean": float(toy_degs.mean()), "median": float(np.median(toy_degs)),
                     "max": int(toy_degs.max()), "min": int(toy_degs.min())},
             "registry": {"mean": float(reg_degs.mean()), "median": float(np.median(reg_degs)),
                          "max": int(reg_degs.max()), "min": int(reg_degs.min()),
                          "nodes": ster.G.number_of_nodes(),
                          "edges": ster.G.number_of_edges(),
                          "sigma_degree": ster.G.degree(ster.SIGMA)},
             "degree_ratio": float(ratio),
             "omegabar_toy_at_w3": float(3 / toy_degs.mean()),
             "omegabar_registry_at_w3": float(3 / reg_degs.mean())}

# ---------------------------------------------------------------- C2
print("\n" + "=" * 74); print("C2  bit-exactness of the w-plumbed variant against Table 1")
BETAS = np.round(np.arange(0.6, 1.61, 0.1), 2)
NSEED = 12
PAPER_T1 = {0.6: 0.00, 0.7: 0.00, 0.8: 0.00, 0.9: 0.08, 1.0: 0.17, 1.1: 0.58,
            1.2: 0.75, 1.3: 0.92, 1.4: 0.92, 1.5: 0.92, 1.6: 0.92}

t0 = time.time()
rows = []
for beta in BETAS:
    o_out = [orig_run(beta, seed=s)[0] for s in range(NSEED)]
    v_out = [engine_w.run_to_outcome(beta, seed=s, w=w_default)[0] for s in range(NSEED)]
    po = float(np.mean([x == "SUSTAINED" for x in o_out]))
    pv = float(np.mean([x == "SUSTAINED" for x in v_out]))
    rows.append({"beta": float(beta), "orig_P": po, "variant_P": pv,
                 "orig_counts": sum(x == "SUSTAINED" for x in o_out),
                 "variant_counts": sum(x == "SUSTAINED" for x in v_out),
                 "paper_P": PAPER_T1[float(beta)],
                 "per_seed_identical": o_out == v_out})
print(f"   ({time.time()-t0:.1f}s)")
print(f"   {'beta':>5} {'paper':>7} {'orig':>7} {'variant':>8} {'n_sus':>6} "
      f"{'seq_identical':>14} {'matches_paper':>14}")
ok_seq = True; ok_paper = True
for r in rows:
    mp = abs(r["variant_P"] - r["paper_P"]) < 0.005 or \
         round(r["variant_P"], 2) == r["paper_P"]
    ok_seq &= r["per_seed_identical"]; ok_paper &= mp
    print(f"   {r['beta']:>5.1f} {r['paper_P']:>7.2f} {r['orig_P']:>7.2f} "
          f"{r['variant_P']:>8.2f} {r['variant_counts']:>4}/12 "
          f"{str(r['per_seed_identical']):>14} {str(mp):>14}")
bc_o = engine_w.beta_c_from_P([r["beta"] for r in rows], [r["orig_P"] for r in rows])
bc_v = engine_w.beta_c_from_P([r["beta"] for r in rows], [r["variant_P"] for r in rows])
print(f"\n   beta_c  original = {bc_o:.4f}   variant = {bc_v:.4f}   "
      f"paper = 1.08 (notebook stored 1.075)")
print(f"   per-seed outcome sequences identical at every beta : {ok_seq}")
print(f"   variant reproduces Table 1 survival counts         : {ok_paper}")
c2 = ok_seq and ok_paper and abs(bc_v - 1.075) < 0.001
print(f"   C2 -> {'PASS' if c2 else 'FAIL'}")
OUT["C2"] = {"rows": rows, "beta_c_orig": bc_o, "beta_c_variant": bc_v,
             "seq_identical": bool(ok_seq), "matches_paper": bool(ok_paper),
             "pass": bool(c2)}

if not c2:
    print("\n   !! C2 FAILED - certification is blocking. No variant data may be used.")
    json.dump(OUT, open(os.path.join(CAMP, "certification_results.json"), "w"), indent=2)
    sys.exit(1)

# ---------------------------------------------------------------- C3
print("\n" + "=" * 74); print("C3  sterile-basin script against Table 3")
PAPER_T3 = {"baseline_no_capture": 0.906,
            "sigma_pinned_no_capture": 0.915,
            "sigma_contact_gamma1": 0.914,
            "matched_universal_contact_gamma1_rep": 0.914,
            "sigma_adjacent_gamma0.5": 1.820,
            "matched_universal_adjacent_gamma0.5_rep": 1.820}

betas3 = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3, 2.6, 3.0]
sweep_seeds = list(range(12000, 12020))            # as committed: 20 seeds
conds = [ster.Condition("baseline_no_capture"),
         ster.Condition("sigma_pinned_no_capture", pin_target=ster.SIGMA),
         ster.Condition("sigma_contact_gamma1", target=ster.SIGMA, mode="contact", gamma=1.0),
         ster.Condition("matched_universal_contact_gamma1_rep",
                        target=ster.NONSTERILE_UNIVERSAL_S[0], mode="contact", gamma=1.0),
         ster.Condition("sigma_adjacent_gamma0.5", target=ster.SIGMA, mode="adjacent", gamma=0.5),
         ster.Condition("matched_universal_adjacent_gamma0.5_rep",
                        target=ster.NONSTERILE_UNIVERSAL_S[0], mode="adjacent", gamma=0.5)]
t0 = time.time()
sweep = ster.run_beta_sweep(conds, betas3, sweep_seeds, max_res=1000)
print(f"   ({time.time()-t0:.1f}s, {len(sweep_seeds)} seeds/beta as committed)")
print(f"   {'condition':<42} {'paper':>7} {'as-committed':>13} {'match':>7}")
c3rows = []; ok3 = True
for cond in conds:
    rs = [r for r in sweep if r["condition"] == cond.name]
    bc = ster.beta_crossing(rs)
    try:
        bcf = float(bc)
    except (TypeError, ValueError):
        bcf = float("nan")
    tgt = PAPER_T3[cond.name]
    m = abs(bcf - tgt) < 0.0005
    ok3 &= m
    c3rows.append({"condition": cond.name, "paper": tgt, "measured": bc,
                   "measured_float": bcf, "match": bool(m),
                   "P_by_beta": {str(r["beta"]): r["P_sustain"] for r in rs}})
    print(f"   {cond.name:<42} {tgt:>7.3f} {str(bc):>13} {str(m):>7}")
print(f"   C3 -> {'PASS' if ok3 else 'FAIL'}")
OUT["C3"] = {"rows": c3rows, "pass": bool(ok3), "seeds_used": len(sweep_seeds),
             "paper_caption_seeds": 64, "betas": betas3}

json.dump(OUT, open(os.path.join(CAMP, "certification_results.json"), "w"), indent=2, default=str)
print("\nwrote certification_results.json")
