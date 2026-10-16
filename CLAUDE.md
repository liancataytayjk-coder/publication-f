# Forecasting Philippine inflation with machine learning: project brief

**Working title.** *Can machine learning beat simple benchmarks in forecasting
Philippine inflation? A pseudo out-of-sample evaluation, 2005–2026.*

The study asks whether machine-learning (ML) models that use many predictors
forecast Philippine consumer price inflation more accurately than simple
benchmarks, and which predictors carry the gains. It replicates the design of
Medeiros, Vasconcelos, Veiga and Zilberman (2021, *Journal of Business &
Economic Statistics* 39(1), 98–119), "Forecasting inflation in a data-rich
environment: the benefits of machine learning methods", on official Philippine
Statistics Authority (PSA) data. Unit: the Philippines, monthly, 1994–2026.
Output: a journal manuscript (personal research). Target journal: *Journal of
Asian Economics* (Elsevier; chosen by the user 2026-10-16). Author: Lian
Cataytay, University of Southeastern Philippines (lrcataytay00745@usep.edu.ph). The user chose the topic (Philippine
inflation), the angle (ML against benchmarks) and asked us to propose the
reference paper and the journal (2026-10-15).

## Conventions

- `data/raw/` holds untouched downloads only. Every file gets an entry in
  `data/raw/source_log.md` (URL, date pulled, base year, coverage).
- `data/processed/` and `output/` are written by scripts, never by hand.
- `replication/medeiros2021_targets.csv` holds the reference paper's targets.
- No Philippine estimate is reported until the replication gate passes.
- Every specification choice goes in the decisions log below, with the
  evidence. Each is labelled pre-registered, supplementary or exploratory.
- Documents are rendered from templates. Never edit a rendered .md/.docx by hand.
- User style: as simple as possible. Define every term on first use (words →
  formula → example). Prefer paragraphs to bullets and tables.

## Research questions and hypotheses

**Main question.** Do data-rich ML models forecast Philippine inflation better
than simple benchmarks, and if so, when and why?

- **RQ1 (accuracy).** Do ML models (ridge, LASSO, adaptive LASSO, random
  forest, gradient boosting) and their combination have lower root mean squared
  error (RMSE) than the random walk (RW) and an autoregressive (AR) benchmark
  for headline inflation at horizons h = 1, …, 12 months, and for inflation
  accumulated over 3, 6 and 12 months?
  - *H1a (data-rich gains):* as in Medeiros et al. (2021) for the United
    States, the random forest beats both benchmarks.
  - *H1b (benchmark is hard to beat):* in a small emerging economy with a
    shorter history, an inflation-targeting regime change (2002) and frequent
    supply shocks (rice, oil, typhoons), the extra predictors add noise.
    Simple benchmarks are as good or better (Atkeson and Ohanian 2001; Stock and
    Watson 2007).
- **RQ2 (what predicts).** Which predictors carry the forecasting gains? We
  answer this with random-forest permutation importance and LASSO selection
  frequency, grouped into food (rice, cereals and other food), energy and
  utilities, other domestic prices, regional inflation, external prices and
  money and exchange rate.
  - *H2:* food (above all rice) and energy predictors dominate. They make up
    the largest weights of the Philippine CPI basket and the most volatile ones.
- **RQ3 (when).** Are the ML gains state dependent? We compare relative RMSE in
  calm months and in high-inflation episodes (2008, 2018, 2022–23), and track
  them over time with cumulative squared forecast-error differences.
  - *H3:* gains concentrate in volatile, high-inflation periods. Medeiros et
    al. report larger random-forest gains in periods of high uncertainty.

**Objectives.** Objective 1 (descriptive) covers trends, volatility, the
inflation episodes and the CPI weights. Objective 2 (estimation) answers RQ1,
RQ2 and RQ3. Objective 3 (policy) asks what the results imply for the BSP's
forecasting toolkit and its 2–4% target band. One example is the probability
that a model flags a breach of the band one year ahead (supplementary).

## Reference specification (Medeiros et al. 2021)

The full text is not reachable from this container. The publisher, SSRN and
GitHub are all blocked (2026-10-15). The elements below are taken from the
published abstract and the well-known design of the paper, and each is marked
as **to be confirmed against the PDF** (see Open questions).

- **Target.** Monthly US CPI inflation π_t = 100·Δln CPI_t, forecast directly
  for each h = 1, …, 12. Accumulated 3-, 6- and 12-month inflation is also
  evaluated. *(to confirm)*
- **Predictors.** FRED-MD (about 120 macro series, stationarity transforms),
  4 lags of each, plus 4 principal components (factors) and their lags.
  *(to confirm)*
- **Estimation.** Rolling window. Our recollection is 360 months. *(to confirm)*
- **Out-of-sample periods.** Two: 1990–2000 and 2001–2015. *(to confirm)*
- **Models.** RW and AR benchmarks; factor models; shrinkage (ridge, LASSO,
  adaptive LASSO, elastic net); complete subset regression (CSR); target
  factors; bagging; random forest (RF); hybrid RF; neural networks.
- **Headline finding (abstract).** ML with many predictors is systematically
  more accurate than the benchmarks, and RF dominates. Nonlinearity matters,
  and gains are larger when uncertainty is high.
- **Evaluation.** RMSE, MAE and median absolute deviation ratios against RW;
  model confidence set (Hansen, Lunde and Nason 2011); Giacomini–White tests.

## Decisions log

| # | Date | Decision | Evidence / reason | Label |
| --- | --- | --- | --- | --- |
| D1 | 2026-10-15 | Reference paper: Medeiros et al. (2021, JBES). | Most-cited data-rich ML inflation-forecasting design; public data (FRED-MD) allow a replication gate. User delegated the choice. | pre-registered |
| D2 | 2026-10-15 | Target variable: monthly headline inflation π_t = 100·Δln CPI_t (PSA, all income households, 2018=100, not seasonally adjusted). Accumulated inflation over k months = Σ of the direct forecasts for h = 1…k; k = 12 at origin t is the year-on-year rate that the BSP targets. | Follows the reference (D-ref target). The non-seasonally adjusted (NSA) series is the official published one; seasonality is handled by month dummies and 12 lags. | pre-registered |
| D3 | 2026-10-15 | Price data: PSA's own 2018=100 backcasts (Jan 1994–Dec 2017) joined to the current 2018=100 series (Jan 2018–), new geographic code. No splicing of different bases. The jump at the join is measured. | Skill rule: prefer the agency's backcasts on the current base. | pre-registered |
| D4 | 2026-10-15 | Direct forecasts: one model per horizon h, regressing π_{t+h} on information dated t. | As in the reference; avoids iterating nonlinear models. | pre-registered |
| D5 | 2026-10-15 | Rolling estimation window of 120 months (10 years). First origin Dec 2004, so the out-of-sample (OOS) target months run Jan 2005–latest. Expanding window as a robustness check. | 1994 start + 12 lags leaves about 130 months before 2005. The reference's 360-month window is impossible here; 120 months balances sample size against the 2002 regime change. | pre-registered |
| D6 | 2026-10-15 | Predictor set X_t (see Estimation plan). External series enter as 100·Δln (prices, FX) or first differences (rates). | Stationarity; the same units as the target. | pre-registered |
| D7 | 2026-10-15 | Rice: no long official world rice series to 2026 is reachable (the FRED IMF rice price starts 2010; the World Bank Pink Sheet link served ends Dec 2024). Use the FAO Cereals Price Index for world grain prices and the domestic CPI rice sub-index for rice. | Data availability, checked 2026-10-15. | pre-registered |
| D8 | 2026-10-15 | Replication gate (below) is qualitative (rankings and ratios < 1), because the paper's tables cannot be read from here. Numeric targets will be added if the user supplies the PDF; that would be logged as a new decision. | Skill rule: replicate what the data and documents allow; say so. | pre-registered |
| D9 | 2026-10-15 | World food and grain prices: the IMF food index, wheat and maize (FRED) replace the FAO indices named in the plan. | The FAO csv served ends Mar 2018. Changed before any estimate. | pre-registered |
| D10 | 2026-10-15 | The predictor set adds the food classes 01.1.1–01.1.9 and the energy classes 04.5.1, 04.5.2, 04.5.4 and 07.2.2. Division 04 (mostly rent) goes to the "other domestic" group. | At the division and group level alone, the food group had only 4 series, too coarse for H2. Changed before any estimate. | pre-registered |
| D11 | 2026-10-15 | Final predictor set: 86 series, complete Feb 1994–Jul 2026 (`output/tables/predictor_groups.csv`). Dropped 17: 16 CPI groups that start after 1994 and US CPI (Oct 2025 not published). | The rule in the plan: every model sees the same complete data. | pre-registered |
| D12 | 2026-10-15 | Implementation details, fixed before the gate is run: (i) LASSO and adaptive LASSO choose the penalty by BIC = n·ln(RSS/n) + df·ln(n) along a 100-point path, considering only models with df < n/2, so that the BIC cannot run off to a perfect in-sample fit when there are more predictors than months; (ii) adaptive LASSO weights are 1/(|β_ridge| + 1/√n); (iii) the AR and factor benchmarks always search p ≤ 12, independent of the lag design of the data-rich models; (iv) principal components are recomputed in every window from data up to the origin only; (v) the engine is tested for look-ahead (`tests/test_forecast.py`). A one-origin smoke test of `05_estimate.py` (Jun 2010, h = 12) was run to check the code; it is not an evaluation and is not reported. | Needed to make the plan computable; checked by the simulation tests. | pre-registered |
| D13 | 2026-10-15 | (i) The out-of-sample period is defined by forecast origin: origins Dec 2004 to Jul 2026 (the last month with all predictors), with each horizon's target observed by Sep 2026, so targets for horizon h start at Dec 2004 + h. (ii) At the first origins the 12 inflation lags leave fewer than 120 training months; the window then uses every available month (at least 108). | The first main run stopped with an error at the first origin before any forecast was saved: the plan's 'first origin Dec 2004' and 'window of 120' cannot both hold for h > 0. No result had been seen. | pre-registered (correction) |
| D14 | 2026-10-16 | Target journal: *Journal of Asian Economics* (user's choice). The Medeiros et al. (2021) PDF is not available to the user either, so the replication gate stays qualitative for good (D8); the manuscript says so. The journal's guide for authors is blocked from this container (403), so standard Elsevier items (highlights, title page, cover letter) are prepared and flagged for checking. | User, 2026-10-16. | supplementary (presentation only) |

## Replication gate (pre-registered 2026-10-15, before any estimate)

Data: FRED-MD current vintage (`data/raw/fredmd/`), standard transformation
codes, target CPIAUCSL monthly inflation 100·Δln. Design as in the reference
specification above: rolling 360-month window, 4 lags of every variable plus
4 principal components and their 4 lags, direct forecasts. Out-of-sample target
months Jan 2001–Dec 2015, horizons h ∈ {1, 3, 6, 12}. Models: RW
(π̂_{t+h|t} = π_t), AR(p) with p ≤ 12 chosen by BIC, ridge, LASSO (BIC) and
RF (500 trees, mtry = p/3, minimum leaf size 5).

- **G1.** RF/RW RMSE ratio < 1 at every h ∈ {1, 3, 6, 12}.
- **G2.** RF/AR RMSE ratio, averaged over the four horizons, < 1.
- **G3.** RF has the lowest average RMSE (over the four horizons) of the five
  models.

The gate passes if G1, G2 and G3 all hold. If it fails, stop, re-read the
specification, fix the code and record what changed. Pass ranges are not
loosened after the results are seen.

**Result (2026-10-15): PASS.** `output/tables/replication_gate.csv`, 720 forecasts.
RMSE relative to RW at h = 1, 3, 6, 12: RF 0.894, 0.714, 0.719, 0.688; LASSO 0.867,
0.730, 0.750, 0.699; AR 0.913, 0.766, 0.760, 0.729; ridge 0.908, 0.807, 0.830, 0.731.
G1 holds at every horizon; G2: mean RF/AR = 0.950; G3: average RMSE RF 0.3257 <
LASSO 0.3302 < AR 0.3431 < ridge 0.3558 < RW 0.4385. Note the RF margin over
LASSO is small, and LASSO is better than RF at h = 1.

## Estimation plan (pre-specified 2026-10-15, before any Philippine estimate)

**Common settings.** Target π_t (D2). Direct forecasts h = 1…12 (D4). Rolling
120-month window (D5). OOS target months Jan 2005 to the latest month available
(Sep 2026 at the time of writing). The forecast origin is t: information
through month t, as published. CPI is released in the first week of t+1, and
monthly external data are available by then. Final-vintage data; PSA rarely
revises the CPI except when rebasing, which is a limitation we will note.

**Predictor set X_t** (each with lags 0–3, i.e. 4 lags, as in the reference),
plus 12 lags of π, 11 month dummies, and 4 principal components of the
standardized predictors with their 4 lags:

1. National CPI sub-indices (PSA, 100·Δln): the 13 COICOP divisions and every
   available group/class at the 3-digit level, together with the rice item.
2. Core CPI (PSA, 100·Δln).
3. Regional headline CPI for the 17 regions (PSA, 100·Δln).
4. External: Brent and Dubai crude (FRED, USD, 100·Δln); FAO Food and Cereals
   Price Indices (100·Δln); IMF all-commodities index (FRED, 100·Δln); US CPI
   (FRED, NSA, 100·Δln); US federal funds rate (Δ).
5. Money and exchange rate: PHP per USD, monthly average (BIS, 100·Δln); BSP
   policy rate (BIS, Δ); crude oil in pesos (100·Δln).

Series with any gap after Jan 1994 are dropped, so that every model sees the
same data. The final count is logged in Phase 2.

**Models.**
- Benchmarks: RW (π̂_{t+h|t} = π_t); RW-AO (mean of π over the last 12 months;
  Atkeson and Ohanian 2001); AR(p) with month dummies, p ≤ 12 by BIC.
- Factor model: AR + the first k ≤ 4 principal components of X (diffusion
  index; Stock and Watson 2002), k and p by BIC.
- Shrinkage on the full set: ridge (penalty by generalized cross-validation),
  LASSO (penalty by BIC), adaptive LASSO (ridge first stage, BIC).
- Trees: RF (500 trees, mtry = p/3, minimum leaf 5); gradient boosting
  (LightGBM: 500 rounds, learning rate 0.02, 15 leaves, minimum leaf 10,
  80% row and column subsampling). The hyperparameters are fixed in advance
  and not tuned on the OOS period.
- Combination: equal-weight mean of the five ML models (ridge, LASSO, adaLASSO,
  RF, LightGBM).
- All models use a fixed random seed, 20261015.

**RQ1 evaluation.** RMSE and MAE ratios against RW and against AR, for each
h = 1…12 and for accumulated k = 3, 6, 12. Diebold–Mariano tests with the
Harvey–Leybourne–Newbold small-sample correction, squared loss, Newey–West
variance with h−1 lags. RQ1 is judged on the four decisive cases: h = 1,
h = 12, accumulated 3-month and accumulated 12-month. A model "beats" a
benchmark when its ratio is < 1 and the one-sided DM p < 0.05. We also run the
model confidence set (MCS, 90%, block bootstrap, 1,000 replications) at each
decisive case. Multiple testing: we report the DM tests for the 8 ML and factor
models × 4 decisive cases, and say which survive a Holm correction within each
benchmark.

**RQ2.** Grouped importance from RF permutation importance (on each window's
training data, averaged over origins at h = 1 and h = 12) and LASSO selection
frequency (the share of origins in which any variable of a group is selected).
The groups are fixed in Phase 2 before estimation and saved to
`output/tables/predictor_groups.csv`.

**RQ3.** Relative RMSE within two pre-defined regimes: *high-inflation*
months, where the year-on-year headline inflation at the target month is above
4% (the top of the BSP target band), and the rest. We also plot cumulative
squared forecast-error differences (CSFE) against AR over time, for RF, LASSO
and the combination, at h = 1 and 12.

**Robustness.** (a) Expanding window. (b) A 96-month and a 180-month rolling
window. (c) The sample ending Dec 2019, without the pandemic and the 2022–23
surge. (d) A small predictor set: external and money variables only (no CPI
components). (e) Core inflation as the target (secondary target). (f) A dummy
for the Jan 2018 join month. Robustness is reported for the four decisive cases.

## Results (2026-10-15; `output/tables/accuracy.csv`, main specification)

- **RQ1 — H1b supported (benchmark hard to beat).** Every model beats the RW
  (AR/RW RMSE 0.83 at h = 1). No challenger beats the AR at any decisive case.
  Relative RMSE to AR: combination 0.98 (h1), 1.01 (h12),
  0.98 (acc3), 1.03 (acc12); RF 0.99, 1.01,
  0.99, 1.04. Smallest DM p = 0.32; smallest Holm p = 1.00.
  The AR is in the 90% MCS in every case. Ridge and LightGBM are worse than the AR
  (up to +40% and +11%). The AR picks p = 1 at the median.
- **RQ2 — H2 partly supported.** RF importance, h = 1: food 26%, regional
  23%, other domestic 23%, world prices 9%,
  energy 5%. At h = 12, other domestic 50%. Energy is *not* dominant.
  Importance is in-sample (training windows) and descriptive.
- **RQ3 — H3 not supported.** h = 1 combination: 0.98 (high-inflation months)
  versus 0.99 (other months). acc12 RF: 1.00 versus 1.07.
  No model anticipates the 2008, 2018, 2022–23 or 2026 episodes a year ahead (fig7).
  Exploratory: in May 2026 the AR carried the April jump forward (1.48% forecast versus
  -0.51% actual), while the combination gave 0.62%.
- **Robustness (2026-10-16; six of seven checks done).** 96- and 180-month windows,
  targets to Dec 2019, world prices and money only, Jan 2018 join dummy: best
  challenger 0.97–0.98, and none of the DM tests rejects at 5%. Core inflation target: RF 0.95 and
  combination 0.95 at h = 1, combination 0.94 at acc3 (DM p = 0.061; Holm 1.00); weak
  evidence only. The expanding window is still running (`output/estimate_expanding_log.txt`;
  it checkpoints each horizon in `output/forecasts/_parts/`, so it resumes after a container restart).
  When it finishes, run `06_evaluate.py`, `07_figures.py` and `08_paper.py`, check the robustness paragraph, commit and push.

## Documents

- `paper/manuscript_template.md` + `paper/results_text.py` (prose with {{ n.* }} numbers) → `scripts/08_paper.py` → `paper/manuscript.md` / `.docx`; numbers in `output/tables/paper_numbers.json`

## Pipeline

`./run_all.sh` rebuilds everything from `data/raw/` (`--download` to refresh).

## Open questions

- [x] Reference PDF: not available (user, 2026-10-16). The gate stays qualitative (D14).
- [x] Target journal: *Journal of Asian Economics* (D14).
- [ ] Check the manuscript against the *Journal of Asian Economics* guide for authors
      (word limit, abstract length, highlights, anonymized review) — blocked here.
- [ ] Would the user like the BSP's own published inflation forecasts (Monetary
      Policy Report) as an extra benchmark? Hand-collected, so not in the pipeline yet.
