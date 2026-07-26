"""R1 -- the w sweep. Emits rows_R1.csv (primary artifact) and summary_R1.csv.

Pre-registration §5: beta=1.3, two observers, n0=60, w in {1..2*d_max},
>=32 seeds per w. Long format, one row per self-referential node per stage,
measured at STAGE START before any expansion move. No aggregation in the loop.
"""
import csv, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import run_measured

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

D_MAX = 25          # measured in preflight over seeds 0..31, n0=60, radius=0.30
W_VALUES = list(range(1, 2 * D_MAX + 1))
SEEDS = list(range(32))
STAGES = 14         # notebook 2's run() default
BETA = 1.3

ROW_COLS = ["seed", "stage", "node_id", "d_live_at_stage_start", "w",
            "omega_w_over_d", "phi_frozen_frac_at_stage_start",
            "resolvable_A_at_stage_start", "resolvable_B_at_stage_start",
            "frozen_self", "label_A_at_stage_start", "label_B_at_stage_start",
            "in_structural_frontier", "beta"]
SUM_COLS = ["seed", "w", "stage", "concordance_selfref_at_stage_start",
            "jaccard_A_at_stage_start", "agree_frontier_label",
            "agree_past_label", "agree_core_label", "n_nodes",
            "symdiff_nodes_AB", "trunk_common"]


def main():
    rows_path = os.path.join(ROOT, "rows_R1.csv")
    sum_path = os.path.join(ROOT, "summary_R1.csv")
    done = set()
    if os.path.exists(sum_path):                       # resumable
        with open(sum_path, newline="") as f:
            for r in csv.DictReader(f):
                done.add((int(r["seed"]), int(r["w"])))
        print(f"resuming: {len(done)} (seed,w) pairs already complete")

    fr = open(rows_path, "a", newline="")
    fs = open(sum_path, "a", newline="")
    wr = csv.DictWriter(fr, fieldnames=ROW_COLS)
    ws = csv.DictWriter(fs, fieldnames=SUM_COLS)
    if not done:
        wr.writeheader(); ws.writeheader()

    t0 = time.time(); n_rows = 0
    for w in W_VALUES:
        for seed in SEEDS:
            if (seed, w) in done:
                continue
            rows, summ = run_measured(seed=seed, w=w, beta=BETA, n0=60,
                                      frac=0.25, stages=STAGES, radius=0.30)
            wr.writerows(rows); n_rows += len(rows)
            for i, st in enumerate(summ["stage"]):
                ws.writerow({
                    "seed": seed, "w": w, "stage": st,
                    "concordance_selfref_at_stage_start": summ["concordance"][i],
                    "jaccard_A_at_stage_start": summ["jaccard_A"][i],
                    "agree_frontier_label": summ["agree_frontier"][i],
                    "agree_past_label": summ["agree_past"][i],
                    "agree_core_label": summ["agree_core"][i],
                    "n_nodes": summ["n_nodes"][i],
                    "symdiff_nodes_AB": summ["symdiff_nodes"][i],
                    "trunk_common": summ["trunk_common"][i],
                })
        fr.flush(); fs.flush()
        print(f"  w={w:3d}/{W_VALUES[-1]}  rows so far={n_rows:8d}  "
              f"elapsed={time.time()-t0:7.1f}s", flush=True)
    fr.close(); fs.close()
    print(f"done. {n_rows} rows in {time.time()-t0:.1f}s -> {rows_path}")


if __name__ == "__main__":
    main()
