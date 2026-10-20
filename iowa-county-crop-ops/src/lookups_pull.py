import urllib.request

URL = "https://www.ncei.noaa.gov/pub/data/cirs/climdiv/county-to-climdivs.txt"
OUT = "data/lookups/ncei_county_to_climdivs.txt"


def main():
    with urllib.request.urlopen(URL, timeout=60) as resp:
        text = resp.read().decode("utf-8", "replace")
    with open(OUT, "w", newline="", encoding="utf-8") as out:
        out.write(text)
    iowa = [l for l in text.splitlines() if l.startswith("19")]
    print(len(iowa), "Iowa county rows in", OUT)


if __name__ == "__main__":
    main()
