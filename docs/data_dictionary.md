# Data dictionary

## Sources, as pulled on October 15, 2026

| File | Source | What it holds |
|---|---|---|
| `data/raw/nass_qs_crops_ia_corn_soy.tsv` | USDA NASS Quick Stats bulk file `qs.crops_20261015.txt.gz` from https://www.nass.usda.gov/datasets/ | Every Iowa row for corn and soybeans from the SURVEY program, 2000 onward: 48,010 rows, all 39 Quick Stats columns, tab separated. Values are text as NASS ships them, with thousands commas. |
| `data/raw/iem_climate_division_daily.csv` | Iowa Environmental Mesonet Climodat, https://mesonet.agron.iastate.edu/cgi-bin/request/coop.py, network IACLIMATE, stations IAC001 to IAC009 | One row per climate division and day, January 1, 2000 to September 30, 2026: high and low (F), precipitation (inches), growing degree days base 50 cap 86, and the IEM's estimated flags. The division series are gridded averages, so every day is present; the estimated flags are true on all but 21 of the 87,930 days. |
| `data/lookups/ncei_county_to_climdivs.txt` | NCEI, https://www.ncei.noaa.gov/pub/data/cirs/climdiv/county-to-climdivs.txt | Each U.S. county's climate division, matched by county centroid. Iowa counties are postal FIPS 19xxx and divisions 1301 to 1309. |
| `data/lookups/iowa_counties.geojson` | Census county boundaries as redistributed in the Plotly datasets repository (geojson-counties-fips.json), trimmed to the 99 Iowa features | Outlines for the map and for finding which counties touch Polk. |

## Processed tables

### `data/processed/crop_county_year.csv` (4,907 rows)

One row per county, crop and year. Built by `src/clean.py` from NASS rows with `AGG_LEVEL_DESC = COUNTY`, `DOMAIN_DESC = TOTAL`, `FREQ_DESC = ANNUAL` and `REFERENCE_PERIOD_DESC = YEAR`. Rows named "OTHER (COMBINED) COUNTIES" or "OTHER COUNTIES" (NASS's catch-all for counties it did not publish that year) are dropped. "(D)" would become null; none occurred in this pull.

| Column | Meaning | NASS series |
|---|---|---|
| `county_fips` | Five-digit county FIPS, text | `STATE_ANSI` + `COUNTY_ANSI` |
| `county_name` | County name in NASS's upper case | `COUNTY_NAME` |
| `asd_code` | NASS agricultural statistics district, 10 to 90 | `ASD_CODE` |
| `crop` | CORN or SOYBEANS | `COMMODITY_DESC` |
| `year` | Crop year | `YEAR` |
| `acres_planted` | Acres planted, all purposes | `CORN - ACRES PLANTED`, `SOYBEANS - ACRES PLANTED` |
| `acres_harvested` | Acres harvested for grain (corn) or beans | `CORN, GRAIN - ACRES HARVESTED`, `SOYBEANS - ACRES HARVESTED` |
| `yield_bu_acre` | Bushels per harvested acre | `CORN, GRAIN - YIELD, MEASURED IN BU / ACRE`, `SOYBEANS - YIELD, MEASURED IN BU / ACRE` |
| `production_bu` | Bushels produced | `CORN, GRAIN - PRODUCTION, MEASURED IN BU`, `SOYBEANS - PRODUCTION, MEASURED IN BU` |
| `source` | Always SURVEY in this pull | `SOURCE_DESC` |

Corn silage rows are in the raw file but not in this table. Coverage by year is in `docs/validation.md`; 2000 to 2014 have all 99 counties for both crops, later years fewer.

### `data/processed/crop_state_year.csv` (54 rows)

Same measures at the state level, 2000 to 2026, plus `last_loaded`, NASS's load time for the newest value in that row. The 2026 row is NASS's estimate as loaded on October 9, 2026, not a final figure.

### `data/processed/weather_district_season.csv` (243 rows)

One row per climate division and year, 2000 to 2026, for the growing season April 1 through September 30 (183 days).

| Column | Meaning |
|---|---|
| `climate_district` | IEM station id, IAC001 (Northwest) to IAC009 (Southeast) |
| `climdiv_code` | NCEI division code, 1301 to 1309 |
| `precip_in` | Season rain, inches |
| `july_precip_in` | July rain, inches |
| `gdd50` | Season growing degree days, base 50 and cap 86, Fahrenheit |
| `days_high_ge_90` | Season days with a high of 90F or more |
| `avg_high_f` | Mean daily high over the season |
| `season_days` | Days in the season, always 183 |

The IEM notes that a Climodat day is the observation date, usually a 7 AM reading covering the prior 24 hours, so a day's rain can belong partly to the calendar day before.

### `data/lookups/county_to_district.csv` (99 rows)

`county_fips`, `county_name`, `asd_code`, `climdiv_code`, `climate_district`, the district number from each source, and `same_boundary`. It is true for all 99 counties: NASS's nine districts and NCEI's nine climate divisions contain the same counties in Iowa.

### `data/lookups/draw_area.csv` (7 rows)

Polk County and the six counties whose outline shares at least two boundary points with Polk's in the Census outlines: Boone, Dallas, Jasper, Marion, Story and Warren. Madison touches Polk only at a corner and is left out. `src/draw_area.py` builds it.

## Database

`data/iowa_crops.db` (SQLite, built by `src/load_sqlite.py`, not committed) holds the same tables as `dim_county` (with `draw_area` 0 or 1), `dim_crop` (1 corn, 2 soybeans), `fact_crop_county_year`, `fact_crop_state_year` and `fact_weather_district_season`, plus the view `v_yield_trend`, which fits the straight-line yield trend per county and crop and scores every year against it. The schema is `sql/schema.sql`.

## Query outputs, `data/outputs/`

| File | Grain | Notes |
|---|---|---|
| `01_production_share.csv` | county and crop | 2021 to 2025 production per published year, share of the published counties' total, rank. `years_published` shows how many of the five years a county has; the five-year sum is kept beside it. |
| `02_crop_mix_shift.csv` | draw-area county and year | Corn share of corn plus soybean planted acres, and the change from the prior year. |
| `03_rolling_yield_yoy.csv` | county, crop and year | Year-over-year yield change and a five-row rolling average. `rows_in_avg` is below 5 only at the start of a series; `years_spanned` is the calendar span of the window and exceeds `rows_in_avg` when a published year is missing inside it. |
| `04_trend_residual_bad_years.csv` | county, crop and year | Straight-line trend fit per county and crop over its published years (x = year minus 2000, from the view `v_yield_trend`), the trend yield, percent against trend rounded to one decimal, and `bad_year` = 1 when that rounded figure is -10.0 or lower. |
| `05_weather_in_bad_years.csv` | crop and year type | Averages of the division weather over bad and normal county-years. |
| `06_expected_bushels.csv` | draw-area county and crop | 2026 trend yield times the latest published planted acres times the 2016 to 2025 harvested-to-planted ratio. |
| `validation_coverage.csv` | crop and year | County sums against the state figure. |
| `summary_worst_years.csv` | crop and year | Counties flagged bad, the median county against trend, and July rain and hot days averaged over the published counties (each taking its division's value). |
| `summary_july_rule.csv` | crop | County-years with July rain under 2 inches and 20 or more days at 90F, and the share that ended bad. |
| `summary_draw_area_bad_years.csv` | crop and year | Draw-area counties flagged bad each year and whether that was half or more of those published. |
| `summary_draw_area_yield_swing.csv` | crop and county | Mean and largest absolute year-over-year yield change in the draw area. |
| `summary_draw_area_totals.csv` | crop | Draw-area production, five-year sum and per published year, as a share of the published counties. |
| `summary_draw_area_corn_share.csv` | year | Corn share of corn plus soybean planted acres across the draw-area counties published that year. |

## Definitions

- **Bad year**: a county's yield 10% or more below its own straight-line trend, judged on the one-decimal percentage shown in the output. The cutoff is a choice; `pct_vs_trend` is there for any other threshold.
- **Draw area**: see `draw_area.csv` above.
- **Growing season**: April 1 through September 30, every year, for all weather measures.
