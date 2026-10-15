"""Download external series unchanged: FRED, BIS and FRED-MD (replication).

Usage: python scripts/01_download_external.py [--force]
Each file is logged in data/raw/source_log.md.
"""
import gzip
import sys
import time
from pathlib import Path

import requests

FORCE = "--force" in sys.argv
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
FILES = {
    "fred/POILBREUSDM.csv.gz": FRED + "POILBREUSDM",      # Brent crude, USD/bbl
    "fred/POILDUBUSDM.csv.gz": FRED + "POILDUBUSDM",      # Dubai crude, USD/bbl
    "fred/PALLFNFINDEXM.csv.gz": FRED + "PALLFNFINDEXM",  # IMF all commodities index
    "fred/PFOODINDEXM.csv.gz": FRED + "PFOODINDEXM",      # IMF food price index
    "fred/PWHEAMTUSDM.csv.gz": FRED + "PWHEAMTUSDM",      # wheat, USD/mt
    "fred/PMAIZMTUSDM.csv.gz": FRED + "PMAIZMTUSDM",      # maize, USD/mt
    "fred/CPIAUCNS.csv.gz": FRED + "CPIAUCNS",            # US CPI, NSA
    "fred/FEDFUNDS.csv.gz": FRED + "FEDFUNDS",            # US federal funds rate
    "bis/WS_XRU_M_PH_PHP_A.csv.gz": "https://stats.bis.org/api/v1/data/WS_XRU/M.PH.PHP.A?format=csv",
    "bis/WS_CBPOL_M_PH.csv.gz": "https://stats.bis.org/api/v1/data/WS_CBPOL/M.PH?format=csv",
    "fredmd/fredmd_current.csv.gz":
        "https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/monthly/current.csv",
}

for rel, url in FILES.items():
    out = Path("data/raw") / rel
    if out.exists() and not FORCE:
        print("exists:", out)
        continue
    for attempt in range(6):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(2 ** (attempt + 1))
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wb") as f:
        f.write(r.content)
    print(f"wrote {out}: {len(r.content):,} bytes")
