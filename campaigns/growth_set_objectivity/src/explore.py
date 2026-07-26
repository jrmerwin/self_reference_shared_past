"""Exploratory pass over rows_R1.csv -- shape inspection before fixing the F2 fit."""
import os, sys
import numpy as np, pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
df = pd.read_csv(os.path.join(ROOT, "rows_R1.csv"))
print("rows:", len(df), " w range:", df.w.min(), df.w.max(),
      " seeds:", df.seed.nunique(), " stages:", df.stage.nunique())

df["conc"] = (df.resolvable_A_at_stage_start == df.resolvable_B_at_stage_start).astype(int)
df["unres_A"] = 1 - df.resolvable_A_at_stage_start
df["unres_B"] = 1 - df.resolvable_B_at_stage_start
df["lblagree"] = (df.label_A_at_stage_start == df.label_B_at_stage_start).astype(int)
om, phi = "omega_w_over_d", "phi_frozen_frac_at_stage_start"

print("\n--- concordance & unresolvable-fraction vs omega (all stages) ---")
b = pd.cut(df[om], np.arange(0, 4.01, 0.2))
g = df.groupby(b, observed=True).agg(n=("conc", "size"), conc=("conc", "mean"),
                                     unA=("unres_A", "mean"), phi=(phi, "mean"))
print(g[g.n >= 30].to_string())

print("\n--- same, restricted to stage<=1 (genuine label privacy, preflight B1) ---")
d01 = df[df.stage <= 1]
b = pd.cut(d01[om], np.arange(0, 4.01, 0.2))
g = d01.groupby(b, observed=True).agg(n=("conc", "size"), conc=("conc", "mean"),
                                      unA=("unres_A", "mean"), phi=(phi, "mean"))
print(g[g.n >= 30].to_string())

print("\n--- concordance vs omega, restricted to phi<0.25 ---")
dl = df[df[phi] < 0.25]
b = pd.cut(dl[om], np.arange(0, 4.01, 0.2))
g = dl.groupby(b, observed=True).agg(n=("conc", "size"), conc=("conc", "mean"))
print(g[g.n >= 30].to_string())

print("\n--- concordance vs w (pooled over degrees) ---")
g = df.groupby("w").agg(n=("conc", "size"), conc=("conc", "mean"))
print(g[g.n >= 30].to_string())

print("\n--- stage profile: concordance and label agreement ---")
g = df.groupby("stage").agg(n=("conc", "size"), conc=("conc", "mean"),
                            lbl=("lblagree", "mean"), phi=(phi, "mean"))
print(g.to_string())
