"""Philippine inflation forecasting horse race (estimation plan in CLAUDE.md).

Runs every forecast origin for one specification and saves the forecasts.
Usage: python scripts/05_estimate.py <spec> [<spec> ...]
Specs: main, expanding, w96, w180, small, core, join2018

Outputs per spec: output/forecasts/<spec>.parquet (origin, h, target, actual, models...)
For main also: output/tables/importance_raw.parquet (RF grouped permutation importance and
LASSO selection by group, per origin, h = 1 and 12).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from phfx.forecast import ALL_MODELS, Design, forecast_origin  # noqa: E402

OUT = Path("output/forecasts")
OUT.mkdir(parents=True, exist_ok=True)
TAB = Path("output/tables")
OOS_START = "2005-01-01"
H = range(1, 13)
SEED = 20261015

panel = pd.read_parquet("data/processed/panel.parquet")
panel.index = pd.DatetimeIndex(panel.index).to_period("M").to_timestamp()
groups = pd.read_csv(TAB / "predictor_groups.csv").set_index("variable")["group"]
last_x = panel.drop(columns="pi").dropna().index.max()

SPECS = {
    "main": dict(window=120),
    "expanding": dict(window=120, expanding=True),
    "w96": dict(window=96),
    "w180": dict(window=180),
    "small": dict(window=120, xgroups=("external_prices", "money_fx")),
    "core": dict(window=120, target="core"),
    "join2018": dict(window=120, join_dummy=True),
}


def data_for(spec):
    s = SPECS[spec]
    if s.get("target") == "core":
        y = panel["core"]
        X = panel.drop(columns=["core"])  # headline pi enters as a predictor
    else:
        y = panel["pi"]
        X = panel.drop(columns=["pi"])
    if "xgroups" in s:
        X = X[[c for c in X.columns if groups.get(c) in s["xgroups"]]]
    if s.get("join_dummy"):
        X = X.assign(join2018=(X.index == "2018-01-01").astype(float))
    X = X.loc[:last_x].reindex(X.index)  # predictors end at last_x
    return y, X


def feature_group(name, xcols):
    if name.startswith("y_l"):
        return "own_lags"
    if name.startswith("pc"):
        return "factors"
    if name.startswith("m") and name[1:].isdigit():
        return "seasonal"
    c = xcols[int(name[1:].split("_l")[0])]
    return groups.get(c, "other")


def grouped_importance(rf, Z, y, fgroups, rng, reps=5):
    """Increase in training MSE when all columns of a group are permuted together."""
    base = np.mean((y - rf.predict(Z)) ** 2)
    out = {}
    for g in sorted(set(fgroups)):
        idx = [i for i, fg in enumerate(fgroups) if fg == g]
        inc = []
        for _ in range(reps):
            Zp = Z.copy()
            Zp[:, idx] = Zp[rng.permutation(len(Z))][:, idx]
            inc.append(np.mean((y - rf.predict(Zp)) ** 2) - base)
        out[g] = float(np.mean(inc))
    return out


def run(spec, T, h, y, X, importance):
    s = SPECS[spec]
    extra = {} if importance else None
    f = forecast_origin(y, X, T, h, window=s["window"], d=Design(), models=ALL_MODELS,
                        expanding=s.get("expanding", False), extra=extra)
    row = {"origin": y.index[T], "h": h, "target": y.index[T + h], "actual": y.iloc[T + h], **f}
    imp = None
    if importance:
        fg = [feature_group(n, list(X.columns)) for n in extra["names"]]
        rng = np.random.default_rng(SEED + T * 13 + h)
        imp = {"origin": y.index[T], "h": h,
               **{f"rf_{g}": v for g, v in grouped_importance(extra["rf"], extra["Z"], extra["y"], fg, rng).items()},
               **{f"lasso_{g}": float(any(sel for sel, gg in zip(extra["lasso_sel"], fg) if gg == g))
                  for g in sorted(set(fg))}}
    return row, imp


def main(spec):
    y, X = data_for(spec)
    pos_last_x = y.index.get_loc(last_x)
    # origins from Dec 2004 (first target Jan 2005) to the last month with predictors; the
    # target must be observed (D13)
    first = y.index.get_loc(pd.Timestamp(OOS_START)) - 1
    last_y = y.index.get_loc(y.dropna().index.max())
    jobs = [(T, h) for h in H for T in range(first, pos_last_x + 1) if T + h <= last_y]
    t0 = time.time()
    # checkpoint each horizon to output/forecasts/_parts so a restarted container resumes
    parts = OUT / "_parts"
    parts.mkdir(exist_ok=True)
    res = []
    for h in H:
        ck = parts / f"{spec}_h{h}.pkl"
        if ck.exists():
            res += pd.read_pickle(ck)
            continue
        r = Parallel(n_jobs=4)(delayed(run)(spec, T, hh, y, X, spec == "main" and hh in (1, 12))
                               for T, hh in jobs if hh == h)
        pd.to_pickle(r, ck)
        res += r
        print(f"  {spec} h={h} done ({time.time() - t0:.0f}s)", flush=True)
    fc = pd.DataFrame([r for r, _ in res])
    fc.to_parquet(OUT / f"{spec}.parquet", index=False)
    if spec == "main":
        pd.DataFrame([i for _, i in res if i is not None]).to_parquet(TAB / "importance_raw.parquet", index=False)
    print(f"{spec}: {len(fc)} forecasts, X={X.shape[1]} predictors, {time.time() - t0:.0f}s")
    for ck in parts.glob(f"{spec}_h*.pkl"):
        ck.unlink()


if __name__ == "__main__":
    for sp in sys.argv[1:] or ["main"]:
        main(sp)
