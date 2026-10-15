"""Phase 2 check: our year-on-year headline inflation, computed from the joined
index, against PSA's published year-on-year rates (Jan 2019-latest).
Writes output/tables/validation_yoy.csv."""
import numpy as np
import pandas as pd

MONTHS = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
cpi = pd.read_parquet("data/processed/cpi_long.parquet")
s = cpi[(cpi.geo == "PHILIPPINES") & (cpi.code == "0")].set_index("month")["index"]
ours = (100 * (s / s.shift(12) - 1)).rename("ours")
d = pd.read_csv("data/raw/psa/cpi_yoy_2018new_bycommodity_ph_2019_latest.csv.gz", dtype=str)
row = d[d["Commodity Description"].str.startswith("0 - ")].iloc[0]
cols = [c for c in d.columns if c[:4].isdigit() and c[5:8] in MONTHS]
pub = pd.Series(pd.to_numeric(row[cols].values, errors="coerce"),
                index=pd.PeriodIndex.from_fields(year=[int(c[:4]) for c in cols],
                                                 month=[MONTHS[c[5:8]] for c in cols], freq="M"),
                name="psa").dropna()
v = pd.concat([pub, ours], axis=1, join="inner")
v["diff"] = v.ours - v.psa
v.to_csv("output/tables/validation_yoy.csv")
print(f"months: {len(v)}, corr: {v.corr().iloc[0, 1]:.4f}, max |diff|: {v['diff'].abs().max():.2f} pp, "
      f"share |diff| <= 0.05pp: {(v['diff'].abs() <= 0.05).mean():.2f}")
