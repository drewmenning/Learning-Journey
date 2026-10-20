-- What yield should storage be planned on, and how much does it swing? Year-over-year change and a five-row rolling average per county and crop. ROWS counts rows, not years, so years_spanned shows when the window stretches over a year NASS did not publish.
SELECT c.county_name, c.draw_area, k.commodity, f.year, f.yield_bu_acre,
       ROUND(f.yield_bu_acre - LAG(f.yield_bu_acre) OVER w, 1) AS yoy_change,
       ROUND(AVG(f.yield_bu_acre) OVER (w ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 1) AS yield_5yr_avg,
       COUNT(*) OVER (w ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS rows_in_avg,
       f.year - FIRST_VALUE(f.year) OVER (w ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) + 1 AS years_spanned
FROM fact_crop_county_year f
JOIN dim_county c USING (county_fips)
JOIN dim_crop k USING (crop_id)
WHERE f.yield_bu_acre IS NOT NULL
WINDOW w AS (PARTITION BY f.county_fips, f.crop_id ORDER BY f.year)
ORDER BY c.county_name, k.commodity, f.year;
