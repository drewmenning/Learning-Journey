import json
import sys

import pandas as pd

OUT = "dashboard/iowa_crops_dashboard.html"
PLOTLY = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def load():
    geo = json.load(open("data/lookups/iowa_counties.geojson"))
    q1 = pd.read_csv("data/outputs/01_production_share.csv")
    q2 = pd.read_csv("data/outputs/02_crop_mix_shift.csv")
    q4 = pd.read_csv("data/outputs/04_trend_residual_bad_years.csv")
    q5 = pd.read_csv("data/outputs/05_weather_in_bad_years.csv")
    q6 = pd.read_csv("data/outputs/06_expected_bushels.csv")
    lookup = pd.read_csv("data/lookups/county_to_district.csv", dtype={"county_fips": str})
    weather = pd.read_csv("data/processed/weather_district_season.csv")
    fips = lookup.set_index("county_name").county_fips
    q1["county_fips"] = q1.county_name.map(fips)
    rows = q4.merge(lookup[["county_name", "climate_district"]], on="county_name")
    rows = rows.merge(weather[["climate_district", "year", "july_precip_in", "days_high_ge_90"]], on=["climate_district", "year"])
    share = q4.groupby(["commodity", "year"]).bad_year.mean().mul(100).round(1).unstack(0).reset_index()
    return {
        "geo": geo,
        "production": q1.to_dict("records"),
        "mix": q2.to_dict("records"),
        "trend": q4.to_dict("records"),
        "weather": q5.to_dict("records"),
        "expected": q6.to_dict("records"),
        "scatter": rows[["county_name", "commodity", "year", "pct_vs_trend", "july_precip_in", "days_high_ge_90"]].to_dict("records"),
        "badShare": share.to_dict("records"),
        "counties": sorted(q4.county_name.unique().tolist()),
    }


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Iowa county crop dashboard</title>
<script src="__PLOTLY__"></script>
<style>
  body { margin: 0; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: #1c1c1c; background: #fafaf7; }
  header { padding: 18px 24px 8px; }
  h1 { margin: 0; font-size: 22px; }
  .sub { color: #555; margin: 4px 0 0; }
  nav { display: flex; gap: 6px; padding: 10px 24px; border-bottom: 1px solid #ddd; flex-wrap: wrap; }
  nav button { border: 1px solid #ccc; background: #fff; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-size: 14px; }
  nav button.on { background: #1c1c1c; color: #fff; border-color: #1c1c1c; }
  section { display: none; padding: 16px 24px 32px; }
  section.on { display: block; }
  .row { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }
  select { font-size: 14px; padding: 6px; }
  .note { color: #555; font-size: 13.5px; max-width: 80ch; }
  .chart { width: 100%; height: 520px; }
  .half { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .half > div { min-width: 0; }
  @media (max-width: 900px) { .half { grid-template-columns: 1fr; } }
  table { border-collapse: collapse; font-size: 14px; margin-top: 8px; }
  th, td { text-align: right; padding: 5px 10px; border-bottom: 1px solid #e3e3e3; }
  th:first-child, td:first-child { text-align: left; }
</style>
</head>
<body>
<header>
  <h1>Iowa county corn and soybeans, 2000 to 2025</h1>
  <p class="sub">USDA NASS county estimates joined to Iowa Environmental Mesonet climate-division weather. Built from the SQL outputs in this repo.</p>
</header>
<nav>
  <button data-page="map" class="on">Where the grain is</button>
  <button data-page="trend">County yield vs trend</button>
  <button data-page="weather">Bad years and weather</button>
  <button data-page="elevator">Elevator view</button>
</nav>

<section id="map" class="on">
  <div class="row">
    <label>Crop <select id="mapCrop"><option value="CORN">Corn</option><option value="SOYBEANS">Soybeans</option></select></label>
    <span class="note">Average production per published year, 2021 to 2025. Counties NASS folded into combined-county rows every year show as missing; hover shows how many of the five years a county has. Draw area outlined in black.</span>
  </div>
  <div id="mapChart" class="chart"></div>
</section>

<section id="trend">
  <div class="row">
    <label>County <select id="trendCounty"></select></label>
    <label>Crop <select id="trendCrop"><option value="CORN">Corn</option><option value="SOYBEANS">Soybeans</option></select></label>
    <span class="note">Actual yield against a straight-line trend fit in SQL. Red markers are years 10% or more below trend.</span>
  </div>
  <div id="trendChart" class="chart"></div>
</section>

<section id="weather">
  <div class="half">
    <div><div id="shareChart" class="chart"></div></div>
    <div><div id="scatterChart" class="chart"></div></div>
  </div>
  <p class="note">Left: share of published counties 10% or more below trend each year. Right: every county and year against July rain in its climate division. Weather is a division average, so single-county storms do not show.</p>
  <div id="weatherTable"></div>
</section>

<section id="elevator">
  <div class="half">
    <div><div id="mixChart" class="chart"></div></div>
    <div><div id="expectedChart" class="chart"></div></div>
  </div>
  <p class="note">The draw area is Polk County plus the counties that share a boundary with it in the Census county outlines. Expected 2026 bushels are the 2026 trend yield times the latest published planted acres, scaled by the ten-year harvested-to-planted ratio. They are planning numbers for a trend year, with no weather in them.</p>
  <div id="expectedTable"></div>
</section>

<script>
const D = __DATA__;
const CORN = "#d98c21", SOY = "#3b7a57";
const draw = new Set(D.production.filter(r => r.draw_area === 1).map(r => r.county_fips));

document.querySelectorAll("nav button").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll("nav button").forEach(x => x.classList.toggle("on", x === b));
  document.querySelectorAll("section").forEach(s => s.classList.toggle("on", s.id === b.dataset.page));
  window.dispatchEvent(new Event("resize"));
}));

function drawMap() {
  const crop = document.getElementById("mapCrop").value;
  const rows = D.production.filter(r => r.commodity === crop && r.county_fips);
  const trace = {
    type: "choropleth", geojson: D.geo, locations: rows.map(r => r.county_fips),
    z: rows.map(r => r.prod_per_year_bu / 1e6), text: rows.map(r => r.county_name),
    customdata: rows.map(r => [r.pct_of_published_counties, r.rnk, r.years_published]),
    colorscale: crop === "CORN" ? [[0, "#fff7bc"], [0.5, "#fe9929"], [1, "#993404"]] : [[0, "#e5f5e0"], [0.5, "#74c476"], [1, "#006d2c"]],
    colorbar: { title: { text: "million bu per year" } },
    marker: { line: { color: rows.map(r => draw.has(r.county_fips) ? "black" : "white"), width: rows.map(r => draw.has(r.county_fips) ? 2 : 0.5) } },
    hovertemplate: "%{text}<br>%{z:.1f} million bu per published year<br>%{customdata[0]}% of published counties, rank %{customdata[1]}<br>%{customdata[2]} of 5 years published<extra></extra>"
  };
  Plotly.react("mapChart", [trace], { geo: { fitbounds: "locations", visible: false }, margin: { t: 10, b: 10, l: 10, r: 10 }, title: "" }, { responsive: true });
}

function drawTrend() {
  const county = document.getElementById("trendCounty").value;
  const crop = document.getElementById("trendCrop").value;
  const rows = D.trend.filter(r => r.county_name === county && r.commodity === crop);
  const color = crop === "CORN" ? CORN : SOY;
  const traces = [
    { x: rows.map(r => r.year), y: rows.map(r => r.trend_yield), mode: "lines", name: "Trend", line: { color: "#999", dash: "dash" } },
    { x: rows.map(r => r.year), y: rows.map(r => r.actual_yield), mode: "lines+markers", name: "Actual",
      line: { color: color }, marker: { size: 9, color: rows.map(r => r.bad_year ? "#c0392b" : color) },
      customdata: rows.map(r => r.pct_vs_trend), hovertemplate: "%{x}: %{y} bu/acre (%{customdata:+.1f}% vs trend)<extra></extra>" }
  ];
  Plotly.react("trendChart", traces, { title: county + " " + crop.toLowerCase() + " yield, bushels per acre",
    xaxis: { dtick: 2 }, yaxis: { title: "bu / acre", rangemode: "tozero" }, margin: { t: 50 }, legend: { orientation: "h" } }, { responsive: true });
}

function drawWeather() {
  const years = D.badShare.map(r => r.year);
  Plotly.react("shareChart", [
    { type: "bar", x: years, y: D.badShare.map(r => r.CORN), name: "Corn", marker: { color: CORN } },
    { type: "bar", x: years, y: D.badShare.map(r => r.SOYBEANS), name: "Soybeans", marker: { color: SOY } }
  ], { title: "Share of counties 10%+ below trend", yaxis: { ticksuffix: "%", range: [0, 100] }, barmode: "group", margin: { t: 50 }, legend: { orientation: "h" } }, { responsive: true });
  const traces = ["CORN", "SOYBEANS"].map(crop => {
    const rows = D.scatter.filter(r => r.commodity === crop);
    return { type: "scatter", mode: "markers", name: crop.toLowerCase(), x: rows.map(r => r.july_precip_in), y: rows.map(r => r.pct_vs_trend),
      text: rows.map(r => r.county_name + " " + r.year), marker: { size: 6, opacity: 0.45, color: crop === "CORN" ? CORN : SOY },
      hovertemplate: "%{text}<br>July rain %{x} in<br>%{y:+.1f}% vs trend<extra></extra>" };
  });
  Plotly.react("scatterChart", traces, { title: "County year vs July rain in its climate division", xaxis: { title: "July rain, inches" },
    yaxis: { title: "% vs trend" }, shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: -10, y1: -10, line: { color: "#999", dash: "dash" } }], margin: { t: 50 }, legend: { orientation: "h" } }, { responsive: true });
  const w = D.weather;
  document.getElementById("weatherTable").innerHTML = "<table><tr><th>Crop</th><th>Year type</th><th>County years</th><th>July rain (in)</th><th>Season rain (in)</th><th>Days 90F+</th><th>GDD base 50</th><th>Harvested / planted</th><th>Avg vs trend</th></tr>" +
    w.map(r => `<tr><td>${r.commodity}</td><td>${r.year_type}</td><td>${r.county_years}</td><td>${r.avg_july_precip_in}</td><td>${r.avg_season_precip_in}</td><td>${r.avg_days_90f}</td><td>${r.avg_gdd50}</td><td>${r.harvested_to_planted}</td><td>${r.avg_pct_vs_trend}%</td></tr>`).join("") + "</table>";
}

function drawElevator() {
  const counties = [...new Set(D.mix.map(r => r.county_name))];
  Plotly.react("mixChart", counties.map(c => {
    const rows = D.mix.filter(r => r.county_name === c);
    return { x: rows.map(r => r.year), y: rows.map(r => r.corn_share_pct), mode: "lines+markers", name: c, marker: { size: 4 } };
  }), { title: "Corn share of corn plus soybean planted acres", yaxis: { ticksuffix: "%" }, margin: { t: 50 }, legend: { orientation: "h" } }, { responsive: true });
  const e = D.expected;
  Plotly.react("expectedChart", ["CORN", "SOYBEANS"].map(crop => {
    const rows = e.filter(r => r.commodity === crop);
    return { type: "bar", name: crop.toLowerCase(), x: rows.map(r => r.county_name), y: rows.map(r => r.expected_bu_2026 / 1e6), marker: { color: crop === "CORN" ? CORN : SOY } };
  }), { title: "Expected 2026 bushels by county (millions)", barmode: "group", margin: { t: 50 }, legend: { orientation: "h" } }, { responsive: true });
  const total = {};
  e.forEach(r => { total[r.commodity] = (total[r.commodity] || 0) + r.expected_bu_2026; });
  document.getElementById("expectedTable").innerHTML = "<table><tr><th>County</th><th>Crop</th><th>Acres year</th><th>Planted acres</th><th>Harvested / planted</th><th>Trend yield 2026</th><th>Expected bushels</th></tr>" +
    e.map(r => `<tr><td>${r.county_name}</td><td>${r.commodity}</td><td>${r.acres_year}</td><td>${r.latest_planted_acres.toLocaleString()}</td><td>${r.harvested_to_planted_10yr}</td><td>${r.trend_yield_2026}</td><td>${Math.round(r.expected_bu_2026).toLocaleString()}</td></tr>`).join("") +
    Object.keys(total).map(k => `<tr><td><b>Draw area total</b></td><td>${k}</td><td></td><td></td><td></td><td></td><td><b>${Math.round(total[k]).toLocaleString()}</b></td></tr>`).join("") + "</table>";
}

const sel = document.getElementById("trendCounty");
D.counties.forEach(c => { const o = document.createElement("option"); o.value = c; o.textContent = c; if (c === "POLK") o.selected = true; sel.appendChild(o); });
document.getElementById("mapCrop").addEventListener("change", drawMap);
sel.addEventListener("change", drawTrend);
document.getElementById("trendCrop").addEventListener("change", drawTrend);
drawMap(); drawTrend(); drawWeather(); drawElevator();
</script>
</body>
</html>
"""


def main():
    plotly = sys.argv[1] if len(sys.argv) > 1 else PLOTLY
    data = load()
    html = PAGE.replace("__PLOTLY__", plotly).replace("__DATA__", json.dumps(data, separators=(",", ":")))
    open(OUT, "w", encoding="utf-8").write(html)
    print(OUT, len(html), "bytes")


if __name__ == "__main__":
    main()
