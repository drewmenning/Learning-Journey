# Memo: what the county numbers say about storage and the July weather watch

**To:** Grain elevator manager, Polk County draw area
**From:** Drew Menning
**Date:** October 15, 2026
**Data:** USDA NASS county estimates 2000 to 2025, Iowa Environmental Mesonet weather through September 30, 2026. Every number below is in `data/outputs/`: the six query exports and the `summary_*.csv` tables that `src/summary.py` builds from them.

## Bottom line

The seven-county draw area (Polk, Boone, Dallas, Jasper, Marion, Story, Warren) should plan on about 168 million bushels of corn and 40 million of soybeans in a trend year, and on a bad year about once every six or seven. For corn, 4 of the 26 years (2010, 2012, 2013 and 2020) had half or more of the area's counties 10% or more below trend; for soybeans it was 2003, 2012, 2013 and 2020. Two of those corn years were dry, hot Julys, and the other two were not, so July rain is the first thing to watch, not the only thing.

## Findings

1. **Where the grain is.** Measured per published year over 2021 to 2025, the draw area grows about 166 million bushels of corn a year, 6.5% of what NASS published for Iowa, and 42 million bushels of soybeans, 7.1%. Jasper is the largest producer at 36 million bushels of corn a year (ranked 19th in the state), then Boone at 32 million and Story at 32 million; Polk grows 15 million. Jasper, Warren and Dallas are missing one or two of the five years because NASS combined them, so a plain five-year sum would understate them.
2. **The bad years, and how bad.** In 2012 all seven draw-area counties came in 12% to 34% below their corn trend (Polk 149 bushels an acre against a trend of 177). In 2020, four of the five published counties missed by 19% to 26%. Statewide, bad corn county-years averaged 2.8 inches of July rain and 24 days at 90F or hotter; normal years averaged 4.3 inches and 13.5 days. Harvested acres as a share of planted also slipped, 0.960 against 0.970, so part of the loss shows up as abandoned acres before it shows up in yield.
3. **The mix has settled.** Corn's share of corn-plus-soybean planted acres in the draw area went from 51.5% in 2000 to 61.3% in 2007 and has run between 52.5% and 56.8% over 2021 to 2025. Five-year average corn yields now run 177 (Warren) to 214 (Jasper, through 2023) bushels an acre; soybeans 54 to 65.

## What to do before next harvest

- **Storage and dryer sizing.** Size on the trend numbers in `06_expected_bushels.csv` (168 million bushels of corn across the area on the latest published acres) and keep a plan for a year 20% under that, which is what the average bad county-year looked like. Year-to-year corn yield swings in the area have averaged 14 (Jasper) to 23 (Dallas) bushels an acre since 2000; Polk averaged 19, with a 67-bushel jump from 2020 to 2021.
- **The July watch.** Track July rain for the Central climate division on the IEM from mid-July on and read the month total at the end. July rain under 2 inches with 20 or more days at 90F is the warning sign for corn: of the 156 county-years statewide that saw it, 73% ended 10% or more below trend, and in 2012 (1.6 inches and 38 hot days in the Central division) it was every county. The same sign only caught 41% of soybean county-years. This year ran the other way: 6.9 inches in July and 22 hot days, with 35.8 inches of April-to-September rain, the second-wettest season in the 27 years here behind 2010.
- **Rebuild the mix table when NASS publishes the 2026 county acres.** The 2025 county rows were loaded on May 5, 2026, so expect the 2026 rows around May 2027. The 2024 and 2025 area totals are missing the counties NASS combined, so do not read a trend into them.

## Two caveats

- **NASS now combines small counties.** Jasper's last published year is 2023, and 2024 shows only 73 corn counties statewide, so the 2026 expected bushels for Jasper rest on 2023 acres. Treat the area total as an estimate with that gap in it.
- **Weather is a division average.** The IEM series averages the whole Central division, so a storm that hit one county and missed the next does not show. It is good for the season-level watch, not for settling a claim about one farm.
