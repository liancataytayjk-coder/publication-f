---
title: "Can Machine Learning Beat Simple Benchmarks in Forecasting Philippine Inflation? Evidence from a Pre-Registered Pseudo Out-of-Sample Evaluation, 2005–2026"
author: "[Author name], [Affiliation], [email]"
date: "Draft of {{ n.build_date }}"
abstract: |
  {{ n.abstract }}
keywords: "inflation forecasting; machine learning; random forest; LASSO; forecast evaluation; Philippines; emerging markets"
---

<#-- Rendered by scripts/08_paper.py. Do not edit paper/manuscript.md by hand; edit this template. --#>

**JEL codes:** C53, C55, E31, E37.

# 1. Introduction

Inflation forecasts sit at the centre of monetary policy. The Bangko Sentral ng
Pilipinas (BSP) has targeted inflation since 2002, and under a forward-looking
regime the policy rate responds to where inflation is *expected* to be one to two
years ahead, not where it is today. A better forecast therefore means better-timed
policy. The Philippine case is also a hard one. Food is
{{ n.w_food }}% of the consumer basket and rice alone is {{ n.w_rice }}%
(Philippine Statistics Authority, 2018 weights). Rice and oil are largely
imported, and typhoons hit farm output every year. As a result, Philippine
inflation swings much more than inflation in advanced economies. Since 2005 it
has left the 2–4% target band in {{ n.share_outside_band }}% of months
(Figure 1), and the most recent episode, an oil-price shock in early 2026, pushed
it to {{ n.yoy_latest }}% in {{ n.latest_month }}.

Machine-learning (ML) methods promise better forecasts when there are many
possible predictors. They do this in two ways: they *shrink* or *select* among
predictors so that noise does not swamp the signal, and some of them (tree-based
methods) also capture *nonlinear* relationships. The most influential evidence is
@medeiros2021. Using about 120 US macroeconomic series, they find that a
random forest (RF) forecasts US consumer price inflation more accurately than
the standard benchmarks at every horizon, and that the gains are largest when
uncertainty is high. Similar comparisons for Brazil [@garcia2017; @araujo2023]
and for a broad set of US variables [@gouletcoulombe2022] support the view that
ML helps. But the classic finding of inflation forecasting points the other way:
simple univariate benchmarks are very hard to beat [@atkeson2001; @stock2007;
@faust2013].

This paper asks which of these two findings holds for the Philippines. We
replicate the design of @medeiros2021 on official monthly data from the
Philippine Statistics Authority (PSA), 1994–2026, and compare five ML models,
their combination and a factor model with three benchmarks over
{{ n.n_oos }} out-of-sample months (January 2005 to {{ n.oos_end }}). We ask three
research questions. RQ1: are the ML models more accurate than the benchmarks?
RQ2: which predictors carry the gains? RQ3: are the gains larger in
high-inflation periods?

The paper makes three contributions. First, to our knowledge it is the first
systematic evaluation of data-rich ML inflation forecasts for the Philippines,
using the full detail of the PSA consumer price index (CPI): 13 food and energy
classes, the remaining divisions and groups, and all 18 regional indices.
Second, the design was *pre-registered*. The research questions, models,
hyperparameters, evaluation sample, tests and robustness checks were written
down and committed to a public version-control history before any Philippine
forecast was computed. A replication of the reference paper's main finding on
US data served as a gate that had to pass before we could proceed. This
guards against the "garden of forking paths" that is common in horse races
between many models. Third, we show *where* the gains come from: which groups of
predictors matter and in which inflation regimes.

{{ n.intro_findings }}

The rest of the paper is organised as follows. Section 2 describes the data,
Section 3 the models and the evaluation, and Section 4 the replication gate.
Section 5 presents the results by research question, Section 6 the robustness
checks, and Section 7 discusses the findings and concludes.

# 2. Data

**Target.** The target is monthly headline inflation, defined as the log change
of the all-items CPI for all income households (2018 = 100):

$$\pi_t = 100 \times \ln\left(\frac{P_t}{P_{t-1}}\right). \qquad (1)$$

For example, if the CPI rises from 120.0 to 120.6, then
$\pi_t = 100 \ln(120.6/120.0) \approx 0.50$, a monthly rate of about half a
percent. Inflation over the next $k$ months is the sum
$\pi_{t+1} + \dots + \pi_{t+k}$. For $k = 12$ this is, to a close
approximation, the year-on-year rate that the BSP targets. We use the official
series, which is not seasonally adjusted. All models therefore include month
dummies and twelve lags of inflation, so that regular patterns such as higher
prices every December do not show up as forecast errors.

The PSA publishes the 2018-based CPI from January 2018 and its *own* backcasts
of the same indices on the same base for January 1994 to December 2017. We join
the two without any rescaling. The January 2018 change in headline inflation at
the join is ordinary: it lies {{ n.join_z }} standard deviations from the
average January change. Our computed year-on-year inflation matches the PSA's
published rates for every month from 2019 to {{ n.latest_month }} to within
{{ n.val_maxdiff }} percentage points.

**Predictors.** The predictor set contains {{ n.n_pred }} monthly series that
are complete from February 1994 to {{ n.last_x }}. Table 1 lists them by group.
They are the 13 COICOP divisions and their groups in the national CPI, the food
classes (cereals, meat, fish, dairy, oils, fruit, vegetables, sugar and other
food) and rice, the energy classes (electricity, gas, solid fuels and motor
fuels), core inflation, and headline inflation in each of the 18 regions. They
also include world prices: Brent and Dubai crude oil, the International Monetary
Fund (IMF) all-commodities and food indices, wheat, maize, and Dubai crude in
pesos. Finally, they include the peso–dollar exchange rate, the BSP policy rate
and the US federal funds rate. Prices and the exchange rate enter as log changes
(as in Equation 1), and interest rates as first differences. Series that start
after 1994 are dropped, so that every model sees the same information. This
removes 16 small CPI groups and US CPI, whose October 2025 value was never
published.

{{ t.table1 }}

# 3. Forecasting models and evaluation

## 3.1 Direct forecasts in a rolling window

We forecast inflation $h = 1, \dots, 12$ months ahead with *direct* forecasts.
For each horizon we fit a separate model that maps information available at
month $t$ into inflation at month $t+h$:

$$\pi_{t+h} = f_h(z_t) + \varepsilon_{t+h}, \qquad (2)$$

and the forecast made at origin $T$ is $\hat\pi_{T+h|T} = \hat f_h(z_T)$. The
information vector $z_t$ contains twelve lags of inflation, the current value
and three lags of every predictor (as in @medeiros2021), the first four
principal components of the predictors and their three lags, and eleven month
dummies, {{ n.n_features }} features in all. The principal components are
recomputed in every window from data up to the origin only.

Each model is re-estimated at every origin on the most recent 120 months, a
*rolling window*. The window lets the models adapt to change, such as the start
of inflation targeting in 2002 or the 2018 rebasing, while keeping enough
months for estimation. The first origin is December 2004, so the first forecast
target is January 2005. Because the forecasts at each origin use only data
available at that origin, they are *pseudo out-of-sample* forecasts: they mimic
what a forecaster could have done in real time, apart from data revisions,
which are rare for the Philippine CPI.

## 3.2 Models

There are three **benchmarks**. The *random walk* (RW) forecasts that inflation
in month $t+h$ equals this month's inflation, $\hat\pi_{T+h|T} = \pi_T$, as in
@medeiros2021. The *12-month-mean random walk* (RW-AO) of @atkeson2001
forecasts the average of the last twelve months. The *autoregressive* (AR)
model regresses $\pi_{t+h}$ on a constant, month dummies and $p$ lags of
inflation, with $p \le 12$ chosen by the Bayesian information criterion (BIC).
We treat the AR as the main benchmark because it is the stronger of the
two for a seasonal monthly series.

The **factor model** adds to the AR the first $k \le 4$ principal components of
the predictors [the *diffusion index* model of @stock2002], with $p$ and $k$
chosen by BIC.

Five **ML models** use all the features. *Ridge regression* [@hoerl1970]
shrinks all coefficients toward zero by penalising their squared size, with
the penalty chosen by leave-one-out cross-validation. The *LASSO*
[@tibshirani1996] penalises the absolute size of the coefficients, which sets
many of them exactly to zero and so *selects* predictors. Its penalty is chosen
by BIC. The *adaptive LASSO* [@zou2006] reweights the LASSO penalty using a
first-stage ridge estimate, so that strong predictors are penalised less. The
*random forest* [@breiman2001] averages 500 regression trees, each grown on a
bootstrap sample with a random third of the features considered at each split.
Trees split the data into regions and predict the regional average, so they
capture nonlinear effects and interactions without having to specify them.
*Gradient boosting* [LightGBM, @ke2017] grows small trees one after another,
each one fitting the errors left by the previous ones. Finally, the *ML combination*
is the equal-weight average of the five ML forecasts [@timmermann2006]. All
hyperparameters were fixed in advance (Appendix A) and never tuned on the
evaluation sample.

## 3.3 Evaluation

Accuracy is measured by the root mean squared error (RMSE), the square root of
the average squared forecast error. We report it relative to a benchmark:

$$\text{Relative RMSE}_{m} = \frac{\text{RMSE}_m}{\text{RMSE}_{\text{AR}}}. \qquad (3)$$

A value of 0.90 means that model $m$'s typical error is 10% smaller than the
AR's. To judge whether a difference could be due to chance, we use the
Diebold–Mariano (DM) test [@diebold1995] with the small-sample correction of
@harvey1997. The test asks whether the average difference in squared errors is
zero, allowing for the overlap of multi-step errors. We report one-sided
p-values for "model $m$ is more accurate than the benchmark". Because we test
seven challengers at four cases, we also report p-values with a Holm correction
for multiple testing. In addition, we compute the 90% model confidence set (MCS)
of @hansen2011, the set of models that cannot be statistically distinguished
from the best one.

RQ1 is judged on four pre-specified *decisive cases*: one month ahead ($h = 1$),
twelve months ahead ($h = 12$), and inflation accumulated over the next three
and the next twelve months. A model *beats* a benchmark when its relative RMSE
is below one and the DM p-value is below 0.05. For RQ2 we measure each
predictor group's contribution with grouped permutation importance in the RF:
the rise in the training error when all of a group's features are shuffled
together. We report it as a share of the total, averaged over origins, for
$h = 1$ and $h = 12$, together with the share of origins in which the LASSO
selects at least one feature from the group. For RQ3 we split the target months
into *high-inflation* months, where year-on-year inflation exceeds 4% (the top of
the target band), and all others. We also plot cumulative squared forecast-error
differences over time [cf. @giacomini2010].

# 4. Validation: the replication gate

Before any Philippine forecast was computed, we tested the code on the
reference paper's own setting. Using FRED-MD [@mccracken2016], US CPI inflation,
a rolling 360-month window, four lags of every series plus four principal
components, and out-of-sample months 2001–2015, we pre-registered three
criteria: (G1) the RF beats the RW at $h = 1, 3, 6, 12$; (G2) its RMSE averaged
across these horizons is below the AR's; and (G3) it has the lowest average
RMSE among RW, AR, ridge, LASSO and RF. The criteria are qualitative because
the paper's tables were not accessible when the gate was written.
{{ n.gate_text }} (Figure 6, Table A2).

# 5. Results

## 5.1 RQ1: Do machine-learning models beat the benchmarks?

{{ n.rq1_text }}

{{ t.table2 }}

## 5.2 RQ2: Which predictors matter?

{{ n.rq2_text }}

## 5.3 RQ3: When do the gains arise?

{{ n.rq3_text }}

{{ t.table3 }}

# 6. Robustness

{{ n.robust_text }}

# 7. Discussion and conclusion

{{ n.discussion_text }}

**Limitations.** We use final-vintage data. The CPI is rarely revised, but
the 2018 rebasing changed the index history, and the external series can be
revised. The evaluation sample is long for an emerging economy
({{ n.n_oos }} months) but contains only a handful of inflation episodes,
so the regime comparisons in RQ3 rest on few independent events. We fixed the
hyperparameters in advance instead of tuning them. This protects against
overfitting the evaluation sample, but it may understate what a carefully tuned
model could achieve. Finally, we do not compare with the BSP's own published
forecasts, which are made on a quarterly schedule with information we do not
observe.

# Declarations

**Funding.** None. **Competing interests.** None. **Data and code availability.**
All data are public (PSA OpenSTAT, FRED, BIS). The raw downloads, the code that
rebuilds every number, table and figure from them, and the dated
pre-registration are in the replication package (`run_all.sh`).
**Pre-registration.** The design (research questions, models,
hyperparameters, evaluation sample, tests, robustness checks and the replication
gate) was committed before any estimate. Deviations are listed in Appendix B.

# References

::: {#refs}
:::

# Appendix A. Hyperparameters and implementation

{{ t.tableA1 }}

# Appendix B. Decisions log and deviations from the pre-registration

{{ n.deviations_text }}

# Appendix C. Full results

{{ t.tableA2 }}

{{ t.tableA3 }}

# Figures

![Headline inflation in the Philippines, year on year, January 1995 to {{ n.latest_month }}. The grey band is the BSP target range of 2–4%. The dashed line marks the first month of the forecast evaluation. Source: PSA CPI (2018 = 100), our calculation.](../output/figures/fig1_inflation.png){width=95%}

![RMSE of each model relative to the AR benchmark (left) and to the random walk (right), by forecast horizon, January 2005 to {{ n.oos_end }}. Values below the horizontal line at 1 mean the model is more accurate than the benchmark.](../output/figures/fig2_ratios.png){width=100%}

![Cumulative squared forecast-error difference between the AR benchmark and each model, by target month, for one-month-ahead (left) and twelve-month-ahead (right) forecasts. A rising line means the model is doing better than the AR over that period; a falling line means it is doing worse.](../output/figures/fig3_csfe.png){width=100%}

![Share of the random forest's grouped permutation importance by predictor group, averaged over all forecast origins, for one-month-ahead (grey) and twelve-month-ahead (hatched) forecasts.](../output/figures/fig4_importance.png){width=85%}

![RMSE relative to the AR at the four decisive cases, for the random forest (filled circles) and the ML combination (open squares), in the main specification and each robustness check. Values left of the vertical line mean the model is more accurate than the AR.](../output/figures/fig5_robustness.png){width=100%}

![Replication gate on US data (FRED-MD): RMSE relative to the random walk for the random forest, LASSO, ridge and AR, 2001–2015.](../output/figures/fig6_replication.png){width=75%}

![Inflation over the next twelve months: actual values and the forecasts of the AR and the ML combination made twelve months earlier, in log points (approximately percent).](../output/figures/fig7_yearahead.png){width=95%}
