import json

import pandas as pd

GEO = "data/lookups/iowa_counties.geojson"
OUT = "data/lookups/draw_area.csv"
CENTER = "19153"


def boundary_points(geometry):
    points = set()
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    for poly in polys:
        for ring in poly:
            for x, y in ring:
                points.add((round(x, 5), round(y, 5)))
    return points


def main():
    features = json.load(open(GEO))["features"]
    points = {f["id"]: boundary_points(f["geometry"]) for f in features}
    names = {f["id"]: f["properties"]["NAME"] for f in features}
    center = points[CENTER]
    rows = []
    for fips, pts in points.items():
        shared = len(center & pts)
        if fips == CENTER or shared >= 2:
            rows.append({"county_fips": fips, "county_name": names[fips].upper(), "shared_boundary_points": shared,
                         "role": "center" if fips == CENTER else "neighbor"})
    out = pd.DataFrame(rows).sort_values(["role", "county_name"])
    out.to_csv(OUT, index=False)
    print(len(out), "counties in the draw area:", ", ".join(out.county_name))


if __name__ == "__main__":
    main()
