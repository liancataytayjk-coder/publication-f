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
LABEL = {"rw": "Random walk", "rw_ao": "Random walk, 12-month mean", "ar": "AR", "factor": "Factor (AR + PCs)",
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
