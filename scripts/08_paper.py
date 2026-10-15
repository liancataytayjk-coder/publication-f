"""Build the numbers dictionary and tables, then render the manuscript.

Every number in the manuscript comes from output/tables via the dictionary n,
saved to output/tables/paper_numbers.json. Prose that depends on the results is
assembled here from the numbers with explicit rules, so no estimate is typed.
"""
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_doc import render  # noqa: E402

TAB = Path("output/tables")
LABEL = {"rw": "Random walk", "rw_ao": "Random walk (12-month mean)", "ar": "AR", "factor": "Factor (AR + PCs)",
         "ridge": "Ridge", "lasso": "LASSO", "adalasso": "Adaptive LASSO", "rf": "Random forest",
         "lgbm": "Gradient boosting", "combo": "ML combination"}
ORDER = ["rw", "rw_ao", "ar", "factor", "ridge", "lasso", "adalasso", "rf", "lgbm", "combo"]
CHALL = ["factor", "ridge", "lasso", "adalasso", "rf", "lgbm", "combo"]
CASES = [("h1", "h = 1"), ("h12", "h = 12"), ("acc3", "3-month acc."), ("acc12", "12-month acc.")]
GROUP_LABEL = {"food": "Food", "energy_utilities": "Energy and utilities", "other_domestic": "Other domestic prices",
               "regional": "Regional inflation", "external_prices": "World prices",
               "money_fx": "Money and exchange rate", "own_lags": "Past inflation", "factors": "Factors (PCs)",
               "seasonal": "Month dummies"}
MONTH = lambda s: pd.Timestamp(s).strftime("%B %Y")  # noqa: E731


def md_table(df, caption, note=None):
    cols = list(df.columns)
    lines = ["", f"**{caption}**", "", "| " + " | ".join(cols) + " |",
             "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    lines.append("")
    if note:
        lines += [f"*Note.* {note}", ""]
    return "\n".join(lines)


def stars(p):
    if p is None or np.isnan(p):
        return ""
    return "\\*\\*\\*" if p < 0.01 else "\\*\\*" if p < 0.05 else "\\*" if p < 0.10 else ""


def fmt(x, d=2):
    return f"{x:.{d}f}"


def build():
    n, t = {}, {}
    n["build_date"] = dt.date.today().strftime("%d %B %Y")

    # ---- data facts
    w = pd.read_parquet("data/processed/cpi_weights.parquet")
    wph = w[w.geo == "PHILIPPINES"].set_index("code")["weight"]
    n["w_food"] = fmt(wph["01.1"], 1)
    n["w_rice"] = fmt(wph["01.1.1.12"], 1)
    val = pd.read_csv(TAB / "validation_yoy.csv", index_col=0)
    n["val_maxdiff"] = fmt(val["diff"].abs().max() + 1e-9, 2)
    n["latest_month"] = MONTH(pd.Period(val.index[-1]).to_timestamp())
    n["yoy_latest"] = fmt(val["psa"].iloc[-1], 1)
    jc = pd.read_csv(TAB / "join_check.csv", dtype={"code": str})
    n["join_z"] = fmt(abs(jc.loc[jc.code == "0", "z"].iloc[0]), 2)
    cpi = pd.read_parquet("data/processed/cpi_long.parquet")
    s = cpi[(cpi.geo == "PHILIPPINES") & (cpi.code == "0")].set_index("month")["index"]
    yoy = (100 * (s / s.shift(12) - 1)).dropna()
    yoy = yoy[yoy.index >= pd.Period("2005-01", "M")]
    n["share_outside_band"] = fmt(100 * ((yoy < 2) | (yoy > 4)).mean(), 0)
    n["share_high"] = fmt(100 * (yoy > 4).mean(), 0)
    summ = pd.read_csv(TAB / "panel_summary.csv").iloc[0]
    n["n_pred"] = int(summ.n_predictors)
    n["last_x"] = MONTH(pd.Period(summ.last_predictors).to_timestamp())
    n["n_features"] = 12 + 4 * n["n_pred"] + 16 + 11

    groups = pd.read_csv(TAB / "predictor_groups.csv")
    rows = []
    for g, d in groups.groupby("group", sort=False):
        rows.append({"Group": GROUP_LABEL[g], "Series": len(d),
                     "Content": "; ".join(d.label.str.capitalize().head(8)) + ("; ..." if len(d) > 8 else ""),
                     "Source": ", ".join(sorted(set(d.source.str.split().str[0])))})
    t["table1"] = md_table(pd.DataFrame(rows), "Table 1. Predictors by group",
                           "All series are monthly, Feb 1994 to " + n["last_x"] + ". Prices and the exchange rate "
                           "enter as 100 × log change, interest rates as first differences. The full list is in "
                           "output/tables/predictor_groups.csv.")

    # ---- replication gate
    gate = pd.read_csv(TAB / "replication_gate.csv")
    rr = pd.read_csv(TAB / "replication_ratios.csv")
    rf = rr[rr.model == "rf"].set_index("h")
    n["gate_pass"] = bool(gate["pass"].all())
    n["gate_rf_rw"] = ", ".join(fmt(v, 2) for v in rf.ratio_rw)
    n["gate_rf_ar_mean"] = fmt(rf.ratio_ar.mean(), 3)
    piv = rr.pivot(index="model", columns="h", values="ratio_rw").reindex(["ar", "ridge", "lasso", "rf"])
    piv.index = [LABEL[m] for m in piv.index]
    piv.columns = [f"h = {h}" for h in piv.columns]
    t["tableA2"] = md_table(piv.round(3).reset_index().rename(columns={"index": "Model"}),
                            "Table A2. Replication gate on FRED-MD: RMSE relative to the random walk, 2001–2015",
                            "US CPI inflation; rolling 360-month window; 180 target months per horizon.")

    # ---- accuracy
    acc = pd.read_csv(TAB / "accuracy.csv")
    main = acc[acc.spec == "main"]
    n["n_oos"] = int(main[main.case == "h1"].n.iloc[0])
    n["oos_end"] = MONTH(main[main.case == "h1"].end.iloc[0])
    for _, r in acc.iterrows():
        k = f"{r.spec}_{r.case}_{r.model}"
        n[k + "_ar"] = fmt(r.ratio_ar, 2)
        n[k + "_rw"] = fmt(r.ratio_rw, 2)
        n[k + "_rmse"] = fmt(r.rmse, 3)
        n[k + "_pdm_ar"] = "–" if np.isnan(r.dm_p_ar) else fmt(r.dm_p_ar, 3)
        n[k + "_pholm_ar"] = "–" if np.isnan(r.get("holm_p_ar", np.nan)) else fmt(r.holm_p_ar, 3)
        n[k + "_pdm_rw"] = "–" if np.isnan(r.dm_p_rw) else fmt(r.dm_p_rw, 3)
    rows = []
    for m in ORDER:
        row = {"Model": LABEL[m]}
        for c, lab in CASES:
            r = main[(main.case == c) & (main.model == m)].iloc[0]
            row[lab] = "1.00" if m == "ar" else fmt(r.ratio_ar, 2) + stars(r.dm_p_ar)
        rows.append(row)
    ar_rmse = {lab: fmt(main[(main.case == c) & (main.model == "ar")].rmse.iloc[0], 3) for c, lab in CASES}
    rows.append({"Model": "AR RMSE (log points)", **ar_rmse})
    mcs = pd.read_csv(TAB / "mcs.csv")
    rows.append({"Model": "In 90% MCS", **{lab: ", ".join(LABEL[m] for m in mcs[(mcs.case == c) & mcs.in_mcs90].model)
                                         for c, lab in CASES}})
    t["table2"] = md_table(pd.DataFrame(rows), f"Table 2. RMSE relative to the AR benchmark, January 2005–{n['oos_end']}",
                           "Stars mark one-sided Diebold–Mariano tests (HLN correction) that the model is more "
                           "accurate than the AR: \\* 10%, \\*\\* 5%, \\*\\*\\* 1%. 'acc.' = inflation accumulated "
                           "over the next 3 or 12 months. The last row lists the models in the 90% model confidence set.")
    full = main[main.case.str.match(r"^h\d+$")].copy()
    full["h"] = full.case.str[1:].astype(int)
    pa = full.pivot(index="model", columns="h", values="ratio_ar").reindex(ORDER)
    pa.index = [LABEL[m] for m in pa.index]
    pa.columns = [str(c) for c in pa.columns]
    t["tableA3"] = md_table(pa.round(2).reset_index().rename(columns={"index": "Model / h"}),
                            "Table A3. RMSE relative to the AR at every horizon h = 1, ..., 12 (main specification)")
    dec = main[main.case.isin([c for c, _ in CASES]) & main.model.isin(CHALL)]
    n["min_dm_p"] = fmt(dec.dm_p_ar.min(), 2)
    n["min_holm_p"] = fmt(dec.holm_p_ar.min(), 2)
    cmb = dec[dec.model == "combo"].ratio_ar
    n["combo_min"], n["combo_max"] = fmt(cmb.min(), 2), fmt(cmb.max(), 2)
    h12 = main[(main.case == "h12") & main.model.isin(CHALL)].ratio_ar
    n["min_h12"], n["max_h12"] = fmt(h12.min(), 2), fmt(h12.max(), 2)
    n["ar_vs_rw_h1"] = fmt(100 * (1 - main[(main.case == "h1") & (main.model == "ar")].ratio_rw.iloc[0]), 0)
    n["ridge_max_pct"] = fmt(100 * (full[full.model == "ridge"].ratio_ar.max() - 1), 0)
    n["lgbm_max_pct"] = fmt(100 * (full[full.model == "lgbm"].ratio_ar.max() - 1), 0)
    n["factor_min"] = fmt(full[full.model == "factor"].ratio_ar.min(), 2)
    n["factor_max"] = fmt(full[full.model == "factor"].ratio_ar.max(), 2)
    fc = pd.read_parquet("output/forecasts/main.parquet")
    one = fc[fc.h == 1].set_index("target")
    for lab, mth in (("mar26", "2026-03-01"), ("apr26", "2026-04-01"), ("may26", "2026-05-01")):
        for col in ("actual", "ar", "combo"):
            n[f"{lab}_{col}"] = fmt(one.loc[mth, col], 2)
    names = {"expanding": "an expanding window", "w96": "a 96-month window", "w180": "a 180-month window",
             "main_pre2020": "targets up to December 2019 only", "small": "only world prices and money as predictors",
             "join2018": "a dummy for the January 2018 join", "core": "core inflation as the target"}
    sents = []
    for sp, nm in names.items():
        a = acc[(acc.spec == sp) & acc.case.isin([c for c, _ in CASES]) & acc.model.isin(CHALL)]
        if a.empty:
            continue
        best = a.loc[a.ratio_ar.idxmin()]
        nsig = int((a.dm_p_ar < 0.05).sum())
        sents.append(f"With {nm}, the lowest relative RMSE among the challengers is {best.ratio_ar:.2f} "
                     f"({LABEL[best.model]}, {dict(CASES)[best.case]}), and {nsig} of {len(a)} "
                     f"Diebold–Mariano tests against the AR reject at 5%"
                     + (f" ({int((a.holm_p_ar < 0.05).sum())} after the Holm correction)." if nsig else "."))
    n["robust_auto"] = " ".join(sents)
    n["robust_comment"] = ""
    order = ["main"] + [k for k in names if k in set(acc.spec)]
    rows = []
    for sp in order:
        for m in ("factor", "lasso", "rf", "combo"):
            r = {"Specification": "Main" if sp == "main" else names[sp].capitalize(), "Model": LABEL[m]}
            for c, lab in CASES:
                q = acc[(acc.spec == sp) & (acc.case == c) & (acc.model == m)].iloc[0]
                r[lab] = fmt(q.ratio_ar, 2) + stars(q.dm_p_ar)
            rows.append(r)
    t["tableA4"] = md_table(pd.DataFrame(rows), "Table A4. Robustness: RMSE relative to the AR at the decisive cases",
                            "Stars as in Table 2. Each check changes one element of the main specification.")
    exc = []
    for c, lab in CASES:
        out = [LABEL[m] for m in mcs[(mcs.case == c) & ~mcs.in_mcs90].model]
        exc.append(f"{' and '.join(out) if out else 'none'} at {lab}")
    n["mcs_excluded"] = "; ".join(exc)
    n["ar_in_all_mcs"] = bool(mcs[mcs.model == "ar"].in_mcs90.all())
    n["mcs"] = {c: [LABEL[m] for m in mcs[(mcs.case == c) & mcs.in_mcs90].model] for c, _ in CASES}

    # ---- regimes
    reg = pd.read_csv(TAB / "regimes.csv")
    for _, r in reg.iterrows():
        n[f"reg_{r.case}_{r.regime}_{r.model}_ar"] = fmt(r.ratio_ar, 2)
        n[f"reg_{r.case}_{r.regime}_n"] = int(r.n)
    rows = []
    for m in ["rw", "factor", "ridge", "lasso", "adalasso", "rf", "lgbm", "combo"]:
        row = {"Model": LABEL[m]}
        for c, lab in CASES:
            for g in ("high", "other"):
                v = reg[(reg.case == c) & (reg.regime == g) & (reg.model == m)].ratio_ar.iloc[0]
                row[f"{lab}, {'high' if g == 'high' else 'other'}"] = fmt(v, 2)
        rows.append(row)
    nrow = {"Model": "Months"}
    for c, lab in CASES:
        for g in ("high", "other"):
            nrow[f"{lab}, {g}"] = int(reg[(reg.case == c) & (reg.regime == g)].n.iloc[0])
    rows.append(nrow)
    t["table3"] = md_table(pd.DataFrame(rows), "Table 3. RMSE relative to the AR in high-inflation and other months",
                           "High-inflation months are target months in which year-on-year headline inflation "
                           "exceeds 4%, the top of the BSP target band.")

    # ---- importance
    imp = pd.read_csv(TAB / "importance.csv")
    for _, r in imp.iterrows():
        n[f"imp_{r.group}_h{r.h}"] = fmt(100 * r.rf_share, 0)
        n[f"lassofreq_{r.group}_h{r.h}"] = fmt(100 * r.lasso_freq, 0)

    t["tableA1"] = md_table(pd.DataFrame([
        {"Model": "AR, factor", "Settings": "OLS; p ≤ 12 lags and k ≤ 4 principal components by BIC; month dummies"},
        {"Model": "Ridge", "Settings": "Standardized features; penalty from 60 values in [0.01, 10^5] by leave-one-out CV"},
        {"Model": "LASSO", "Settings": "Standardized features; 100-value path; BIC with df < n/2"},
        {"Model": "Adaptive LASSO", "Settings": "As LASSO with weights 1/(|β_ridge| + 1/√n)"},
        {"Model": "Random forest", "Settings": "500 trees; a third of features per split; minimum leaf 5"},
        {"Model": "Gradient boosting", "Settings": "LightGBM; 500 rounds; learning rate 0.02; 15 leaves; minimum leaf 10; "
                                                   "80% row and column subsampling"},
        {"Model": "All", "Settings": "Rolling 120-month window; direct forecasts; seed 20261015"},
    ]), "Table A1. Model settings (fixed before estimation)")
    return n, t


if __name__ == "__main__":
    n, t = build()
    tpl = Path("paper/manuscript_template.md")
    import subprocess
    subprocess.run([sys.executable, "paper/results_text.py"], check=True)
    text_keys = json.loads(Path("paper/results_text.json").read_text())
    import jinja2
    env = jinja2.Environment(undefined=jinja2.StrictUndefined, comment_start_string="<#--", comment_end_string="--#>")
    for k, v in text_keys.items():  # prose blocks may reference numbers: {{ n.key }}
        n[k] = env.from_string(v).render(n=n)
    Path(TAB / "paper_numbers.json").write_text(json.dumps(n, indent=1, default=str))
    render(tpl, "paper/manuscript.md", numbers=TAB / "paper_numbers.json", bib="paper/references.bib",
           resource_path="paper:output/figures", tables=t)
