import sys

import pandas as pd

sys.path.insert(0, "src")
from clean import to_number


def test_to_number_handles_commas_and_withheld():
    assert to_number("1,134,000") == 1134000.0
    assert to_number(" 54.5 ") == 54.5
    assert to_number("(D)") is None
    assert to_number("") is None


def test_county_table_covers_99_counties_and_two_crops():
    county = pd.read_csv("data/processed/crop_county_year.csv", dtype={"county_fips": str})
    assert county.county_fips.nunique() == 99
    assert set(county.crop) == {"CORN", "SOYBEANS"}
    assert county.year.min() == 2000
    assert not county.duplicated(["county_fips", "crop", "year"]).any()


def test_acres_and_production_are_consistent():
    county = pd.read_csv("data/processed/crop_county_year.csv")
    assert (county.acres_harvested <= county.acres_planted).all()
    implied = county.acres_harvested * county.yield_bu_acre
    assert ((implied - county.production_bu).abs() <= 0.02 * county.production_bu).all()


def test_every_district_season_has_183_days():
    weather = pd.read_csv("data/processed/weather_district_season.csv")
    assert (weather.season_days == 183).all()
    assert weather.climate_district.nunique() == 9
    assert weather.july_precip_in.between(0, 20).all()


def test_nass_districts_match_climate_divisions():
    lookup = pd.read_csv("data/lookups/county_to_district.csv")
    assert len(lookup) == 99
    assert lookup.same_boundary.all()
