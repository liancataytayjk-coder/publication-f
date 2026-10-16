---
title: "Cover letter"
---

{{ n.build_date }}

The Editors\
*Journal of Asian Economics*

Dear Editors,

Please consider the enclosed manuscript, "Can Machine Learning Beat Simple
Benchmarks in Forecasting Philippine Inflation? Evidence from a Pre-Registered
Pseudo Out-of-Sample Evaluation, 2005–2026", for publication in the *Journal of
Asian Economics*.

Machine-learning methods are increasingly promoted as tools for forecasting
inflation, mostly on the strength of evidence from the United States. The
paper asks whether that evidence carries over to an Asian emerging economy
where inflation is driven by rice, food and oil shocks. Using official monthly
data from the Philippine Statistics Authority and {{ n.n_pred }} predictors, it
compares five machine-learning methods, their combination and a factor model
with standard benchmarks over {{ n.n_oos }} out-of-sample months.

The main finding is negative and, we believe, useful. Every model beats the
random walk, but none beats a simple autoregressive benchmark: the best
machine-learning forecast has an error between {{ n.combo_min }} and
{{ n.combo_max }} times the benchmark's, and no difference is significant. The
result holds across rolling-window lengths, predictor sets and samples. Only
with an expanding window do two machine-learning forecasts gain a small edge one
month ahead (about 5%), and that edge does not survive a correction for multiple
testing. Two features
make it credible. The design was pre-registered before any Philippine forecast
was computed, and the code first had to reproduce the reference paper's main
result on US data. The paper also shows where the predictive content lies (food
and regional prices) and why it does not translate into accuracy. These lessons
are relevant to other Asian central banks with similar inflation dynamics.

The manuscript is original, has not been published, and is not under
consideration elsewhere. There are no competing interests and no funding to
declare. All data are public, and the replication package rebuilds every number
from the raw downloads.

Sincerely,

Lian Cataytay\
University of Southeastern Philippines\
lrcataytay00745\@usep.edu.ph
