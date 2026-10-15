# Power BI report: model and pages

## What is in the folder

`powerbi/` holds the report two ways.

- `iowa-county-crop-ops.pbip`: the project file.
- `iowa-county-crop-ops.Report/`: the report definition as PBIR JSON. It has `definition/report.json`, one folder per page under `definition/pages/`, one `visual.json` per visual, and `StaticResources/RegisteredResources/` for the theme and the custom county map.
- `iowa-county-crop-ops.SemanticModel/`: the model in TMDL. It has `definition/model.tmdl`, `definition/tables/*.tmdl`, `definition/relationships.tmdl` and `definition/expressions.tmdl`.
- `iowa-county-crop-ops.pbix`: the single-file version with data loaded.

`.pbi/` cache files are gitignored. The theme is a small custom one: corn in brown (`#b8711d`), soybeans in green (`#2f6b3a`).

## Source data

Every table loads from CSVs the pipeline already writes. One text parameter, `DataFolder` (default `C:\Users\drewm\dev\iowa-county-crop-ops\data`), sets the root, so there is no database connection to configure.

| Table | Source |
|---|---|
| Crop Year | `processed/crop_county_year.csv`, joined in Power Query to `outputs/04_trend_residual_bad_years.csv` (trend yield, percent vs trend, bad-year flag, trend slope) and `outputs/03_rolling_yield_yoy.csv` (five-row rolling yield, year-over-year change). One row per county and crop for each year, 4,907 rows. |
| County | `lookups/county_to_district.csv` plus `lookups/draw_area.csv`. 99 rows. Columns include County FIPS, County, Ag District, Climate Division, Draw Area ("Draw area" or "Rest of Iowa") and Draw Area Role. |
| Weather | `processed/weather_district_season.csv`. One row per climate division and year: season rain, July rain, GDD, days at 90F or hotter, average high. |
| State Year | `processed/crop_state_year.csv` |
| Expected 2026 | `outputs/06_expected_bushels.csv` |
| Weather in Bad Years | `outputs/05_weather_in_bad_years.csv` |
| Worst Years | `outputs/summary_worst_years.csv` |
| Crop Type | Two rows (Corn, Soybeans) typed in M, so one slicer filters every table. |

County names are title-cased in Power Query. O'Brien is fixed by hand because Text.Proper drops the apostrophe form.

## Relationships

Eight, all many-to-one and single direction. Crop Year joins Crop Type on Crop and County on County FIPS. It joins Weather on a District Year key built as climate division plus year. State Year joins Crop Type, as do Weather in Bad Years and Worst Years. Expected 2026 joins both County and Crop Type.

## Measures

There are 23 measures on Crop Year. State Year and Expected 2026 carry one each. The ones that carry the modeling decision:

```
Production per Published Year (M bu) =
SUMX(
    SUMMARIZE('Crop Year', 'Crop Year'[County FIPS], 'Crop Year'[Crop]),
    CALCULATE(DIVIDE(SUM('Crop Year'[Production]), DISTINCTCOUNT('Crop Year'[Year])))
) / 1000000

Recent Production per Year (M bu) =
CALCULATE([Production per Published Year (M bu)], 'Crop Year'[Year] >= 2021, 'Crop Year'[Year] <= 2025)

Share of Published Counties =
DIVIDE([Recent Production per Year (M bu)], CALCULATE([Recent Production per Year (M bu)], REMOVEFILTERS(County)))

Draw Area Production per Year (M bu) =
CALCULATE([Recent Production per Year (M bu)], County[Draw Area] = "Draw area")

Share Bad = DIVIDE([Bad County Years], [County Years])

July Rain (in) = AVERAGEX('Crop Year', RELATED(Weather[July Rain]))
```

The first measure iterates county by county on purpose. A county with four published years out of five would otherwise be understated by a fifth. Share of Published Counties uses REMOVEFILTERS(County) because the denominator is what NASS published, not the state total; the coverage note in the README explains the gap.

The rest are plain: Yield (bu/acre) as production over harvested acres, Trend Yield, Avg Pct vs Trend, Median Pct vs Trend, Trend Slope (bu/acre/yr), Bad County Years, Counties Published, Published Years, Days 90F, Season Rain (in), Corn Share of Planted and Expected 2026 (M bu). Corn Share of Planted only counts county-years where NASS published both crops. In 2024 Dallas County had a soybean row but no corn row, and counting it would have dropped the draw-area share to 49.6% instead of 55.7%.

## Pages

All numbers below are the corn view, which is the default. Every page carries the same Corn / Soybeans slicer. It is synced across pages and single select, and it starts on Corn.

**Where the grain is.** Four cards: published counties 2,561.5 M bu per year (shown as 2.6K), 99 counties published, Polk draw area 165.6 M bu per year, draw area share of published counties 6.5%. A shape map shades all 99 counties by production per published year, with Kossuth darkest at 58.6 M bu. A ranked table has Kossuth, Pottawattamie (47.4), Crawford (42.3), Webster (41.1) and Plymouth (40.5) at the top. Switching the slicer to Soybeans gives 592.0 M bu across published counties and 42.0 M bu for the draw area, a 7.1% share.

**County yield vs trend.** A county dropdown (all counties when empty) drives the cards: yield 178.8 bu per acre over all years, trend slope 2.20 bu per acre per year, 338 county-years 10% or more below trend, 13.7% of county-years. A line chart plots actual against trend yield by year, and a year table adds July rain and hot days. 2012 is the low point at 137.0 bu per acre, 25.9% below trend.

**Bad years and weather.** A column chart shows the share of published counties at least 10% below trend by year, and 2012 is the tall bar. The query 05 table splits county-years: bad ones (338) averaged 2.84 in of July rain with 24.0 days at 90F+, and came in 20.2% below trend; normal ones (2,132) averaged 4.28 in with 13.5 days, and came in 3.2% above. A scatter puts one dot per county and year with July rain against percent vs trend. The worst-years table has 2012 at 91 of 99 counties bad, median 25.0% below.

**Elevator view.** A page-level filter keeps the seven draw-area counties: Polk, Boone, Dallas, Jasper, Marion, Story and Warren. Cards: 165.6 M bu per year, 6.5% share, expected 2026 corn 168.0 M bu, corn share of planted acres 55.7% over all years. A line tracks corn's share of corn-plus-soybean planted acres by year. It starts at 51.5% in 2000 and peaks at 61.3% in 2007; over 2021 to 2025 it stays between 52.5% and 56.8%. A column chart ranks expected 2026 bushels by county, Jasper largest at about 37 M bu and Warren smallest at about 11.7. A county table lists bad years and trend slope.

## The county map

The built-in filled map geocodes county names and placed several Iowa counties in other states. Page 1 uses the shape map visual with a custom map instead: the Census county outlines already in `data/lookups/`, converted to TopoJSON and registered in the report as `StaticResources/RegisteredResources/iowa-counties.json`. County names in the data match the `NAME` property in the TopoJSON. The fill is a two-color gradient on the production measure. Counties NASS did not publish for that crop show in grey.

## Opening and refreshing

The `.pbix` opens with data loaded. For the project, open the `.pbip` in Power BI Desktop, go to Transform data > Edit parameters, point `DataFolder` at the `data` folder of your clone, then Refresh. I built and tested the report in Power BI Desktop on Windows (the Microsoft Store build) in October 2026.
