import gzip
import io
import re
import sys
import urllib.request

DATASETS = "https://www.nass.usda.gov/datasets/"
OUT = "data/raw/nass_qs_crops_ia_corn_soy.tsv"
COMMODITIES = {"CORN", "SOYBEANS"}
HEADERS = {"User-Agent": "iowa-county-crop-ops (data pull script)"}


def latest_crops_file():
    req = urllib.request.Request(DATASETS, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp:
        page = resp.read().decode("utf-8", "replace")
    names = sorted(set(re.findall(r"qs\.crops_\d{8}\.txt\.gz", page)))
    return DATASETS + names[-1]


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else latest_crops_file()
    print("pulling", url, flush=True)
    kept = 0
    seen = 0
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=120) as resp, gzip.GzipFile(fileobj=resp) as gz, open(OUT, "w", newline="", encoding="utf-8") as out:
        text = io.TextIOWrapper(gz, encoding="utf-8", errors="replace", newline="")
        header = next(text)
        out.write(header)
        cols = header.rstrip("\r\n").split("\t")
        i_state = cols.index("STATE_ALPHA")
        i_comm = cols.index("COMMODITY_DESC")
        i_src = cols.index("SOURCE_DESC")
        i_year = cols.index("YEAR")
        for line in text:
            seen += 1
            if "\tIA\t" not in line:
                continue
            f = line.split("\t")
            if f[i_state] == "IA" and f[i_comm] in COMMODITIES and f[i_src] == "SURVEY" and f[i_year] >= "2000":
                out.write(line)
                kept += 1
            if seen % 5000000 == 0:
                print(seen, "lines read,", kept, "kept", flush=True)
    print("source", url)
    print(kept, "rows written to", OUT, "from", seen, "lines")


if __name__ == "__main__":
    main()
