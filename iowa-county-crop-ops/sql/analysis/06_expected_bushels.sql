-- How many bushels should the draw area expect this fall? Trend yield for 2026 times the latest published planted acres, scaled by the ten-year harvested-to-planted ratio. Planning numbers, not a forecast.
WITH fit AS (
  SELECT DISTINCT county_fips, crop_id, slope, xbar, ybar
  FROM v_yield_trend
),
latest AS (
  SELECT county_fips, crop_id, MAX(year) AS acres_year
  FROM fact_crop_county_year
  WHERE acres_planted IS NOT NULL
  GROUP BY county_fips, crop_id
),
ratio AS (
  SELECT county_fips, crop_id,
         SUM(acres_harvested) / SUM(acres_planted) AS harvested_to_planted
  FROM fact_crop_county_year
  WHERE year BETWEEN 2016 AND 2025 AND acres_planted IS NOT NULL AND acres_harvested IS NOT NULL
  GROUP BY county_fips, crop_id
)
SELECT c.county_name, k.commodity,
       l.acres_year,
       f.acres_planted AS latest_planted_acres,
       ROUND(r.harvested_to_planted, 3) AS harvested_to_planted_10yr,
       ROUND(t.ybar + t.slope * (2026 - 2000.0 - t.xbar), 1) AS trend_yield_2026,
       ROUND(f.acres_planted * r.harvested_to_planted * (t.ybar + t.slope * (2026 - 2000.0 - t.xbar)), 0) AS expected_bu_2026
FROM dim_county c
CROSS JOIN dim_crop k
JOIN latest l ON l.county_fips = c.county_fips AND l.crop_id = k.crop_id
JOIN fact_crop_county_year f ON f.county_fips = c.county_fips AND f.crop_id = k.crop_id AND f.year = l.acres_year
JOIN ratio r ON r.county_fips = c.county_fips AND r.crop_id = k.crop_id
JOIN fit t ON t.county_fips = c.county_fips AND t.crop_id = k.crop_id
WHERE c.draw_area = 1
ORDER BY k.commodity, c.county_name;
