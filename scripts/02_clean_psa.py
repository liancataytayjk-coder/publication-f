"""Clean PSA CPI downloads into long tables (geo x item x month), 2018=100.

Joins PSA's own backcasts (Jan 1994-Dec 2017) to the current series (Jan 2018-)
on the same base (D3); no rescaling. Writes
  data/processed/cpi_long.parquet      geo, code, label, month, index
  data/processed/core_ph.parquet       month, core index
  data/processed/cpi_weights.parquet   geo, code, label, weight
  output/tables/join_check.csv         size of the Dec 2017 -> Jan 2018 change
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/raw/psa")
OUT = Path("data/processed")
TAB = Path("output/tables")
OUT.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}


def wide_to_long(path):
    d = pd.read_csv(path, dtype=str)
    d = d.rename(columns={"Geolocation": "geo", "Commodity Description": "item"})
    cols = [c for c in d.columns if c not in ("geo", "item") and not c.endswith("Ave")]
    long = d.melt(id_vars=["geo", "item"], value_vars=cols, var_name="ym", value_name="index")
    yr = long["ym"].str[:4].astype(int)
    mo = long["ym"].str[5:8].map(MONTHS)
    long["month"] = pd.PeriodIndex.from_fields(year=yr, month=mo, freq="M")
    long["index"] = pd.to_numeric(long["index"], errors="coerce")  # '..' = not available
    long["geo"] = long["geo"].str.replace(r"^\.+", "", regex=True).str.strip()
    long["code"] = long["item"].str.split(" - ").str[0].str.strip()
    long["label"] = long["item"].str.split(" - ", n=1).str[1].str.strip()
    return long.dropna(subset=["index"])[["geo", "code", "label", "month", "index"]]


back = wide_to_long(RAW / "cpi_all_2018new_backcast_bycommodity_regions_1994_2017.csv.gz")
cur = wide_to_long(RAW / "cpi_all_2018new_bycommodity_regions_2018_latest.csv.gz")
assert back["month"].max() < cur["month"].min()
cpi = pd.concat([back, cur], ignore_index=True).sort_values(["geo", "code", "month"])
cpi.to_parquet(OUT / "cpi_long.parquet", index=False)
print(f"cpi_long: {len(cpi):,} rows, {cpi.geo.nunique()} geos, {cpi.code.nunique()} items, "
      f"{cpi.month.min()}..{cpi.month.max()}")

# Join check (D3): the Dec 2017 -> Jan 2018 log change against the typical January change.
cpi["dl"] = cpi.groupby(["geo", "code"])["index"].transform(lambda s: 100 * np.log(s).diff())
jan = cpi[cpi["month"].dt.month == 1]
rows = []
for (g, c), s in jan.groupby(["geo", "code"]):
    if g not in ("PHILIPPINES",) or c.count(".") > 1:
        continue
    j = s.loc[s["month"] == pd.Period("2018-01", "M"), "dl"]
    other = s.loc[s["month"] != pd.Period("2018-01", "M"), "dl"].dropna()
    if len(j) and len(other) > 5:
        rows.append({"geo": g, "code": c, "dl_join": j.iloc[0], "mean_jan": other.mean(),
                     "sd_jan": other.std(), "z": (j.iloc[0] - other.mean()) / other.std()})
jc = pd.DataFrame(rows)
jc.to_csv(TAB / "join_check.csv", index=False)
print("join check (national, divisions and groups):",
      f"median |z| = {jc.z.abs().median():.2f}, share |z|>2 = {(jc.z.abs() > 2).mean():.2f}")
print(jc[jc.code == "0"].round(3).to_string(index=False))

# Core CPI: backcast (Period x Year) + current (by commodity; keep all items)
cb = pd.read_csv(RAW / "cpi_core_2018new_backcast_allitems_ph_1994_2017.csv.gz", dtype=str)
cb = cb[cb["Period"] != "Average"].melt(id_vars="Period", var_name="year", value_name="core")
cb["month"] = pd.PeriodIndex.from_fields(year=cb["year"].astype(int),
                                         month=cb["Period"].str[:3].map(MONTHS), freq="M")
cc = wide_to_long(RAW / "cpi_core_2018new_bycommodity_ph_2018_latest.csv.gz")
cc = cc[cc.code == "0"].rename(columns={"index": "core"})
core = pd.concat([cb[["month", "core"]].assign(core=lambda d: pd.to_numeric(d.core, errors="coerce")),
                  cc[["month", "core"]]]).dropna().sort_values("month")
core.to_parquet(OUT / "core_ph.parquet", index=False)
print(f"core: {core.month.min()}..{core.month.max()}, n={len(core)}")

w = pd.read_csv(RAW / "cpi_weights_2018new_bycommodity_regions.csv.gz", dtype=str)
w = w.rename(columns={"Geolocation": "geo", "Commodity Description": "item", "Weights": "weight"})
w["geo"] = w["geo"].str.replace(r"^\.+", "", regex=True).str.strip()
w["code"] = w["item"].str.split(" - ").str[0].str.strip()
w["label"] = w["item"].str.split(" - ", n=1).str[1].str.strip()
w["weight"] = pd.to_numeric(w["weight"], errors="coerce")
w[["geo", "code", "label", "weight"]].to_parquet(OUT / "cpi_weights.parquet", index=False)
