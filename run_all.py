import subprocess
import sys

STEPS = [
    ["src/lookups_pull.py"],
    ["src/iem_pull.py"],
    ["src/nass_pull.py"],
    ["src/clean.py"],
    ["src/draw_area.py"],
    ["src/load_sqlite.py"],
    ["src/run_queries.py"],
    ["src/validate.py"],
    ["src/summary.py"],
    ["src/figures.py"],
    ["src/build_dashboard.py"],
]


def main():
    skip_pull = "--no-pull" in sys.argv
    for step in STEPS:
        if skip_pull and step[0].endswith("_pull.py"):
            print("skipping", step[0], "(using the committed raw files)")
            continue
        print("==", step[0])
        subprocess.run([sys.executable] + step, check=True)


if __name__ == "__main__":
    main()
