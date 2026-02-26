#!/usr/bin/env python3
# save as tools/fips_to_string.py and run from repo root:
#   python tools/fips_to_string.py --folder Environmental_GDB_NPDES/data
#   python tools/fips_to_string.py --folder Socioeconomic/data

import argparse
from pathlib import Path
import pandas as pd

CANDS = ["fips","FIPS","GEOID","GEOID10","COUNTYFP","COUNTY_FIPS"]

def normalize_to_string_fips(path: Path):
    try:
        df = pd.read_csv(path, dtype="string")
    except Exception as e:
        print(f"[SKIP] {path}: {e}")
        return
    src = None
    for c in CANDS:
        if c in df.columns:
            src = c; break
    if not src:
        print(f"[SKIP] {path}: no fips-like column")
        return
    # clean & zfill, store in 'fips'
    f = df[src].astype("string").str.replace(r"\D","", regex=True).str.zfill(5)
    df["fips"] = f
    out = path  # overwrite
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        path.rename(bak)
    df.to_csv(out, index=False)
    print(f"[OK]  {path} -> normalized 'fips' as string (backup: {bak.name})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    args = ap.parse_args()
    for csv in Path(args.folder).rglob("*.csv"):
        normalize_to_string_fips(csv)
        
        
