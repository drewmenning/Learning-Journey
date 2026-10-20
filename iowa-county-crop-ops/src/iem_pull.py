import urllib.parse
import urllib.request

BASE = "https://mesonet.agron.iastate.edu/cgi-bin/request/coop.py"
OUT = "data/raw/iem_climate_division_daily.csv"
STATIONS = ["IAC00%d" % i for i in range(1, 10)]
VARS = ["high", "low", "precip", "gdd_50_86", "temp_estimated", "precip_estimated"]
START = (2000, 1, 1)
END = (2026, 9, 30)


def fetch(station):
    params = [("network", "IACLIMATE"), ("stations", station),
              ("year1", START[0]), ("month1", START[1]), ("day1", START[2]),
              ("year2", END[0]), ("month2", END[1]), ("day2", END[2]),
              ("what", "view"), ("delim", "comma"), ("gis", "no")]
    params += [("vars[]", v) for v in VARS]
    url = BASE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=180) as resp:
        return resp.read().decode("utf-8", "replace")


def main():
    rows = 0
    with open(OUT, "w", newline="", encoding="utf-8") as out:
        wrote_header = False
        for station in STATIONS:
            text = fetch(station)
            for line in text.splitlines():
                if not line or line.startswith("#"):
                    continue
                if line.startswith("station,"):
                    if not wrote_header:
                        out.write(line + "\n")
                        wrote_header = True
                    continue
                out.write(line + "\n")
                rows += 1
            print(station, "done", flush=True)
    print(rows, "daily rows written to", OUT)


if __name__ == "__main__":
    main()
