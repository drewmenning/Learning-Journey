-- Is the corn and soybean mix shifting in the draw area? Corn share of planted acres by county and year, with the change from the prior year.
WITH mix AS (
  SELECT c.county_name, f.year,
         SUM(CASE WHEN k.commodity = 'CORN' THEN f.acres_planted END) AS corn_acres,
         SUM(CASE WHEN k.commodity = 'SOYBEANS' THEN f.acres_planted END) AS soy_acres
  FROM fact_crop_county_year f
  JOIN dim_county c USING (county_fips)
  JOIN dim_crop k USING (crop_id)
  WHERE c.draw_area = 1
  GROUP BY c.county_name, f.year
),
share AS (
  SELECT county_name, year, corn_acres, soy_acres,
         100.0 * corn_acres / (corn_acres + soy_acres) AS corn_share
  FROM mix
  WHERE corn_acres IS NOT NULL AND soy_acres IS NOT NULL
)
SELECT county_name, year, corn_acres, soy_acres,
       ROUND(corn_share, 1) AS corn_share_pct,
       ROUND(corn_share - LAG(corn_share) OVER (PARTITION BY county_name ORDER BY year), 1) AS change_pts
FROM share
ORDER BY county_name, year;
