"""Evaluate the saved forecasts (RQ1, RQ2, RQ3) and write every table the paper uses.

Outputs (output/tables/):
  accuracy.csv     spec x case x model: RMSE, MAE, ratios to RW and AR, DM p-values, Holm
  mcs.csv          main spec: 90% model confidence set p-values at the decisive cases
  regimes.csv      main spec: RMSE ratios to AR in high-inflation vs other target months
  csfe.csv         main spec: cumulative squared-error differences against AR (h = 1, 12)
  importance.csv   main spec: RF grouped permutation importance and LASSO selection by group
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from phfx.evaluate import dm_test, holm, mcs, rmse  # noqa: E402
from phfx.forecast import ALL_MODELS  # noqa: E402

FC = Path("output/forecasts")
TAB = Path("output/tables")
BENCH = ["rw", "rw_ao", "ar"]
CHALLENGERS = [m for m in ALL_MODELS if m not in BENCH]
DECISIVE = ["h1", "h12", "acc3", "acc12"]
HIGH_INFL = 4.0  # top of the BSP target band, year-on-year percent


def cases(fc):
    """Yield (case, horizon for DM, frame of actual + model forecasts indexed by target)."""
    for h, g in fc.groupby("h"):
        yield f"h{h}", h, g.set_index("target")[["actual"] + ALL_MODELS]
    for k in (3, 6, 12):
        sub = fc[fc.h <= k]
        cnt = sub.groupby("origin")["h"].count()
        ok = cnt[cnt == k].index
        s = sub[sub.origin.isin(ok)].groupby("origin")[["actual"] + ALL_MODELS].sum()
        s.index = [o + pd.DateOffset(months=k) for o in s.index]  # label by the last target month
        yield f"acc{k}", k, s


def accuracy(spec, fc=None):
    fc = pd.read_parquet(FC / f"{spec}.parquet") if fc is None else fc
    rows = []
    for case, h, d in cases(fc):
        e = {m: d["actual"] - d[m] for m in ALL_MODELS}
        for m in ALL_MODELS:
            r = {"spec": spec, "case": case, "model": m, "n": len(d),
                 "start": d.index.min().strftime("%Y-%m"), "end": d.index.max().strftime("%Y-%m"),
                 "rmse": rmse(e[m]), "mae": float(np.mean(np.abs(e[m])))}
            for b in ("rw", "ar"):
                r[f"ratio_{b}"] = r["rmse"] / rmse(e[b])
                r[f"mae_ratio_{b}"] = r["mae"] / float(np.mean(np.abs(e[b])))
                r[f"dm_p_{b}"] = np.nan if m == b else dm_test(e[b], e[m], h)[1]
            rows.append(r)
    return pd.DataFrame(rows)


def add_holm(acc):
    acc = acc.copy()
    for b in ("rw", "ar"):
        acc[f"holm_p_{b}"] = np.nan
        for spec, g in acc.groupby("spec"):
            sel = g[g.case.isin(DECISIVE) & g.model.isin(CHALLENGERS)].index
            acc.loc[sel, f"holm_p_{b}"] = holm(acc.loc[sel, f"dm_p_{b}"]).values
    return acc


def yoy_headline():
    cpi = pd.read_parquet("data/processed/cpi_long.parquet")
    s = cpi[(cpi.geo == "PHILIPPINES") & (cpi.code == "0")].set_index("month")["index"]
    s.index = s.index.to_timestamp()
    return 100 * (s / s.shift(12) - 1)


def main():
    specs = [p.stem for p in sorted(FC.glob("*.parquet"))]
    main_fc = pd.read_parquet(FC / "main.parquet")
    pre2020 = main_fc[main_fc.target <= "2019-12-01"]  # robustness (c): targets up to Dec 2019
    acc = pd.concat([accuracy(s) for s in specs] + [accuracy("main_pre2020", pre2020)], ignore_index=True)
    acc = add_holm(acc)
    acc.to_csv(TAB / "accuracy.csv", index=False)
    m = acc[(acc.spec == "main") & acc.case.isin(DECISIVE)]
    print(m.pivot(index="model", columns="case", values="ratio_ar").round(3)[DECISIVE])

    fc = pd.read_parquet(FC / "main.parquet")
    # MCS at the decisive cases
    rows = []
    for case, h, d in cases(fc):
        if case not in DECISIVE:
            continue
        losses = pd.DataFrame({mm: (d["actual"] - d[mm]) ** 2 for mm in ALL_MODELS})
        p = mcs(losses, size=0.10, reps=1000)
        rows += [{"case": case, "model": mm, "mcs_p": float(p.get(mm, np.nan)), "in_mcs90": bool(p.get(mm, 0) >= 0.10)}
                 for mm in ALL_MODELS]
    pd.DataFrame(rows).to_csv(TAB / "mcs.csv", index=False)

    # RQ3: regimes by year-on-year headline inflation at the (last) target month
    yoy = yoy_headline()
    rows = []
    for case, h, d in cases(fc):
        if case not in DECISIVE:
            continue
        hi = yoy.reindex(d.index) > HIGH_INFL
        for reg, mask in (("high", hi), ("other", ~hi)):
            dd = d[mask.values]
            for mm in ALL_MODELS:
                rows.append({"case": case, "regime": reg, "model": mm, "n": len(dd),
                             "rmse": rmse(dd["actual"] - dd[mm]),
                             "ratio_ar": rmse(dd["actual"] - dd[mm]) / rmse(dd["actual"] - dd["ar"]),
                             "ratio_rw": rmse(dd["actual"] - dd[mm]) / rmse(dd["actual"] - dd["rw"])})
    pd.DataFrame(rows).to_csv(TAB / "regimes.csv", index=False)

    # CSFE against AR, h = 1 and 12
    rows = []
    for h in (1, 12):
        g = fc[fc.h == h].set_index("target").sort_index()
        for mm in ("rf", "lasso", "ridge", "lgbm", "combo", "factor"):
            c = ((g["actual"] - g["ar"]) ** 2 - (g["actual"] - g[mm]) ** 2).cumsum()
            rows += [{"h": h, "model": mm, "target": t, "csfe": v} for t, v in c.items()]
    pd.DataFrame(rows).to_csv(TAB / "csfe.csv", index=False)

    # RQ2: importance by group
    imp = pd.read_parquet(TAB / "importance_raw.parquet")
    rf_cols = [c for c in imp.columns if c.startswith("rf_")]
    la_cols = [c for c in imp.columns if c.startswith("lasso_")]
    rows = []
    for h, g in imp.groupby("h"):
        rf = g[rf_cols].clip(lower=0)
        share = rf.div(rf.sum(axis=1), axis=0).mean()
        for c in rf_cols:
            grp = c[3:]
            rows.append({"h": h, "group": grp, "rf_share": share[c],
                         "lasso_freq": g.get(f"lasso_{grp}", pd.Series(np.nan)).mean()})
    pd.DataFrame(rows).to_csv(TAB / "importance.csv", index=False)
    print(pd.DataFrame(rows).pivot(index="group", columns="h", values="rf_share").round(3))


if __name__ == "__main__":
    main()
