#!/usr/bin/env bash
# Rebuild every number, table, figure and document from data/raw/.
#   ./run_all.sh              rebuild from the committed raw files
#   ./run_all.sh --download   re-download raw data first (overwrites data/raw)
#   ./run_all.sh --skip-estimation   reuse saved forecasts (output/forecasts)
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv/bin/python}
if [[ " $* " == *" --download "* ]]; then
  $PY scripts/01_download_psa.py --force
  $PY scripts/01_download_external.py --force
fi
$PY scripts/02_clean_psa.py
$PY scripts/02b_validate_cpi.py
$PY scripts/03_build_panel.py
$PY -m pytest -q
if [[ " $* " != *" --skip-estimation "* ]]; then
  $PY scripts/04_replicate.py                      # replication gate (~55 min on 4 cores)
  $PY scripts/05_estimate.py main small w96 join2018 core w180 expanding   # ~4 h on 4 cores
fi
$PY scripts/06_evaluate.py
$PY scripts/07_figures.py
$PY scripts/08_paper.py
echo "done: paper/manuscript.docx"
