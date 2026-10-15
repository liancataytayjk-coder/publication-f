"""Download a PxWeb table (PSA OpenSTAT and other statistics offices) unchanged to a gzipped CSV.

Pulls every value of every variable, one geography at a time to stay under the
PxWeb cell limit, retries with exponential backoff, and decodes Latin-1 when
UTF-8 fails. The API's CSV responses are stacked but otherwise unchanged, so the
file is a faithful raw download. Log it in data/raw/source_log.md afterwards.

Usage:
  python pxweb_download.py <api_base> <table_path> <out.csv.gz> [--geo-regex REGEX] [--force]

Example (PSA, bottom-30% CPI, 2018=100):
  python pxweb_download.py https://openstat.psa.gov.ph/PXWeb/api/v1/en/DB/2M/PI/ \
      BIH/2018NEW/0022M4ABIR1.px data/raw/psa/cpi_b30_2018new_2018_2026.csv.gz \
      --geo-regex '^(PHILIPPINES|\.\.[^.].*)$'

--geo-regex keeps only geography labels that match (e.g. country and regions,
not provinces). Check the number of geographies printed against what you expect.
"""

import argparse
import io
import re
import time
from pathlib import Path

import pandas as pd
import requests

GEO_CODES = ("Geolocation", "Area", "Region", "Geography")


def post(url, query):
    for attempt in range(5):
        try:
            r = requests.post(url, json=query, timeout=120)
            r.raise_for_status()
            try:
                return r.content.decode("utf-8-sig")
            except UnicodeDecodeError:
                return r.content.decode("latin-1")
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** (attempt + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("api_base")
    ap.add_argument("table")
    ap.add_argument("out")
    ap.add_argument("--geo-regex", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists() and not a.force:
        print("exists:", out)
        return
    url = a.api_base.rstrip("/") + "/" + a.table
    meta = requests.get(url, timeout=60).json()
    geo = next((v for v in meta["variables"] if v["code"] in GEO_CODES), None)
    rest = [{"code": v["code"], "selection": {"filter": "all", "values": ["*"]}}
            for v in meta["variables"] if v is not geo]
    if geo is None:
        codes = [None]
    else:
        rx = re.compile(a.geo_regex) if a.geo_regex else None
        codes = [c for c, t in zip(geo["values"], geo["valueTexts"]) if rx is None or rx.match(t)]
    parts = []
    for code in codes:
        sel = list(rest)
        if code is not None:
            sel.insert(0, {"code": geo["code"], "selection": {"filter": "item", "values": [code]}})
        text = post(url, {"query": sel, "response": {"format": "csv"}})
        parts.append(pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False))
        time.sleep(0.5)
    df = pd.concat(parts, ignore_index=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"wrote {out}: {len(codes)} geographies, {df.shape[0]} rows x {df.shape[1]} cols")


if __name__ == "__main__":
    main()
