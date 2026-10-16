"""Prose blocks for the manuscript that depend on the results.

Each block is a Jinja2 string: numbers are pulled from the numbers dictionary
({{ n.key }}), never typed. scripts/08_paper.py renders them before the template.
Written after the main results were seen; the interpretation, not the numbers,
is the author's.
"""
import json
from pathlib import Path

T = {}

T["abstract"] = (
    "Do machine-learning (ML) models that use many predictors forecast Philippine inflation better than simple "
    "benchmarks? We replicate the data-rich design of Medeiros et al. (2021) on official monthly data from the "
    "Philippine Statistics Authority, 1994–2026. We compare ridge, LASSO, adaptive LASSO, random forest and "
    "gradient boosting forecasts, their combination and a factor model with random-walk and autoregressive (AR) "
    "benchmarks over {{ n.n_oos }} out-of-sample months, using {{ n.n_pred }} predictors that include detailed "
    "food and energy prices, all 18 regional indices and world commodity prices. The design was pre-registered, and "
    "the code first had to reproduce the reference paper's main result on US data, which it did. Every model "
    "beats the random walk by a wide margin, but none beats the AR. At the four pre-specified test cases, the "
    "best ML forecast, the equal-weight combination, has a root mean squared error between {{ n.combo_min }} and "
    "{{ n.combo_max }} times the AR's. No difference is statistically significant, and the AR is never excluded "
    "from the 90% model confidence set. The gains are not larger in high-inflation months. Food and regional "
    "prices carry most of the random forest's one-month-ahead predictive content. Yet no model, linear or "
    "nonlinear, anticipated the large inflation episodes of 2008, 2018, 2022–23 or 2026 a year ahead. For the "
    "Philippines, simple benchmarks remain very hard to beat; adding predictors and nonlinearity does not change "
    "that."
)

T["intro_findings"] = (
    "The answer is clear and goes against the US evidence. All models beat the random walk by a wide margin; "
    "the AR's error is {{ n.ar_vs_rw_h1 }}% smaller one month ahead. But no ML model is more "
    "accurate than the AR benchmark. The best of them, the equal-weight ML combination, has a relative RMSE of "
    "{{ n.main_h1_combo_ar }} one month ahead and {{ n.main_acc12_combo_ar }} for inflation over the next year, "
    "and none of the Diebold–Mariano tests rejects equal accuracy. The random forest, the winner in the "
    "US, has relative RMSEs of {{ n.main_h1_rf_ar }} to {{ n.main_acc12_rf_ar }} at these cases. The same code "
    "reproduces the random forest's advantage on US data, so the difference lies in the data, not the "
    "implementation. Food and regional prices carry most of the random forest's short-horizon signal, but that "
    "signal is already contained in past headline inflation. The ML gains do not grow in high-inflation periods. "
    "We read these results as support for the long-standing view that simple benchmarks are hard to beat "
    "[@atkeson2001; @stock2007], in a setting where supply shocks dominate inflation and are hard to predict."
)

T["gate_text"] = (
    "All three criteria hold. The RF's RMSE relative to the RW is {{ n.gate_rf_rw }} at h = 1, 3, 6 and 12; its "
    "RMSE averaged over horizons is {{ n.gate_rf_ar_mean }} times the AR's; and it has the lowest average RMSE of "
    "the five models, although LASSO is close and is better than RF one month ahead. The random forest's advantage "
    "on US data is therefore reproduced by our code"
)

T["rq1_text"] = (
    "Table 2 and Figure 2 give the main result. First, the random walk is a poor benchmark for monthly "
    "Philippine inflation. Its RMSE is {{ n.main_h1_rw_ar }} times the AR's one month ahead and "
    "{{ n.main_acc12_rw_ar }} times for inflation over the next twelve months. It is excluded from the "
    "90% model confidence set in every decisive case. Every other model beats it, and so would pass the "
    "criterion of @medeiros2021, who report results relative to the random walk.\n\n"
    "Second, against the AR benchmark, no model wins. At $h = 1$ the relative RMSEs range from "
    "{{ n.main_h1_combo_ar }} (ML combination) and {{ n.main_h1_rf_ar }} (random forest) to "
    "{{ n.main_h1_ridge_ar }} (ridge). The lowest one-sided Diebold–Mariano p-value across all seven challengers "
    "and four decisive cases is {{ n.min_dm_p }}, far from any conventional threshold; after the Holm correction, "
    "the smallest is {{ n.min_holm_p }}. Twelve months ahead the picture is the same: the ratios lie "
    "between {{ n.min_h12 }} and {{ n.max_h12 }}. For inflation accumulated over the next three months, the "
    "combination and the random forest are about 2% more accurate than the AR ({{ n.main_acc3_combo_ar }} and "
    "{{ n.main_acc3_rf_ar }}), but for inflation over the next year they are worse ({{ n.main_acc12_combo_ar }} "
    "and {{ n.main_acc12_rf_ar }}). The model confidence set confirms that these differences are noise. "
    "The 90% set contains the AR in every case, together with almost every challenger. The models excluded "
    "are: {{ n.mcs_excluded }}.\n\n"
    "Third, the methods that use the predictors most aggressively do worst. Ridge regression, which keeps every "
    "feature, and gradient boosting are up to {{ n.ridge_max_pct }}% and {{ n.lgbm_max_pct }}% less accurate "
    "than the AR at some horizons (Table A3). At long horizons the LASSO usually selects few or no features (Section "
    "5.2), so its forecast stays close to the window mean and is about as accurate as the AR. The factor model is "
    "almost identical to the AR (relative RMSEs between {{ n.factor_min }} and {{ n.factor_max }} across all "
    "horizons). The AR itself almost always chooses a single lag (the median at every horizon), so the strongest "
    "forecast is little more than a recent mean plus seasonal dummies."
)

T["rq2_text"] = (
    "Figure 4 shows which predictor groups the random forest relies on. One month ahead, food prices carry "
    "{{ n.imp_food_h1 }}% of the grouped permutation importance, regional inflation {{ n.imp_regional_h1 }}% and "
    "the other domestic CPI components {{ n.imp_other_domestic_h1 }}%. World prices ({{ n.imp_external_prices_h1 }}%), "
    "energy and utilities ({{ n.imp_energy_utilities_h1 }}%) and money and the exchange rate "
    "({{ n.imp_money_fx_h1 }}%) matter much less. The LASSO tells the same story: it selects at least one food "
    "feature at {{ n.lassofreq_food_h1 }}% of origins and one regional feature at {{ n.lassofreq_regional_h1 }}%, "
    "against {{ n.lassofreq_external_prices_h1 }}% for world prices. Twelve months ahead, the random forest "
    "shifts toward the slow-moving domestic components ({{ n.imp_other_domestic_h12 }}%), and the LASSO selects "
    "far fewer features: the share of origins with any food feature falls to {{ n.lassofreq_food_h12 }}%, and "
    "with any other domestic feature to {{ n.lassofreq_other_domestic_h12 }}%.\n\n"
    "H2 is therefore supported at short horizons, with one qualification. Food is the most important group "
    "one month ahead, but energy is not; the oil and fuel series matter less than regional and other domestic prices. "
    "And because the models that use these predictors do not beat the AR, the importance measures describe "
    "where the models find signal in the training data, not where they gain accuracy out of sample. The food and regional "
    "series co-move closely with headline inflation, so they largely repeat information that past "
    "inflation already contains. These importance measures are computed on the training windows and are "
    "descriptive."
)

T["rq3_text"] = (
    "Since 2005, year-on-year inflation has been above 4% in {{ n.share_high }}% of months. Table 3 "
    "compares relative RMSEs in these months and in the rest. H3 predicts that the ML gains concentrate in the "
    "high-inflation months. They do not. One month ahead, the combination's relative RMSE is "
    "{{ n.reg_h1_high_combo_ar }} in high-inflation months and {{ n.reg_h1_other_combo_ar }} in other months, and "
    "the random forest's is {{ n.reg_h1_high_rf_ar }} and {{ n.reg_h1_other_rf_ar }}. For inflation over the next "
    "year, the random forest is about as accurate as the AR in high-inflation periods ({{ n.reg_acc12_high_rf_ar }}) "
    "and worse in calm ones ({{ n.reg_acc12_other_rf_ar }}). That is a small relative advantage in turbulent "
    "times, but only because the AR is also bad then.\n\n"
    "Figure 3 tracks the comparison over time. A rising line means the model is gaining on the AR. One month "
    "ahead, the random forest and the combination gain a little on the AR before 2008 and again in "
    "2010–12, hold that small lead until 2020, lose it in the 2021–23 surge, and then swing sharply in the 2026 "
    "oil shock. No model saw the March–April 2026 jump coming (monthly "
    "inflation of {{ n.mar26_actual }}% and {{ n.apr26_actual }}%). But the AR then carried the April jump "
    "forward, forecasting {{ n.may26_ar }}% for May, when prices in fact fell ({{ n.may26_actual }}%). The ML "
    "models, which average over many predictors, gave a damped {{ n.may26_combo }}%. Twelve months ahead, the "
    "ML models lose ground in the 2022–23 surge and do not recover it. Figure 7 shows why accuracy is so hard to "
    "come by at this horizon. Both the AR and the ML combination forecast year-ahead inflation close to its "
    "recent average, mostly between about 3% and 5%, and neither anticipates the 2008, 2018, 2022–23 or 2026 episodes."
)

T["discussion_text"] = (
    "We asked whether the data-rich ML methods that beat the benchmarks for the United States also help forecast "
    "Philippine inflation. On {{ n.n_oos }} months of pseudo out-of-sample forecasts, with a pre-registered design "
    "and code that reproduces the US result, the answer is no. All the models comfortably beat the random walk. "
    "None beats a simple autoregression with month dummies, and the differences among the better models are "
    "small and statistically insignificant. This is the outcome predicted by H1b, not H1a.\n\n"
    "Why does the US result not carry over? We see three reasons, which the design lets us partly separate. "
    "First, the benchmark matters. Relative to the random walk used by @medeiros2021, all our models look good "
    "(ratios of {{ n.main_h12_rf_rw }} and lower at $h = 12$), which shows how much of the reported ML gain "
    "can come from a weak benchmark when inflation is noisy month to month. Second, the sample is short. A "
    "120-month window gives about 120 observations for {{ n.n_features }} features. With so few observations "
    "per feature, the flexible models fit noise (ridge and boosting) or shrink to the mean (LASSO). The "
    "360-month windows available for the United States are not possible for an inflation-targeting regime that "
    "began in 2002. Third, and most importantly, Philippine inflation episodes are driven by supply "
    "shocks to rice, other food and oil that are themselves unpredictable a month or a year ahead. The predictors "
    "that carry signal are other prices that move at the same time as headline inflation, so they "
    "add little to its own history.\n\n"
    "For forecasting practice, the results suggest that the effort should go into better information on the "
    "shocks themselves, not into more flexible models of the same monthly price data. Examples are crop and "
    "import data for rice, futures prices for oil, and scheduled changes in administered prices and excise "
    "taxes. For the BSP's communication, they suggest stating openly that year-ahead "
    "inflation forecasts carry wide uncertainty, which simple and complex models share. The ML "
    "combination does have one useful property: it reacts less to a single extreme month than the AR does, as "
    "in May 2026. This may make it a useful second opinion during a shock, which future work could evaluate with "
    "density forecasts.\n\n"
    "Several extensions follow naturally. They include real-time vintages, density and quantile ('inflation at "
    "risk') forecasts, and forecasting the components separately and combining them bottom-up. Another is "
    "a comparison with the BSP's own published forecasts."
)

T["robust_text"] = (
    "Figure 5 and Table A4 report the four decisive cases under each pre-registered robustness check. "
    "{{ n.robust_auto }} {{ n.robust_comment }}"
)

T["robust_comment"] = (
    "Taken together, the checks leave the conclusion unchanged. For headline inflation, the best model in "
    "each check is at most about 3% more accurate than the AR, the same small and insignificant margin as in "
    "the main specification. A shorter (96-month) or longer (180-month) window does not help the data-rich models: more "
    "data per window does not turn the small gains into significant ones. Leaving out the pandemic and the "
    "2022–23 surge (targets up to December 2019) does not change the picture either, so the null result is not "
    "an artefact of recent shocks. Using only world prices and money as predictors makes gradient boosting and "
    "the random forest worse at the one-year horizon ({{ n.small_acc12_lgbm_ar }} and {{ n.small_acc12_rf_ar }}), "
    "which confirms that the world-price block on its own adds noise. The January 2018 join dummy changes "
    "nothing.\n\n"
    "The one partial exception is core inflation, which excludes the most volatile food and energy items. With "
    "core inflation as the target, the random forest and the ML combination have relative RMSEs of "
    "{{ n.core_h1_rf_ar }} and {{ n.core_h1_combo_ar }} one month ahead, and the combination reaches "
    "{{ n.core_acc3_combo_ar }} for inflation over the next three months (one-sided DM p = "
    "{{ n.core_acc3_combo_pdm_ar }}). This is significant only at the 10% level, and not after the Holm "
    "correction (p = {{ n.core_acc3_combo_pholm_ar }}). We read it as weak evidence that the ML models find "
    "some signal once the hardest-to-predict supply shocks are removed from the target. That fits the "
    "explanation in Section 7: the obstacle is the unpredictability of food and energy shocks, not a lack of "
    "model flexibility."
)

T["deviations_text"] = (
    "The full decisions log (D1–D13) is in the replication package (`CLAUDE.md`), with dates and labels. Three "
    "changes were made after the plan was written but before any estimate: world food and grain prices come "
    "from the IMF series on FRED because the FAO file was out of date (D9); food and energy classes were added "
    "so that H2 could be tested (D10); and US CPI was dropped because of a missing month (D11). One correction "
    "was made after the first run stopped with an error at its first origin, before any forecast was saved "
    "(D13). The out-of-sample period is defined by origin (December 2004 to {{ n.last_x }}), and the first few "
    "origins use every month available, at least 108, rather than exactly 120. The Holm correction covers seven "
    "challengers at four cases (28 tests per benchmark); the plan said eight challengers by miscounting. "
    "Everything in Section 5.3 after the regime table, including the discussion of the 2026 episode, is "
    "exploratory."
)

Path("paper/results_text.json").write_text(json.dumps(T, indent=1))
print("wrote paper/results_text.json")
