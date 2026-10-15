"""Forecast evaluation: loss ratios, Diebold-Mariano (HLN correction), model confidence set."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def rmse(e):
    return float(np.sqrt(np.mean(np.square(e))))


def dm_test(e1, e2, h: int, loss="sq"):
    """Diebold-Mariano test of equal accuracy, with the Harvey-Leybourne-Newbold correction.

    d_t = L(e1) - L(e2). H1 (one-sided): model 2 is more accurate (mean d > 0).
    Newey-West long-run variance with h-1 lags (rectangular, as in DM 1995; Bartlett
    fallback if the rectangular estimate is not positive). Returns (stat, p_one_sided).
    """
    e1, e2 = np.asarray(e1, float), np.asarray(e2, float)
    d = (e1 ** 2 - e2 ** 2) if loss == "sq" else (np.abs(e1) - np.abs(e2))
    n = len(d)
    if np.allclose(d, 0):  # identical forecasts: no evidence either way
        return 0.0, 0.5
    dbar = d.mean()
    dc = d - dbar
    gam = [np.sum(dc[k:] * dc[: n - k]) / n for k in range(h)]
    lrv = gam[0] + 2 * sum(gam[1:])
    if lrv <= 0:
        lrv = gam[0] + 2 * sum((1 - k / h) * gam[k] for k in range(1, h))
    dm = dbar / np.sqrt(lrv / n)
    corr = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    stat = dm * corr
    return float(stat), float(1 - stats.t.cdf(stat, df=n - 1))


def holm(pvals: pd.Series) -> pd.Series:
    """Holm step-down adjusted p-values."""
    p = pvals.sort_values()
    m = len(p)
    adj = np.maximum.accumulate([(m - i) * v for i, v in enumerate(p.values)])
    return pd.Series(np.minimum(adj, 1), index=p.index).reindex(pvals.index)


def mcs(losses: pd.DataFrame, size=0.10, reps=1000, seed=20261015) -> pd.Series:
    """Model confidence set p-values (Hansen, Lunde and Nason 2011), stationary bootstrap."""
    from arch.bootstrap import MCS
    m = MCS(losses, size=size, reps=reps, method="R", bootstrap="stationary", seed=seed)
    m.compute()
    return m.pvalues["Pvalue"]
