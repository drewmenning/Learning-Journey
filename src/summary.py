import pandas as pd

OUT = "data/outputs/"


def county_weather():
    q4 = pd.read_csv(OUT + "04_trend_residual_bad_years.csv")
    lookup = pd.read_csv("data/lookups/county_to_district.csv")
    weather = pd.read_csv("data/processed/weather_district_season.csv")
    rows = q4.merge(lookup[["county_name", "climate_district"]], on="county_name")
    return rows.merge(weather[["climate_district", "year", "precip_in", "july_precip_in", "days_high_ge_90"]], on=["climate_district", "year"])


def worst_years(rows):
    by_year = rows.groupby(["commodity", "year"]).agg(
        counties_bad=("bad_year", "sum"), counties_published=("bad_year", "size"),
        median_pct_vs_trend=("pct_vs_trend", "median"),
        july_precip_in=("july_precip_in", "mean"), days_high_ge_90=("days_high_ge_90", "mean")).reset_index()
    by_year["share_bad_pct"] = (100 * by_year.counties_bad / by_year.counties_published).round(1)
    by_year = by_year.round({"median_pct_vs_trend": 1, "july_precip_in": 1, "days_high_ge_90": 1})
    return by_year.sort_values(["commodity", "share_bad_pct"], ascending=[True, False])


def july_rule(rows):
    hot = rows[(rows.july_precip_in < 2) & (rows.days_high_ge_90 >= 20)]
    out = hot.groupby("commodity").agg(county_years=("bad_year", "size"), bad=("bad_year", "sum")).reset_index()
    out["share_bad_pct"] = (100 * out.bad / out.county_years).round(1)
    out["rule"] = "July rain under 2 inches and 20 or more days at 90F in the county's climate division"
    return out


def draw_area_years(rows):
    d = rows[rows.draw_area == 1]
    out = d.groupby(["commodity", "year"]).agg(counties_bad=("bad_year", "sum"), counties_published=("bad_year", "size"),
                                              july_precip_in=("july_precip_in", "mean")).reset_index()
    out["half_or_more_bad"] = (out.counties_bad * 2 >= out.counties_published).astype(int)
    return out.round({"july_precip_in": 2})


def yield_swing():
    q3 = pd.read_csv(OUT + "03_rolling_yield_yoy.csv")
    d = q3[q3.draw_area == 1].dropna(subset=["yoy_change"])
    out = d.groupby(["commodity", "county_name"]).agg(mean_abs_yoy=("yoy_change", lambda s: s.abs().mean()),
                                                     max_abs_yoy=("yoy_change", lambda s: s.abs().max()),
                                                     years=("yoy_change", "size")).reset_index()
    return out.round(1)


def draw_area_totals():
    q1 = pd.read_csv(OUT + "01_production_share.csv")
    d = q1[q1.draw_area == 1].groupby("commodity").agg(prod_published_bu=("prod_published_bu", "sum"),
                                                     prod_per_year_bu=("prod_per_year_bu", "sum")).reset_index()
    state = q1.groupby("commodity").prod_per_year_bu.sum().rename("state_per_year_bu")
    d = d.merge(state, on="commodity")
    d["pct_of_state_per_year"] = (100 * d.prod_per_year_bu / d.state_per_year_bu).round(2)
    q2 = pd.read_csv(OUT + "02_crop_mix_shift.csv")
    mix = q2.groupby("year").agg(corn=("corn_acres", "sum"), soy=("soy_acres", "sum"), counties=("county_name", "size")).reset_index()
    mix["corn_share_pct"] = (100 * mix.corn / (mix.corn + mix.soy)).round(1)
    return d, mix


def main():
    rows = county_weather()
    worst_years(rows).to_csv(OUT + "summary_worst_years.csv", index=False)
    july_rule(rows).to_csv(OUT + "summary_july_rule.csv", index=False)
    draw_area_years(rows).to_csv(OUT + "summary_draw_area_bad_years.csv", index=False)
    yield_swing().to_csv(OUT + "summary_draw_area_yield_swing.csv", index=False)
    totals, mix = draw_area_totals()
    totals.to_csv(OUT + "summary_draw_area_totals.csv", index=False)
    mix.to_csv(OUT + "summary_draw_area_corn_share.csv", index=False)
    print("6 summary tables written to", OUT)


if __name__ == "__main__":
    main()
