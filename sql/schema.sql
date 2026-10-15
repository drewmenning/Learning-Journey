DROP TABLE IF EXISTS fact_weather_district_season;
DROP TABLE IF EXISTS fact_crop_state_year;
DROP TABLE IF EXISTS fact_crop_county_year;
DROP TABLE IF EXISTS dim_crop;
DROP TABLE IF EXISTS dim_county;

CREATE TABLE dim_county (
  county_fips TEXT PRIMARY KEY,
  county_name TEXT NOT NULL,
  asd_code TEXT NOT NULL,
  climate_district TEXT NOT NULL,
  draw_area INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE dim_crop (
  crop_id INTEGER PRIMARY KEY,
  commodity TEXT NOT NULL UNIQUE,
  unit TEXT NOT NULL
);

CREATE TABLE fact_crop_county_year (
  county_fips TEXT NOT NULL REFERENCES dim_county (county_fips),
  crop_id INTEGER NOT NULL REFERENCES dim_crop (crop_id),
  year INTEGER NOT NULL,
  acres_planted REAL,
  acres_harvested REAL,
  yield_bu_acre REAL,
  production_bu REAL,
  source TEXT NOT NULL,
  PRIMARY KEY (county_fips, crop_id, year)
);

CREATE TABLE fact_crop_state_year (
  crop_id INTEGER NOT NULL REFERENCES dim_crop (crop_id),
  year INTEGER NOT NULL,
  acres_planted REAL,
  acres_harvested REAL,
  yield_bu_acre REAL,
  production_bu REAL,
  last_loaded TEXT,
  PRIMARY KEY (crop_id, year)
);

CREATE TABLE fact_weather_district_season (
  climate_district TEXT NOT NULL,
  year INTEGER NOT NULL,
  precip_in REAL,
  july_precip_in REAL,
  gdd50 REAL,
  days_high_ge_90 INTEGER,
  avg_high_f REAL,
  season_days INTEGER,
  PRIMARY KEY (climate_district, year)
);

CREATE INDEX idx_fact_crop_year ON fact_crop_county_year (year, crop_id);

DROP VIEW IF EXISTS v_yield_trend;
CREATE VIEW v_yield_trend AS
WITH base AS (
  SELECT county_fips, crop_id, year, yield_bu_acre AS y, year - 2000.0 AS x
  FROM fact_crop_county_year
  WHERE yield_bu_acre IS NOT NULL
),
stats AS (
  SELECT county_fips, crop_id, AVG(x) AS xbar, AVG(y) AS ybar, COUNT(*) AS n
  FROM base
  GROUP BY county_fips, crop_id
),
fit AS (
  SELECT b.county_fips, b.crop_id, s.xbar, s.ybar, s.n,
         SUM((b.x - s.xbar) * (b.y - s.ybar)) / SUM((b.x - s.xbar) * (b.x - s.xbar)) AS slope
  FROM base b
  JOIN stats s USING (county_fips, crop_id)
  GROUP BY b.county_fips, b.crop_id
)
SELECT b.county_fips, b.crop_id, b.year,
       b.y AS actual_yield,
       f.ybar + f.slope * (b.x - f.xbar) AS trend_yield,
       ROUND(100.0 * (b.y - (f.ybar + f.slope * (b.x - f.xbar))) / (f.ybar + f.slope * (b.x - f.xbar)), 1) AS pct_vs_trend,
       f.slope, f.xbar, f.ybar, f.n AS years_fit
FROM base b
JOIN fit f USING (county_fips, crop_id);
