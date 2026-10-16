# Forecasting Philippine inflation with machine learning

A pre-registered pseudo out-of-sample comparison of machine-learning (ML)
forecasts of Philippine CPI inflation against simple benchmarks, January
2005–September 2026. It replicates the design of Medeiros et al. (2021, *JBES*)
on official PSA data.

**Main finding.** Every model beats the random walk by a wide margin, but none
beats an autoregressive (AR) benchmark. The best, an equal-weight ML
combination, has an RMSE of 0.98–1.03 times the AR's, and no difference is
significant.

## What is where

| Path | What it is |
| --- | --- |
| `CLAUDE.md` | Project brief: research questions, the dated pre-registration, the decisions log (D1–D13), the replication gate and its result, the results, open questions |
| `paper/manuscript.md`, `.docx` | The journal manuscript (rendered; edit `paper/manuscript_template.md` and `paper/results_text.py`, never the output) |
| `paper/references.bib` | Bibliography, checked against Crossref |
| `paper/SUBMISSION_CHECKLIST.md` | What remains before submission |
| `data/raw/` | Untouched downloads, logged in `data/raw/source_log.md` |
| `phfx/` | Forecasting engine (`forecast.py`) and evaluation tests (`evaluate.py`) |
| `tests/` | Simulation tests: no look-ahead, AR recovery, sparse-signal recovery, DM size and power |
| `scripts/` | Numbered pipeline, 01 download → 08 paper |
| `output/forecasts/` | Every out-of-sample forecast, by specification |
| `output/tables/`, `output/figures/` | Tables and black-and-white figures, written by scripts |

## Rebuild

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
./run_all.sh                     # full rebuild from data/raw (about 5 h on 4 cores)
./run_all.sh --skip-estimation   # reuse saved forecasts; tables, figures, paper in minutes
./run_all.sh --download          # re-download the raw data first
```

Pandoc must be installed to render the `.docx` file. The manuscript uses the author's house style
(Times New Roman 12 pt, double spacing, three-line tables; `paper/lian-article-reference.docx`,
`scripts/style/`); `scripts/style/check_style.py paper/manuscript.docx` audits it.
