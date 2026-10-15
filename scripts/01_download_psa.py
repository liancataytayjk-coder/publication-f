"""Download PSA OpenSTAT CPI tables (2018=100, new geographic code) unchanged.

Tables: headline CPI by commodity group for the country and regions, current
(2018-) and PSA's own backcasts (1994-2017); core CPI current and backcast.
Each file is logged in data/raw/source_log.md.
"""
import subprocess
import sys
from pathlib import Path

API = "https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/CPI/2018NEW/"
GEO = r"^(PHILIPPINES|\.\.[^.].*)$"  # country, NCR, AONCR and the regions; no provinces
TABLES = [
    ("0012M4ACP22.px", "cpi_all_2018new_bycommodity_regions_2018_latest.csv.gz", GEO),
    ("0012M4ACP28.px", "cpi_all_2018new_backcast_bycommodity_regions_1994_2017.csv.gz", GEO),
    ("0012M4ACP30.px", "cpi_core_2018new_bycommodity_ph_2018_latest.csv.gz", None),
    ("0012M4ACP33.px", "cpi_core_2018new_backcast_allitems_ph_1994_2017.csv.gz", None),
    ("0012M4ACP23.px", "cpi_yoy_2018new_bycommodity_ph_2019_latest.csv.gz", r"^PHILIPPINES$"),  # validation only
    ("0012M4ACP25.px", "cpi_weights_2018new_bycommodity_regions.csv.gz", GEO),
]

here = Path(__file__).parent
for table, name, geo in TABLES:
    cmd = [sys.executable, str(here / "pxweb_download.py"), API, table, f"data/raw/psa/{name}"]
    if geo:
        cmd += ["--geo-regex", geo]
    cmd += sys.argv[1:]  # e.g. --force
    subprocess.run(cmd, check=True)
