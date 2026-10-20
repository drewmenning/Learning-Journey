-- Did the bad years line up with weather and abandoned acres? Season weather for each county's climate division, averaged over bad and normal county years.
SELECT k.commodity,
       CASE WHEN t.pct_vs_trend <= -10.0 THEN 'bad' ELSE 'normal' END AS year_type,
       COUNT(*) AS county_years,
       ROUND(AVG(w.july_precip_in), 2) AS avg_july_precip_in,
       ROUND(AVG(w.precip_in), 2) AS avg_season_precip_in,
       ROUND(AVG(w.days_high_ge_90), 1) AS avg_days_90f,
       ROUND(AVG(w.gdd50), 0) AS avg_gdd50,
       ROUND(AVG(1.0 * f.acres_harvested / f.acres_planted), 3) AS harvested_to_planted,
       ROUND(AVG(t.pct_vs_trend), 1) AS avg_pct_vs_trend
FROM v_yield_trend t
JOIN fact_crop_county_year f USING (county_fips, crop_id, year)
JOIN dim_county c USING (county_fips)
JOIN dim_crop k USING (crop_id)
JOIN fact_weather_district_season w ON w.climate_district = c.climate_district AND w.year = t.year
GROUP BY k.commodity, year_type
ORDER BY k.commodity, year_type;
