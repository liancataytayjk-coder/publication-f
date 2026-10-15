"""All figures, black and white, from the saved tables (no estimation here).

fig1_inflation      headline inflation 1994-2026, year on year, with the BSP target band
fig2_ratios         RMSE relative to AR by horizon, h = 1..12
fig3_csfe           cumulative squared forecast-error difference against AR, h = 1 and 12
fig4_importance     RF grouped permutation importance shares, h = 1 and 12
fig5_robustness     RMSE ratio to AR at the decisive cases across robustness checks
fig6_replication    replication gate: RMSE relative to RW on FRED-MD
fig7_yearahead      year-ahead inflation: actual against AR and combination forecasts
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fig_style import BLACK, DARK, LIGHT, MID, save, setup, zero  # noqa: E402

TAB = Path("output/tables")
FIG = Path("output/figures")
setup()

LABEL = {"rw": "Random walk", "rw_ao": "Random walk (12-month mean)", "ar": "AR", "factor": "Factor (AR + PCs)",
         "ridge": "Ridge", "lasso": "LASSO", "adalasso": "Adaptive LASSO", "rf": "Random forest",
         "lgbm": "Gradient boosting", "combo": "ML combination"}
STY = {
    "rf": dict(color=BLACK, linestyle="-", marker="o", markersize=3.5, markerfacecolor=BLACK),
    "combo": dict(color=BLACK, linestyle="--", marker="s", markersize=3.5, markerfacecolor="white"),
    "lasso": dict(color=DARK, linestyle=":", marker="^", markersize=3.5, markerfacecolor="white"),
    "ridge": dict(color=MID, linestyle="-.", marker="D", markersize=3, markerfacecolor=MID),
    "lgbm": dict(color=MID, linestyle="-", marker="v", markersize=3.5, markerfacecolor="white"),
    "factor": dict(color=DARK, linestyle="--", marker="x", markersize=3.5),
    "rw": dict(color=BLACK, linestyle=(0, (1, 2)), marker="", linewidth=1.0),
}
GROUP_LABEL = {"food": "Food", "energy_utilities": "Energy and utilities", "other_domestic": "Other domestic prices",
               "regional": "Regional inflation", "external_prices": "World prices", "money_fx": "Money and exchange rate",
               "own_lags": "Past inflation", "factors": "Factors (PCs)", "seasonal": "Month dummies"}


def fig1():
    cpi = pd.read_parquet("data/processed/cpi_long.parquet")
    s = cpi[(cpi.geo == "PHILIPPINES") & (cpi.code == "0")].set_index("month")["index"]
    s.index = s.index.to_timestamp()
    yoy = (100 * (s / s.shift(12) - 1)).dropna()
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    ax.axhspan(2, 4, color=LIGHT, linewidth=0, label="BSP target band, 2–4%")
    ax.plot(yoy.index, yoy.values, color=BLACK, linewidth=1.1, label="Headline inflation, year on year")
    ax.axvline(pd.Timestamp("2005-01-01"), color=BLACK, linestyle="--", linewidth=0.8)
    ax.text(pd.Timestamp("2005-04-01"), 0.3, "Forecast evaluation\nstarts Jan 2005", fontsize=8, va="bottom")
    zero(ax)
    ax.set_ylabel("Percent")
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.13), ncol=2, fontsize=8)
    save(fig, "fig1_inflation", FIG)


def fig2():
    acc = pd.read_csv(TAB / "accuracy.csv")
    m = acc[(acc.spec == "main") & acc.case.str.match(r"^h\d+$")].copy()
    m["h"] = m.case.str[1:].astype(int)
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.9), sharey=False)
    for ax, base in zip(axes, ("ar", "rw")):
        for mod in ("rf", "combo", "lasso", "ridge", "lgbm", "factor"):
            q = m[m.model == mod].sort_values("h")
            ax.plot(q.h, q[f"ratio_{base}"], label=LABEL[mod], **STY[mod])
        ax.axhline(1, color=BLACK, linewidth=0.6)
        ax.set_xticks(range(1, 13))
        ax.set_xlabel("Forecast horizon (months)")
        ax.set_ylabel(f"RMSE relative to {'AR' if base == 'ar' else 'random walk'}")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 1.08))
    fig.tight_layout()
    save(fig, "fig2_ratios", FIG)


def fig3():
    c = pd.read_csv(TAB / "csfe.csv", parse_dates=["target"])
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.9), sharey=False)
    for ax, h in zip(axes, (1, 12)):
        for mod in ("rf", "combo", "lasso"):
            q = c[(c.h == h) & (c.model == mod)]
            st = {k: v for k, v in STY[mod].items() if not k.startswith("marker")}
            ax.plot(q.target, q.csfe, label=LABEL[mod], **st)
        zero(ax)
        ax.set_xlabel(f"Target month (h = {h})")
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[0].set_ylabel("Cumulative squared error of AR\nminus that of the model")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 1.06))
    fig.tight_layout()
    save(fig, "fig3_csfe", FIG)


def fig4():
    imp = pd.read_csv(TAB / "importance.csv")
    piv = imp.pivot(index="group", columns="h", values="rf_share").sort_values(1)
    fig, ax = plt.subplots(figsize=(5.6, 3.1))
    y = np.arange(len(piv))
    ax.barh(y - 0.2, piv[1], height=0.38, color=MID, label="h = 1")
    ax.barh(y + 0.2, piv[12], height=0.38, color="white", edgecolor=BLACK, hatch="///", label="h = 12")
    ax.set_yticks(y, [GROUP_LABEL.get(g, g) for g in piv.index])
    ax.set_xlabel("Share of random-forest permutation importance")
    ax.legend(loc="lower right")
    save(fig, "fig4_importance", FIG)


def fig5():
    acc = pd.read_csv(TAB / "accuracy.csv")
    order = ["main", "expanding", "w96", "w180", "main_pre2020", "small", "join2018", "core"]
    names = {"main": "Main (120-month rolling)", "expanding": "(a) Expanding window", "w96": "(b) 96-month window",
             "w180": "(b) 180-month window", "main_pre2020": "(c) Targets up to Dec 2019",
             "small": "(d) World prices and money only", "join2018": "(f) Jan 2018 join dummy",
             "core": "(e) Core inflation target"}
    order = [o for o in order if o in set(acc.spec)]
    cases = [("h1", "h = 1"), ("h12", "h = 12"), ("acc3", "3-month accumulated"), ("acc12", "12-month accumulated")]
    fig, axes = plt.subplots(1, 4, figsize=(7.0, 3.2), sharey=True)
    y = np.arange(len(order))[::-1]
    for ax, (case, lab) in zip(axes, cases):
        for mod, st in (("rf", dict(marker="o", color=BLACK, linestyle="")),
                        ("combo", dict(marker="s", markerfacecolor="white", color=BLACK, linestyle=""))):
            v = [acc[(acc.spec == s) & (acc.case == case) & (acc.model == mod)].ratio_ar.iloc[0] for s in order]
            ax.plot(v, y + (0.12 if mod == "rf" else -0.12), label=LABEL[mod], markersize=4, **st)
        ax.axvline(1, color=BLACK, linewidth=0.6)
        ax.set_title(lab, fontsize=8)
        ax.set_xlabel("RMSE / AR")
    axes[0].set_yticks(y, [names[o] for o in order])
    axes[-1].legend(fontsize=7, loc="lower right")
    fig.tight_layout()
    save(fig, "fig5_robustness", FIG)


def fig6():
    r = pd.read_csv(TAB / "replication_ratios.csv")
    fig, ax = plt.subplots(figsize=(4.6, 2.9))
    for mod in ("rf", "lasso", "ridge"):
        q = r[r.model == mod]
        ax.plot(q.h, q.ratio_rw, label=LABEL[mod], **STY[mod])
    q = r[r.model == "ar"]
    ax.plot(q.h, q.ratio_rw, label="AR", **STY["factor"])
    ax.axhline(1, color=BLACK, linewidth=0.6)
    ax.set_xticks([1, 3, 6, 12])
    ax.set_xlabel("Forecast horizon (months)")
    ax.set_ylabel("RMSE relative to random walk")
    ax.legend(fontsize=7)
    save(fig, "fig6_replication", FIG)


def fig7():
    fc = pd.read_parquet("output/forecasts/main.parquet")
    sub = fc[fc.h <= 12]
    cnt = sub.groupby("origin")["h"].count()
    s = sub[sub.origin.isin(cnt[cnt == 12].index)].groupby("origin")[["actual", "ar", "combo", "rf"]].sum()
    s.index = [o + pd.DateOffset(months=12) for o in s.index]
    fig, ax = plt.subplots(figsize=(6.2, 2.9))
    ax.plot(s.index, s.actual, color=BLACK, linewidth=1.3, label="Actual")
    ax.plot(s.index, s.ar, color=MID, linestyle="--", linewidth=1.0, label="AR forecast")
    ax.plot(s.index, s.combo, color=BLACK, linestyle=":", linewidth=1.2, label="ML combination forecast")
    zero(ax)
    ax.set_ylabel("Inflation over 12 months\n(log points)")
    ax.set_xlabel("Last month of the 12-month period")
    ax.xaxis.set_major_locator(mdates.YearLocator(3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=7, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.12))
    save(fig, "fig7_yearahead", FIG)


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        try:
            f()
            print("ok", f.__name__)
        except FileNotFoundError as e:
            print("skip", f.__name__, e)
