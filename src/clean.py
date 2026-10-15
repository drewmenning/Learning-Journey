import pandas as pd

RAW_NASS = "data/raw/nass_qs_crops_ia_corn_soy.tsv"
RAW_IEM = "data/raw/iem_climate_division_daily.csv"
RAW_NCEI = "data/lookups/ncei_county_to_climdivs.txt"

SERIES = {
    "CORN - ACRES PLANTED": ("CORN", "acres_planted"),
    "CORN, GRAIN - ACRES HARVESTED": ("CORN", "acres_harvested"),
    "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE": ("CORN", "yield_bu_acre"),
    "CORN, GRAIN - PRODUCTION, MEASURED IN BU": ("CORN", "production_bu"),
    "SOYBEANS - ACRES PLANTED": ("SOYBEANS", "acres_planted"),
    "SOYBEANS - ACRES HARVESTED": ("SOYBEANS", "acres_harvested"),
    "SOYBEANS - YIELD, MEASURED IN BU / ACRE": ("SOYBEANS", "yield_bu_acre"),
    "SOYBEANS - PRODUCTION, MEASURED IN BU": ("SOYBEANS", "production_bu"),
}
MEASURES = ["acres_planted", "acres_harvested", "yield_bu_acre", "production_bu"]
SEASON_START = "04-01"
SEASON_END = "09-30"


def to_number(value):
    text = value.strip().replace(",", "")
    if text == "" or text.startswith("("):
        return None
    return float(text)


def annual_totals(frame, level):
    rows = frame[(frame.AGG_LEVEL_DESC == level) & (frame.DOMAIN_DESC == "TOTAL")
                 & (frame.FREQ_DESC == "ANNUAL") & (frame.REFERENCE_PERIOD_DESC == "YEAR")
                 & (frame.SHORT_DESC.isin(SERIES))].copy()
    rows["crop"] = rows.SHORT_DESC.map(lambda s: SERIES[s][0])
    rows["measure"] = rows.SHORT_DESC.map(lambda s: SERIES[s][1])
    rows["value"] = rows.VALUE.map(to_number)
    rows["year"] = rows.YEAR.astype(int)
    return rows


def county_table(nass):
    rows = annual_totals(nass, "COUNTY")
    rows = rows[rows.COUNTY_ANSI != ""]
    rows["county_fips"] = rows.STATE_ANSI + rows.COUNTY_ANSI
    wide = rows.pivot_table(index=["county_fips", "COUNTY_NAME", "ASD_CODE", "crop", "year"],
                            columns="measure", values="value", aggfunc="first").reset_index()
    wide = wide.rename(columns={"COUNTY_NAME": "county_name", "ASD_CODE": "asd_code"})
    for m in MEASURES:
        if m not in wide:
            wide[m] = None
    wide["source"] = "SURVEY"
    cols = ["county_fips", "county_name", "asd_code", "crop", "year"] + MEASURES + ["source"]
    return wide[cols].sort_values(["county_fips", "crop", "year"])


def state_table(nass):
    rows = annual_totals(nass, "STATE")
    wide = rows.pivot_table(index=["crop", "year"], columns="measure", values="value", aggfunc="first").reset_index()
    loaded = rows.groupby(["crop", "year"]).LOAD_TIME.max().reset_index().rename(columns={"LOAD_TIME": "last_loaded"})
    wide = wide.merge(loaded, on=["crop", "year"])
    return wide[["crop", "year"] + MEASURES + ["last_loaded"]].sort_values(["crop", "year"])


def district_lookup(county):
    ncei = pd.read_csv(RAW_NCEI, sep=r"\s+", skiprows=3, dtype=str)
    ncei = ncei[ncei.POSTAL_FIPS_ID.str.startswith("19")]
    ncei["climdiv_code"] = ncei.CLIMDIV_ID
    ncei["climate_district"] = "IAC0" + ncei.CLIMDIV_ID.str[-2:]
    counties = county[["county_fips", "county_name", "asd_code"]].drop_duplicates()
    out = counties.merge(ncei[["POSTAL_FIPS_ID", "climdiv_code", "climate_district"]],
                         left_on="county_fips", right_on="POSTAL_FIPS_ID", how="left").drop(columns="POSTAL_FIPS_ID")
    out["asd_district"] = out.asd_code.str[0].astype(int)
    out["climdiv_district"] = out.climdiv_code.str[-1].astype(int)
    out["same_boundary"] = out.asd_district == out.climdiv_district
    return out.sort_values("county_fips")


def weather_table():
    daily = pd.read_csv(RAW_IEM)
    daily["date"] = pd.to_datetime(daily.day, format="%Y/%m/%d")
    daily["year"] = daily.date.dt.year
    daily["mmdd"] = daily.date.dt.strftime("%m-%d")
    season = daily[(daily.mmdd >= SEASON_START) & (daily.mmdd <= SEASON_END)].copy()
    season["is_july"] = season.date.dt.month == 7
    season["hot"] = season.high >= 90
    grouped = season.groupby(["station", "year"])
    out = pd.DataFrame({
        "precip_in": grouped.precip.sum(),
        "july_precip_in": grouped.apply(lambda g: g.loc[g.is_july, "precip"].sum()),
        "gdd50": grouped.gdd_50_86.sum(),
        "days_high_ge_90": grouped.hot.sum(),
        "avg_high_f": grouped.high.mean(),
        "season_days": grouped.size(),
    }).reset_index().rename(columns={"station": "climate_district"})
    out["climdiv_code"] = "13" + out.climate_district.str[-2:]
    cols = ["climate_district", "climdiv_code", "year", "precip_in", "july_precip_in", "gdd50", "days_high_ge_90", "avg_high_f", "season_days"]
    return out[cols].round(2)


def main():
    nass = pd.read_csv(RAW_NASS, sep="\t", dtype=str, keep_default_na=False)
    county = county_table(nass)
    county.to_csv("data/processed/crop_county_year.csv", index=False)
    state = state_table(nass)
    state.to_csv("data/processed/crop_state_year.csv", index=False)
    lookup = district_lookup(county)
    lookup.to_csv("data/lookups/county_to_district.csv", index=False)
    weather = weather_table()
    weather.to_csv("data/processed/weather_district_season.csv", index=False)
    print(len(county), "county crop years,", len(state), "state crop years,", len(lookup), "counties,", len(weather), "district seasons")
    print("counties whose NASS district and climate division differ:", int((~lookup.same_boundary).sum()))


if __name__ == "__main__":
    main()
