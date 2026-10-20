import sqlite3

import numpy as np
import pandas as pd

DB = "data/iowa_crops.db"


def test_tables_are_loaded():
    con = sqlite3.connect(DB)
    counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ["dim_county", "dim_crop", "fact_crop_county_year", "fact_weather_district_season"]}
    con.close()
    assert counts["dim_county"] == 99
    assert counts["dim_crop"] == 2
    assert counts["fact_crop_county_year"] > 4000
    assert counts["fact_weather_district_season"] == 9 * 27


def test_production_shares_sum_to_100_per_crop():
    q1 = pd.read_csv("data/outputs/01_production_share.csv")
    for crop, g in q1.groupby("commodity"):
        assert abs(g.pct_of_published_counties.sum() - 100) < 0.2
        assert g.rnk.min() == 1


def test_sql_trend_matches_numpy_for_polk_corn():
    q4 = pd.read_csv("data/outputs/04_trend_residual_bad_years.csv")
    rows = q4[(q4.county_name == "POLK") & (q4.commodity == "CORN")].sort_values("year")
    slope, intercept = np.polyfit(rows.year - 2000.0, rows.actual_yield, 1)
    expected = intercept + slope * (rows.year - 2000.0)
    assert np.allclose(rows.trend_yield, expected, atol=0.15)


def test_rolling_average_window_is_five_rows_and_reports_gaps():
    q3 = pd.read_csv("data/outputs/03_rolling_yield_yoy.csv")
    assert q3.rows_in_avg.max() == 5
    assert (q3.years_spanned >= q3.rows_in_avg).all()
    assert (q3.years_spanned > 5).sum() > 0
    first = q3.groupby(["county_name", "commodity"]).head(1)
    assert first.yoy_change.isna().all()


def test_bad_year_flag_is_consistent_with_shown_percent():
    q4 = pd.read_csv("data/outputs/04_trend_residual_bad_years.csv")
    assert (q4.bad_year == (q4.pct_vs_trend <= -10).astype(int)).all()
