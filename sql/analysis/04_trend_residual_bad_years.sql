-- Which years were the bad ones, and how bad against trend? Every county year scored against the straight-line trend in v_yield_trend (sql/schema.sql). A bad year is 10 percent or more below trend, judged on the rounded figure shown.
SELECT c.county_name, c.draw_area, k.commodity, t.year,
       ROUND(t.actual_yield, 1) AS actual_yield,
       ROUND(t.trend_yield, 1) AS trend_yield,
       t.pct_vs_trend,
       CASE WHEN t.pct_vs_trend <= -10.0 THEN 1 ELSE 0 END AS bad_year,
       ROUND(t.slope, 2) AS trend_slope_bu_per_year,
       t.years_fit
FROM v_yield_trend t
JOIN dim_county c USING (county_fips)
JOIN dim_crop k USING (crop_id)
ORDER BY k.commodity, c.county_name, t.year;
