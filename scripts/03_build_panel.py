"""Build the monthly analysis panel for the Philippine forecasting study.

Rows are months. Columns: the target pi (100*dln headline CPI) and the
predictor set X (D6), all as 100*dln (prices, FX) or first differences (rates).
Series with any gap between Jan 1994 and the panel end are dropped so that all
models see the same data. Also writes the predictor groups for RQ2.

Outputs
  data/processed/panel.parquet
  output/tables/predictor_groups.csv   variable, group, label, source
  output/tables/panel_summary.csv
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

P = Path("data/processed")
RAW = Path("data/raw")
TAB = Path("output/tables")


def dln(s):
    return 100 * np.log(s).diff()


cpi = pd.read_parquet(P / "cpi_long.parquet")
cpi["month"] = cpi["month"].astype("period[M]")
nat = cpi[cpi.geo == "PHILIPPINES"]
wide = nat.pivot(index="month", columns="code", values="index").sort_index()
labels = nat.drop_duplicates("code").set_index("code")["label"]

panel = pd.DataFrame(index=wide.index)
panel["pi"] = dln(wide["0"])
meta = []

# 1. National CPI divisions and groups (level <= 1) and rice
# D10: add the food classes 01.1.1-01.1.9 and the energy classes (electricity, gas,
# solid fuels, motor fuels), fixed before any estimate.
FOOD_ENERGY_CLASSES = [f"01.1.{i}" for i in range(1, 10)] + ["04.5.1", "04.5.2", "04.5.4", "07.2.2"]
codes = [c for c in wide.columns if c != "0" and c.count(".") <= 1] + FOOD_ENERGY_CLASSES + ["01.1.1.12"]
for c in codes:
    v = "cpi_" + c.replace(".", "_")
    panel[v] = dln(wide[c])
    if c.startswith("01") or c == "01.1.1.12":
        grp = "food"
    elif c.startswith(("04.4", "04.5", "07.2")):
        grp = "energy_utilities"
    else:
        grp = "other_domestic"
    meta.append((v, grp, labels.get(c, c), "PSA CPI " + c))

# 2. Core CPI
core = pd.read_parquet(P / "core_ph.parquet")
core["month"] = core["month"].astype("period[M]")
panel["core"] = dln(core.set_index("month")["core"]).reindex(panel.index)
meta.append(("core", "other_domestic", "Core CPI", "PSA core CPI"))

# 3. Regional headline CPI
reg = cpi[(cpi.code == "0") & ~cpi.geo.isin(["PHILIPPINES", "Areas Outside National Capital Region (AONCR)"])]
for g, s in reg.groupby("geo"):
    v = "reg_" + "".join(ch for ch in g.split("(")[-1] if ch.isalnum())[:12]
    panel[v] = dln(s.set_index("month")["index"]).reindex(panel.index)
    meta.append((v, "regional", g, "PSA regional CPI"))


# 4-5. External series
def fred(code):
    d = pd.read_csv(RAW / f"fred/{code}.csv.gz")
    d["month"] = pd.PeriodIndex(pd.to_datetime(d["observation_date"]), freq="M")
    return pd.to_numeric(d.set_index("month")[code], errors="coerce")


def bis(name):
    d = pd.read_csv(RAW / f"bis/{name}.csv.gz")
    d["month"] = pd.PeriodIndex(d["TIME_PERIOD"], freq="M")
    return pd.to_numeric(d.set_index("month")["OBS_VALUE"], errors="coerce")


php = bis("WS_XRU_M_PH_PHP_A")
ext = {
    "brent": (dln(fred("POILBREUSDM")), "external_prices", "Brent crude, USD"),
    "dubai": (dln(fred("POILDUBUSDM")), "external_prices", "Dubai crude, USD"),
    "imf_allcomm": (dln(fred("PALLFNFINDEXM")), "external_prices", "IMF all-commodities index"),
    "imf_food": (dln(fred("PFOODINDEXM")), "external_prices", "IMF food price index"),
    "wheat": (dln(fred("PWHEAMTUSDM")), "external_prices", "Wheat, USD/mt"),
    "maize": (dln(fred("PMAIZMTUSDM")), "external_prices", "Maize, USD/mt"),
    "us_cpi": (dln(fred("CPIAUCNS")), "external_prices", "US CPI, NSA"),
    "brent_php": (dln(fred("POILDUBUSDM") * php), "external_prices", "Dubai crude in pesos"),
    "fedfunds": (fred("FEDFUNDS").diff(), "money_fx", "US federal funds rate (change)"),
    "php_usd": (dln(php), "money_fx", "Peso per US dollar"),
    "bsp_rate": (bis("WS_CBPOL_M_PH").diff(), "money_fx", "BSP policy rate (change)"),
}
for v, (s, grp, lab) in ext.items():
    panel[v] = s.reindex(panel.index)
    src = "BIS" if v in ("php_usd", "bsp_rate") else "FRED"
    meta.append((v, grp, lab, src))

# Panel window: Feb 1994 (first change) to the last month with every external series
panel = panel.loc["1994-02":]
xcols = [c for c in panel.columns if c != "pi"]
last_x = panel[["brent", "imf_food", "php_usd", "bsp_rate", "us_cpi"]].dropna().index.max()
inside = panel.loc[:last_x, xcols]
complete = inside.columns[inside.notna().all()]
dropped = sorted(set(xcols) - set(complete))
print(f"predictors: {len(xcols)} candidates, {len(complete)} complete Feb 1994-{last_x}; dropped {len(dropped)}:")
print("  ", dropped)
panel = panel[["pi"] + list(complete)]
panel.attrs["last_x"] = str(last_x)
panel.index = panel.index.to_timestamp()
panel.to_parquet(P / "panel.parquet")

groups = pd.DataFrame(meta, columns=["variable", "group", "label", "source"])
groups = groups[groups.variable.isin(complete)]
groups.to_csv(TAB / "predictor_groups.csv", index=False)
print(groups.group.value_counts().to_string())

summ = pd.DataFrame({"first": [panel.index.min().strftime("%Y-%m")],
                     "last_target": [panel["pi"].dropna().index.max().strftime("%Y-%m")],
                     "last_predictors": [str(last_x)], "n_predictors": [len(complete)],
                     "n_dropped": [len(dropped)]})
summ.to_csv(TAB / "panel_summary.csv", index=False)
print(summ.to_string(index=False))
