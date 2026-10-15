"""Direct multi-step forecasting engine (pseudo out-of-sample, rolling window).

For a forecast origin T and horizon h, a model is trained on pairs
(z_t, y_{t+h}) with t + h <= T (the last `window` such pairs) and then applied
to z_T. The features are z_t = [y_t..y_{t-p+1}, X_t..X_{t-L+1}, F_t..F_{t-L+1},
month dummies], where F are principal components of X computed inside the
training window only, so nothing after T is used.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import RidgeCV, lasso_path

warnings.filterwarnings("ignore", category=UserWarning)

SEED = 20261015
N_JOBS = 1  # threads per model; scripts parallelize over forecast origins instead


# --------------------------------------------------------------------------- features
@dataclass
class Design:
    y_lags: int = 12        # lags of the target in the data-rich models
    x_lags: int = 4         # lags 0..3 of every predictor (as in the reference)
    n_pc: int = 4           # principal components of X (within window)
    month_dummies: bool = True


def _lagged(a: np.ndarray, lags: int) -> np.ndarray:
    """Stack a (n x k) array with its lags 0..lags-1 -> (n x k*lags); NaN where unavailable."""
    n, k = a.shape
    out = np.full((n, k * lags), np.nan)
    for j in range(lags):
        out[j:, j * k:(j + 1) * k] = a[: n - j]
    return out


def pcs(x: np.ndarray, k: int) -> np.ndarray:
    """First k principal components of standardized x (rows = time)."""
    mu, sd = x.mean(0), x.std(0)
    sd[sd == 0] = 1
    z = (x - mu) / sd
    u, s, _ = np.linalg.svd(z, full_matrices=False)
    return u[:, :k] * s[:k]


def build_features(y: np.ndarray, x: np.ndarray | None, months: np.ndarray, d: Design,
                   use_x: bool = True) -> tuple[np.ndarray, list[str]]:
    """Feature matrix for every t in the (already truncated) sample."""
    blocks, names = [_lagged(y[:, None], d.y_lags)], [f"y_l{j}" for j in range(d.y_lags)]
    if use_x and x is not None and x.shape[1] > 0:
        blocks.append(_lagged(x, d.x_lags))
        names += [f"x{c}_l{j}" for j in range(d.x_lags) for c in range(x.shape[1])]
        if d.n_pc:
            blocks.append(_lagged(pcs(x, d.n_pc), d.x_lags))
            names += [f"pc{c}_l{j}" for j in range(d.x_lags) for c in range(d.n_pc)]
    if d.month_dummies:
        md = np.zeros((len(months), 11))
        for m in range(2, 13):
            md[:, m - 2] = months == m
        blocks.append(md)
        names += [f"m{m}" for m in range(2, 13)]
    return np.hstack(blocks), names


# --------------------------------------------------------------------------- models
def _std(a, b):
    mu, sd = a.mean(0), a.std(0)
    sd[sd == 0] = 1
    return (a - mu) / sd, (b - mu) / sd


def _ols_bic(Z, y):
    Z1 = np.column_stack([np.ones(len(Z)), Z])
    beta, *_ = np.linalg.lstsq(Z1, y, rcond=None)
    rss = np.sum((y - Z1 @ beta) ** 2)
    n = len(y)
    return n * np.log(rss / n) + Z1.shape[1] * np.log(n), beta


def fit_ar(ylags, md, ytr, zte_y, zte_md, pmax=12):
    """AR(p) (+ month dummies), p <= pmax by BIC; returns forecast and chosen p."""
    best = None
    for p in range(1, pmax + 1):
        Z = np.column_stack([ylags[:, :p], md]) if md is not None else ylags[:, :p]
        bic, beta = _ols_bic(Z, ytr)
        if best is None or bic < best[0]:
            zt = np.concatenate([zte_y[:p], zte_md]) if md is not None else zte_y[:p]
            best = (bic, beta[0] + zt @ beta[1:], p)
    return best[1], best[2]


def fit_factor(ylags, md, F, ytr, zte_y, zte_md, zte_F, pmax=12, kmax=4):
    best = None
    for p in range(1, pmax + 1):
        for k in range(0, kmax + 1):
            parts = [ylags[:, :p], F[:, :k]] + ([md] if md is not None else [])
            bic, beta = _ols_bic(np.column_stack(parts), ytr)
            if best is None or bic < best[0]:
                zt = np.concatenate([zte_y[:p], zte_F[:k]] + ([zte_md] if md is not None else []))
                best = (bic, beta[0] + zt @ beta[1:])
    return best[1]


def fit_ridge(Z, y, zte):
    Zs, zs = _std(Z, zte[None, :])
    m = RidgeCV(alphas=np.logspace(-2, 5, 60)).fit(Zs, y)  # efficient leave-one-out (GCV)
    return float(m.predict(zs)[0]), m


def _lasso_bic(Zs, y, zs, penalty_scale=None):
    """LASSO with the penalty chosen by BIC along the path (df < n/2, D12)."""
    yc = y - y.mean()
    if penalty_scale is not None:
        Zs, zs = Zs * penalty_scale, zs * penalty_scale
    alphas, coefs, _ = lasso_path(Zs, yc, alphas=100, eps=1e-3, max_iter=5000)
    n = len(y)
    best = None
    for i in range(len(alphas)):
        b = coefs[:, i]
        df = int(np.sum(b != 0))
        if df >= n / 2:
            continue
        rss = np.sum((yc - Zs @ b) ** 2)
        bic = n * np.log(rss / n) + df * np.log(n)
        if best is None or bic < best[0]:
            best = (bic, b)
    b = best[1]
    sel = b != 0
    return float(y.mean() + zs[0] @ b), sel


def fit_lasso(Z, y, zte):
    Zs, zs = _std(Z, zte[None, :])
    return _lasso_bic(Zs, y, zs)


def fit_adalasso(Z, y, zte):
    Zs, zs = _std(Z, zte[None, :])
    _, ridge = fit_ridge(Z, y, zte)
    w = np.abs(ridge.coef_) + 1 / np.sqrt(len(y))   # adaptive weights from a ridge first stage
    return _lasso_bic(Zs, y, zs, penalty_scale=w)


def fit_rf(Z, y, zte, seed=SEED, importance=False):
    m = RandomForestRegressor(n_estimators=500, max_features=1 / 3, min_samples_leaf=5,
                              n_jobs=N_JOBS, random_state=seed).fit(Z, y)
    return float(m.predict(zte[None, :])[0]), m


def fit_lgbm(Z, y, zte, seed=SEED):
    import lightgbm as lgb
    m = lgb.LGBMRegressor(n_estimators=500, learning_rate=0.02, num_leaves=15, min_child_samples=10,
                          subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                          random_state=seed, n_jobs=N_JOBS, verbose=-1).fit(Z, y)
    return float(m.predict(zte[None, :])[0])


ML_MODELS = ["ridge", "lasso", "adalasso", "rf", "lgbm"]
ALL_MODELS = ["rw", "rw_ao", "ar", "factor"] + ML_MODELS + ["combo"]


# --------------------------------------------------------------------------- driver
def forecast_origin(y: pd.Series, X: pd.DataFrame | None, T: int, h: int, window: int, d: Design,
                    models=ALL_MODELS, expanding=False, extra: dict | None = None) -> dict:
    """Forecasts of y[T+h] made at integer position T. Uses only data at positions <= T."""
    yv = y.to_numpy(float)[: T + 1]
    xv = None if X is None else X.to_numpy(float)[: T + 1]
    months = y.index.month.to_numpy()[: T + 1]
    out = {}
    if "rw" in models:
        out["rw"] = yv[T]
    if "rw_ao" in models:
        out["rw_ao"] = yv[T - 11: T + 1].mean()

    # training targets: pairs (t, t+h) with t+h <= T; keep the last `window`
    t_end = T - h
    t_start = 0 if expanding else t_end - window + 1
    AR_P = 12                                    # benchmark AR / factor lags, p <= 12 by BIC
    burn = max(d.y_lags, d.x_lags, AR_P) - 1
    if t_start < burn:
        raise ValueError(f"window too long for origin {T}: need t_start >= {burn}")
    lo = t_start - burn                          # features need lagged rows; PCs from rows lo..T
    xs = None if xv is None else xv[lo: T + 1]
    Zall, names = build_features(yv[lo: T + 1], xs, months[lo: T + 1], d, use_x=xv is not None)
    tr_rows = np.arange(t_start - lo, t_end - lo + 1)
    Z, ytr, zte = Zall[tr_rows], yv[tr_rows + lo + h], Zall[-1]
    assert np.isfinite(Z).all() and np.isfinite(zte).all()

    ylag_all = _lagged(yv[lo: T + 1, None], AR_P)
    ylag_tr, ylag_te = ylag_all[tr_rows], ylag_all[-1]
    md_idx = [i for i, n in enumerate(names) if n.startswith("m") and n[1:].isdigit()]
    md, md_te = (Z[:, md_idx], zte[md_idx]) if md_idx else (None, None)
    if "ar" in models:
        out["ar"], out["ar_p"] = fit_ar(ylag_tr, md, ytr, ylag_te, md_te)
    if "factor" in models and xv is not None:
        pc0 = [names.index(f"pc{c}_l0") for c in range(d.n_pc)]
        out["factor"] = fit_factor(ylag_tr, md, Z[:, pc0], ytr, ylag_te, md_te, zte[pc0])
    if "ridge" in models:
        out["ridge"], _ = fit_ridge(Z, ytr, zte)
    if "lasso" in models:
        out["lasso"], sel = fit_lasso(Z, ytr, zte)
        if extra is not None:
            extra["lasso_sel"] = sel
    if "adalasso" in models:
        out["adalasso"], _ = fit_adalasso(Z, ytr, zte)
    if "rf" in models:
        out["rf"], rf = fit_rf(Z, ytr, zte)
        if extra is not None:
            extra["rf"] = rf
            extra["Z"], extra["y"] = Z, ytr
    if "lgbm" in models:
        out["lgbm"] = fit_lgbm(Z, ytr, zte)
    ml = [out[m] for m in ML_MODELS if m in out]
    if "combo" in models and len(ml) == len(ML_MODELS):
        out["combo"] = float(np.mean(ml))
    if extra is not None:
        extra["names"] = names
    return out
