-- Where is the grain, and what share of the state is it? Production per published year, 2021 to 2025, so a county NASS skipped in some years is not penalized for the gap.
WITH recent AS (
  SELECT c.county_fips, c.county_name, c.draw_area, k.commodity, f.production_bu
  FROM fact_crop_county_year f
  JOIN dim_county c USING (county_fips)
  JOIN dim_crop k USING (crop_id)
  WHERE f.year BETWEEN 2021 AND 2025
),
by_county AS (
  SELECT county_fips, county_name, draw_area, commodity,
         SUM(production_bu) AS prod_published_bu,
         COUNT(*) AS years_published,
         AVG(production_bu) AS prod_per_year_bu
  FROM recent
  GROUP BY county_fips, county_name, draw_area, commodity
)
SELECT commodity, county_name, draw_area, years_published,
       prod_published_bu,
       ROUND(prod_per_year_bu, 0) AS prod_per_year_bu,
       ROUND(100.0 * prod_per_year_bu / SUM(prod_per_year_bu) OVER (PARTITION BY commodity), 2) AS pct_of_published_counties,
       RANK() OVER (PARTITION BY commodity ORDER BY prod_per_year_bu DESC) AS rnk
FROM by_county
ORDER BY commodity, rnk;
