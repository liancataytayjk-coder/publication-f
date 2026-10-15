"""Replication gate (pre-registered in CLAUDE.md, 2026-10-15): Medeiros et al. (2021)
on FRED-MD. US CPI inflation, rolling 360-month window, 4 lags of every series plus
4 principal components, direct forecasts, OOS target months 2001-01..2015-12,
h in {1, 3, 6, 12}. Models: RW, AR(BIC), ridge, LASSO(BIC), RF.

Outputs: output/tables/replication_forecasts.csv, output/tables/replication_gate.csv
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from phfx.evaluate import rmse  # noqa: E402
from phfx.forecast import Design, forecast_origin  # noqa: E402

TAB = Path("output/tables")
MODELS = ["rw", "ar", "ridge", "lasso", "rf"]
H = [1, 3, 6, 12]


def transform(x, code):
    if code == 1:
        return x
    if code == 2:
        return x.diff()
    if code == 3:
        return x.diff().diff()
    if code == 4:
        return np.log(x)
    if code == 5:
        return np.log(x).diff()
    if code == 6:
        return np.log(x).diff().diff()
    if code == 7:
        return (x / x.shift(1) - 1).diff()
    raise ValueError(code)


raw = pd.read_csv("data/raw/fredmd/fredmd_current.csv.gz")
codes = raw.iloc[0, 1:].astype(float).astype(int)
d = raw.iloc[1:].copy()
d.index = pd.to_datetime(d.pop("sasdate"), format="%m/%d/%Y")
d = d.apply(pd.to_numeric, errors="coerce").loc[:"2015-12-01"]
y = (100 * np.log(d["CPIAUCSL"]).diff()).rename("pi")
X = pd.DataFrame({c: transform(d[c], codes[c]) for c in d.columns if c != "CPIAUCSL"})
X = X.loc["1960-01-01":]
y = y.loc["1960-01-01":]
X = X.loc[:, X.notna().all()]
print(f"FRED-MD: {X.shape[1]} complete predictors, {X.index.min():%Y-%m}..{X.index.max():%Y-%m}")

design = Design(y_lags=4, x_lags=4, n_pc=4, month_dummies=False)
targets = y.loc["2001-01-01":"2015-12-01"].index
pos = {t: i for i, t in enumerate(y.index)}
jobs = [(pos[t] - h, h, t) for h in H for t in targets]


def run(T, h, t):
    f = forecast_origin(y, X, T, h, window=360, d=design, models=MODELS)
    return {"target": t, "h": h, "actual": y.iloc[T + h], **{m: f[m] for m in MODELS}}


t0 = time.time()
res = Parallel(n_jobs=4, verbose=0)(delayed(run)(*j) for j in jobs)
fc = pd.DataFrame(res)
fc.to_csv(TAB / "replication_forecasts.csv", index=False)
print(f"{len(fc)} forecasts in {time.time() - t0:.0f}s")

r = {(m, h): rmse(g["actual"] - g[m]) for h, g in fc.groupby("h") for m in MODELS}
tab = pd.DataFrame([{"model": m, "h": h, "rmse": r[(m, h)], "ratio_rw": r[(m, h)] / r[("rw", h)],
                     "ratio_ar": r[(m, h)] / r[("ar", h)]} for m in MODELS for h in H])
print(tab.pivot(index="model", columns="h", values="ratio_rw").round(3))
avg = tab.groupby("model")["rmse"].mean()
g1 = tab[(tab.model == "rf")]["ratio_rw"]
g2 = tab[(tab.model == "rf")]["ratio_ar"].mean()
gate = pd.DataFrame([
    {"criterion": "G1", "target": "RF/RW RMSE < 1 at h=1,3,6,12",
     "estimate": "; ".join(f"h{h}={v:.3f}" for h, v in zip(H, g1)), "pass": bool((g1 < 1).all())},
    {"criterion": "G2", "target": "mean over h of RF/AR RMSE < 1", "estimate": f"{g2:.3f}", "pass": bool(g2 < 1)},
    {"criterion": "G3", "target": "RF lowest average RMSE of rw, ar, ridge, lasso, rf",
     "estimate": "; ".join(f"{m}={v:.4f}" for m, v in avg.sort_values().items()),
     "pass": bool(avg.idxmin() == "rf")},
])
gate.to_csv(TAB / "replication_gate.csv", index=False)
tab.to_csv(TAB / "replication_ratios.csv", index=False)
print(gate.to_string(index=False))
print("GATE:", "PASS" if gate["pass"].all() else "FAIL")
