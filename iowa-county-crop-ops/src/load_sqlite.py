import sqlite3

import pandas as pd

DB = "data/iowa_crops.db"
CROPS = [(1, "CORN", "bushels of grain"), (2, "SOYBEANS", "bushels")]


def main():
    county = pd.read_csv("data/processed/crop_county_year.csv", dtype={"county_fips": str, "asd_code": str})
    state = pd.read_csv("data/processed/crop_state_year.csv")
    weather = pd.read_csv("data/processed/weather_district_season.csv")
    lookup = pd.read_csv("data/lookups/county_to_district.csv", dtype=str)
    draw = pd.read_csv("data/lookups/draw_area.csv", dtype=str)
    crop_id = {c[1]: c[0] for c in CROPS}

    con = sqlite3.connect(DB)
    con.executescript(open("sql/schema.sql").read())
    con.executemany("INSERT INTO dim_crop VALUES (?, ?, ?)", CROPS)
    dim = lookup[["county_fips", "county_name", "asd_code", "climate_district"]].copy()
    dim["draw_area"] = dim.county_fips.isin(draw.county_fips).astype(int)
    dim.to_sql("dim_county", con, if_exists="append", index=False)

    fact = county.copy()
    fact["crop_id"] = fact.crop.map(crop_id)
    fact = fact[["county_fips", "crop_id", "year", "acres_planted", "acres_harvested", "yield_bu_acre", "production_bu", "source"]]
    fact.to_sql("fact_crop_county_year", con, if_exists="append", index=False)

    st = state.copy()
    st["crop_id"] = st.crop.map(crop_id)
    st = st[["crop_id", "year", "acres_planted", "acres_harvested", "yield_bu_acre", "production_bu", "last_loaded"]]
    st.to_sql("fact_crop_state_year", con, if_exists="append", index=False)

    weather[["climate_district", "year", "precip_in", "july_precip_in", "gdd50", "days_high_ge_90", "avg_high_f", "season_days"]].to_sql(
        "fact_weather_district_season", con, if_exists="append", index=False)
    con.commit()
    for table in ["dim_county", "dim_crop", "fact_crop_county_year", "fact_crop_state_year", "fact_weather_district_season"]:
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(table, n)
    con.close()


if __name__ == "__main__":
    main()
