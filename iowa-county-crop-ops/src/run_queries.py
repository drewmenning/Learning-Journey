import glob
import os
import sqlite3

import pandas as pd

DB = "data/iowa_crops.db"
OUT_DIR = "data/outputs"


def main():
    con = sqlite3.connect(DB)
    for path in sorted(glob.glob("sql/analysis/*.sql")):
        name = os.path.splitext(os.path.basename(path))[0]
        frame = pd.read_sql_query(open(path).read(), con)
        out = os.path.join(OUT_DIR, name + ".csv")
        frame.to_csv(out, index=False)
        print(name, len(frame), "rows")
    con.close()


if __name__ == "__main__":
    main()
