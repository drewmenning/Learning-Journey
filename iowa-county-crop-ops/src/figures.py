import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection

CORN = "#d98c21"
SOY = "#3b7a57"
GREY = "#777777"


def bad_year_share():
    q4 = pd.read_csv("data/outputs/04_trend_residual_bad_years.csv")
    share = q4.groupby(["commodity", "year"]).bad_year.mean().mul(100).unstack(0)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    years = share.index.values
    ax.bar(years - 0.2, share["CORN"], width=0.4, color=CORN, label="Corn")
    ax.bar(years + 0.2, share["SOYBEANS"], width=0.4, color=SOY, label="Soybeans")
    ax.set_ylabel("Share of published counties 10%+ below trend")
    ax.set_ylim(0, 100)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=60, fontsize=8)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter())
    ax.set_title("Iowa county yields against their straight-line trend, 2000 to 2025")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig("docs/figures/bad-year-share-by-year.png", dpi=150)
    plt.close(fig)


def weather_bad_vs_normal():
    q4 = pd.read_csv("data/outputs/04_trend_residual_bad_years.csv")
    lookup = pd.read_csv("data/lookups/county_to_district.csv")
    weather = pd.read_csv("data/processed/weather_district_season.csv")
    rows = q4.merge(lookup[["county_name", "climate_district"]], on="county_name")
    rows = rows.merge(weather[["climate_district", "year", "july_precip_in", "days_high_ge_90"]], on=["climate_district", "year"])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, crop, color in zip(axes, ["CORN", "SOYBEANS"], [CORN, SOY]):
        g = rows[rows.commodity == crop]
        ax.scatter(g.july_precip_in, g.pct_vs_trend, s=10, alpha=0.35, color=color, edgecolors="none")
        ax.axhline(-10, color=GREY, linewidth=1, linestyle="--")
        ax.set_title(crop.title())
        ax.set_xlabel("July rain in the county's climate division (inches)")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("County yield vs trend (%)")
    fig.suptitle("Dry Julys hold most of the bad years (one dot per county and year)")
    fig.tight_layout()
    fig.savefig("docs/figures/july-rain-vs-trend.png", dpi=150)
    plt.close(fig)


def production_map():
    geo = json.load(open("data/lookups/iowa_counties.geojson"))
    q1 = pd.read_csv("data/outputs/01_production_share.csv")
    draw = pd.read_csv("data/lookups/draw_area.csv", dtype=str)
    corn = q1[q1.commodity == "CORN"].set_index("county_name")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    polys, values, edges, widths = [], [], [], []
    for f in geo["features"]:
        name = f["properties"]["NAME"].upper()
        geom = f["geometry"]
        rings = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        value = corn.prod_per_year_bu.get(name, np.nan) / 1e6
        in_draw = f["id"] in set(draw.county_fips)
        for poly in rings:
            polys.append(poly[0])
            values.append(value)
            edges.append("black" if in_draw else "white")
            widths.append(1.6 if in_draw else 0.5)
    coll = PolyCollection(polys, array=np.array(values), cmap="YlOrBr", edgecolors=edges, linewidths=widths)
    ax.add_collection(coll)
    ax.autoscale()
    ax.set_aspect(1.3)
    ax.axis("off")
    cbar = fig.colorbar(coll, ax=ax, shrink=0.7)
    cbar.set_label("Corn production per published year, 2021 to 2025, million bushels")
    ax.set_title("Where the corn is: production per published year, 2021 to 2025, draw area outlined")
    fig.tight_layout()
    fig.savefig("docs/figures/corn-production-map.png", dpi=150)
    plt.close(fig)


def draw_area_mix():
    q2 = pd.read_csv("data/outputs/02_crop_mix_shift.csv")
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for county, g in q2.groupby("county_name"):
        ax.plot(g.year, g.corn_share_pct, marker="o", markersize=3, linewidth=1.2, label=county.title())
    ax.set_ylabel("Corn share of corn plus soybean planted acres (%)")
    ax.set_title("Crop mix in the draw area, 2000 to 2025")
    ax.legend(frameon=False, ncol=4, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig("docs/figures/draw-area-corn-share.png", dpi=150)
    plt.close(fig)


def main():
    bad_year_share()
    weather_bad_vs_normal()
    production_map()
    draw_area_mix()
    print("4 figures written to docs/figures")


if __name__ == "__main__":
    main()
