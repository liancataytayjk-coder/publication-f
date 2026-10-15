# Raw data source log

All files were pulled on 2026-10-15 by `scripts/01_download_psa.py` and
`scripts/01_download_external.py`. They are stored unchanged (gzipped).

| File | Source / URL or table id | Base / units | Coverage | Notes |
| --- | --- | --- | --- | --- |
| psa/cpi_all_2018new_bycommodity_regions_2018_latest.csv.gz | PSA OpenSTAT `DB/2M/PI/CPI/2018NEW/0012M4ACP22.px` | 2018=100 | Jan 2018–Sep 2026; PH, NCR, AONCR, 17 regions; 354 items | '..' = not available (Oct–Dec 2026 not yet published). |
| psa/cpi_all_2018new_backcast_bycommodity_regions_1994_2017.csv.gz | PSA OpenSTAT `.../2018NEW/0012M4ACP28.px` | 2018=100 (PSA backcast) | Jan 1994–Dec 2017; same geographies and items | PSA's own backcast; some items start later ('..'). |
| psa/cpi_core_2018new_bycommodity_ph_2018_latest.csv.gz | PSA OpenSTAT `.../2018NEW/0012M4ACP30.px` | 2018=100 | Jan 2018–Sep 2026; PH | Core CPI by commodity; all items row used. |
| psa/cpi_core_2018new_backcast_allitems_ph_1994_2017.csv.gz | PSA OpenSTAT `.../2018NEW/0012M4ACP33.px` | 2018=100 (PSA backcast) | Jan 1994–Dec 2017; PH | Layout is Period × Year. |
| psa/cpi_yoy_2018new_bycommodity_ph_2019_latest.csv.gz | PSA OpenSTAT `.../2018NEW/0012M4ACP23.px` | percent | Jan 2019–Sep 2026; PH | Used only to validate our computed year-on-year inflation. |
| psa/cpi_weights_2018new_bycommodity_regions.csv.gz | PSA OpenSTAT `.../2018NEW/0012M4ACP25.px` | percent of basket | 2018 weights; PH and regions | |
| fred/POILBREUSDM.csv.gz | https://fred.stlouisfed.org/graph/fredgraph.csv?id=POILBREUSDM | USD/barrel | Jan 1992–Jul 2026 | IMF Primary Commodity Prices via FRED. |
| fred/POILDUBUSDM.csv.gz | FRED id POILDUBUSDM | USD/barrel | Jan 1992–Jul 2026 | Dubai crude (the Asian benchmark). |
| fred/PALLFNFINDEXM.csv.gz | FRED id PALLFNFINDEXM | index 2016=100 | Jan 1992–Jul 2026 | IMF all-commodities index. |
| fred/PFOODINDEXM.csv.gz | FRED id PFOODINDEXM | index 2016=100 | Jan 1992–Jul 2026 | IMF food index (replaces FAO, D9). |
| fred/PWHEAMTUSDM.csv.gz | FRED id PWHEAMTUSDM | USD/metric ton | Jan 1992–Jul 2026 | Wheat. |
| fred/PMAIZMTUSDM.csv.gz | FRED id PMAIZMTUSDM | USD/metric ton | Jan 1992–Jul 2026 | Maize. |
| fred/CPIAUCNS.csv.gz | FRED id CPIAUCNS | 1982–84=100, NSA | Jan 1913–Sep 2026 | Oct 2025 missing (not collected during the 2025 US government shutdown); dropped from the predictor set (D11). |
| fred/FEDFUNDS.csv.gz | FRED id FEDFUNDS | percent | Jul 1954–Sep 2026 | |
| bis/WS_XRU_M_PH_PHP_A.csv.gz | https://stats.bis.org/api/v1/data/WS_XRU/M.PH.PHP.A?format=csv | PHP per USD, monthly average | 1945–Sep 2026 | |
| bis/WS_CBPOL_M_PH.csv.gz | https://stats.bis.org/api/v1/data/WS_CBPOL/M.PH?format=csv | percent | 1986–2026 | BSP policy rate (BIS definition notes in file). |
| fredmd/fredmd_current.csv.gz | https://www.stlouisfed.org/-/media/project/frbstl/stlouisfed/research/fred-md/monthly/current.csv | FRED-MD, row 2 = transformation codes | Jan 1959–Sep 2025 | Replication gate only. Current vintage, not the vintage Medeiros et al. used. |

Not used: the FAO Food Price Index csv at the long-standing FAO URL ended in
Mar 2018 when pulled, and the World Bank Pink Sheet link reachable from here
ended in Dec 2024 (D7, D9).
