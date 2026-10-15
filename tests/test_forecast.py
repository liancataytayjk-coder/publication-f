"""Phase 3 simulation tests: the engine recovers known forecasts, never looks ahead,
and the Diebold-Mariano test has the right size."""
import numpy as np
import pandas as pd
import pytest

from phfx.evaluate import dm_test, holm, rmse
from phfx.forecast import Design, forecast_origin

RNG = np.random.default_rng(1)
IDX = pd.date_range("1990-01-01", periods=400, freq="MS")


def ar1(n=400, phi=0.6, rng=RNG):
    y = np.zeros(n)
    e = rng.standard_normal(n)
    for t in range(1, n):
        y[t] = phi * y[t - 1] + e[t]
    return y


def test_no_lookahead():
    """Changing data after the origin must not change any forecast."""
    y = pd.Series(ar1(), index=IDX)
    X = pd.DataFrame(RNG.standard_normal((400, 6)), index=IDX)
    d = Design(y_lags=4, x_lags=2, n_pc=2)
    f1 = forecast_origin(y, X, T=300, h=3, window=120, d=d)
    y2, X2 = y.copy(), X.copy()
    y2.iloc[301:] += 50
    X2.iloc[301:] *= -7
    f2 = forecast_origin(y2, X2, T=300, h=3, window=120, d=d)
    for k in f1:
        assert f1[k] == pytest.approx(f2[k]), k


def test_ar_recovers_oracle():
    """Direct AR forecasts approach the oracle phi^h * y_T on an AR(1)."""
    phi = 0.6
    y = pd.Series(ar1(phi=phi), index=IDX)
    d = Design(y_lags=12, month_dummies=False)
    for h in (1, 3):
        err_m, err_o = [], []
        for T in range(200, 399 - h):
            f = forecast_origin(y, None, T, h, window=150, d=d, models=["ar"])
            err_m.append(y.iloc[T + h] - f["ar"])
            err_o.append(y.iloc[T + h] - phi ** h * y.iloc[T])
        assert rmse(err_m) / rmse(err_o) < 1.08


def test_sparse_signal_lasso_and_rf_beat_rw():
    """y_{t+1} = 0.9 x1_t + noise among 30 noise predictors: LASSO picks x1; LASSO and RF beat RW."""
    rng = np.random.default_rng(7)
    n = 330
    x = rng.standard_normal((n, 30))
    y = np.zeros(n)
    y[1:] = 0.9 * x[:-1, 0] + 0.3 * rng.standard_normal(n - 1)
    ys, X = pd.Series(y, index=IDX[:n]), pd.DataFrame(x, index=IDX[:n])
    d = Design(y_lags=2, x_lags=1, n_pc=0, month_dummies=False)
    errs = {"rw": [], "lasso": [], "rf": []}
    picked = 0
    for T in range(250, n - 1, 4):
        extra = {}
        f = forecast_origin(ys, X, T, 1, window=150, d=d, models=["rw", "lasso", "rf"], extra=extra)
        for k in errs:
            errs[k].append(y[T + 1] - f[k])
        names = extra["names"]
        picked += extra["lasso_sel"][names.index("x0_l0")]
    assert picked == len(errs["rw"])
    assert rmse(errs["lasso"]) / rmse(errs["rw"]) < 0.5
    assert rmse(errs["rf"]) / rmse(errs["rw"]) < 0.8


def test_dm_size_and_power():
    rng = np.random.default_rng(3)
    rej = 0
    for _ in range(600):
        e1, e2 = rng.standard_normal(150), rng.standard_normal(150)
        rej += dm_test(e1, e2, h=1)[1] < 0.05
    assert 0.02 <= rej / 600 <= 0.09
    rej = 0
    for _ in range(200):
        e1, e2 = 1.5 * rng.standard_normal(150), rng.standard_normal(150)
        rej += dm_test(e1, e2, h=1)[1] < 0.05
    assert rej / 200 > 0.8


def test_holm():
    p = pd.Series([0.01, 0.04, 0.03])
    assert holm(p).round(3).tolist() == [0.03, 0.06, 0.06]
