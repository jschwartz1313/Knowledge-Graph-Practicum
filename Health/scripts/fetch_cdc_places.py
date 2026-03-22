"""
fetch_cdc_places.py
Fetches county-level health measure data for North Carolina from the
CDC PLACES API (Socrata SODA endpoint) and saves a clean CSV.

Source:
    PLACES: Local Data for Better Health, County Data 2024 release
    https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-20/swc5-untb

Output:
    cdc_places_nc_counties.csv — one row per county, one column per measure

Measures extracted (all are age-adjusted prevalence % unless noted):
    ARTHRITIS       — Arthritis among adults
    BPHIGH          — High blood pressure among adults
    CANCER          — Cancer (excl. skin) among adults
    CASTHMA         — Current asthma among adults
    CHD             — Coronary heart disease among adults
    COPD            — COPD among adults
    DEPRESSION      — Depression among adults
    DIABETES        — Diabetes among adults
    HIGHCHOL        — High cholesterol among adults (screened in past 5 yrs)
    KIDNEY          — Chronic kidney disease among adults
    OBESITY         — Obesity among adults
    STROKE          — Stroke among adults
    TEETHLOST       — All teeth lost among adults 65+
    BINGE           — Binge drinking among adults
    CSMOKING        — Current smoking among adults
    LPA             — No leisure-time physical activity
    SLEEP           — Short sleep duration (<7 hrs)
    CHECKUP         — Annual checkup among adults
    CHOLSCREEN      — Cholesterol screening among adults
    COLON_SCREEN    — Colorectal cancer screening among adults 45-75
    COREM           — Core preventive services for older men 65+
    COREW           — Core preventive services for older women 65+
    MAMMOUSE        — Mammography use among women 50-74
    PAPTEST         — Pap smear use among women 21-65
    DENTAL          — Dental visit in past year among adults
    HEARING         — Hearing disability among adults
    VISION          — Vision disability among adults
    COGNITION       — Cognitive disability among adults
    MOBILITY        — Mobility disability among adults
    SELFCARE        — Self-care disability among adults
    INDEPLIVE       — Independent living disability among adults
    ACCESS2         — No health insurance among adults 18-64
"""

import requests
import pandas as pd
from pathlib import Path

# Socrata SODA API endpoint for PLACES County Data 2024
API_URL = "https://data.cdc.gov/resource/swc5-untb.json"

# Measures to extract — (column_name_in_output, measureid in PLACES)
MEASURES = [
    ("arthritis_pct",           "ARTHRITIS"),
    ("high_blood_pressure_pct", "BPHIGH"),
    ("cancer_pct",              "CANCER"),
    ("asthma_pct",              "CASTHMA"),
    ("coronary_heart_disease_pct", "CHD"),
    ("copd_pct",                "COPD"),
    ("depression_pct",          "DEPRESSION"),
    ("diabetes_pct",            "DIABETES"),
    ("high_cholesterol_pct",    "HIGHCHOL"),
    ("kidney_disease_pct",      "KIDNEY"),
    ("obesity_pct",             "OBESITY"),
    ("stroke_pct",              "STROKE"),
    ("teeth_lost_pct",          "TEETHLOST"),
    ("binge_drinking_pct",      "BINGE"),
    ("current_smoking_pct",     "CSMOKING"),
    ("physical_inactivity_pct", "LPA"),
    ("short_sleep_pct",         "SLEEP"),
    ("annual_checkup_pct",      "CHECKUP"),
    ("cholesterol_screen_pct",  "CHOLSCREEN"),
    ("colorectal_screen_pct",   "COLON_SCREEN"),
    ("mammography_pct",         "MAMMOUSE"),
    ("pap_test_pct",            "PAPTEST"),
    ("dental_visit_pct",        "DENTAL"),
    ("hearing_disability_pct",  "HEARING"),
    ("vision_disability_pct",   "VISION"),
    ("cognitive_disability_pct","COGNITION"),
    ("mobility_disability_pct", "MOBILITY"),
    ("selfcare_disability_pct", "SELFCARE"),
    ("no_health_insurance_pct", "ACCESS2"),
]

OUT_FILE = Path(__file__).parent.parent / "data" / "processed" / "cdc_places_nc_counties.csv"
LIMIT = 2000  # max rows per request; NC has 100 counties × ~30 measures = ~3000 rows


def fetch_all_nc_records() -> list[dict]:
    """Pull NC county PLACES records for the specific measure IDs we need."""
    measure_ids = [m for _, m in MEASURES]
    # Build an IN(...) filter — SODA supports this syntax
    ids_quoted = ",".join(f"'{m}'" for m in measure_ids)
    where_clause = f"stateabbr='NC' AND measureid in({ids_quoted})"

    records = []
    offset = 0
    while True:
        params = {
            "$where": where_clause,
            "$limit": LIMIT,
            "$offset": offset,
            "$select": "locationid,locationname,measureid,data_value",
            "$order": "locationid,measureid",
        }
        resp = requests.get(API_URL, params=params, timeout=120)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        records.extend(batch)
        offset += len(batch)
        print(f"  fetched {offset} records so far...")
        if len(batch) < LIMIT:
            break
    return records


def pivot_to_counties(records: list[dict]) -> pd.DataFrame:
    """Pivot long-format records to wide (one row per county)."""
    df = pd.DataFrame(records)
    df["data_value"] = pd.to_numeric(df["data_value"], errors="coerce")

    # Keep only measures we care about
    measure_ids = {m for _, m in MEASURES}
    df = df[df["measureid"].isin(measure_ids)]

    # Pivot: rows = county, cols = measureid
    wide = df.pivot_table(
        index=["locationid", "locationname"],
        columns="measureid",
        values="data_value",
        aggfunc="first",
    ).reset_index()

    wide.columns.name = None

    # Rename columns
    rename_map = {m: name for name, m in MEASURES}
    rename_map["locationid"] = "fips"
    rename_map["locationname"] = "county"
    wide = wide.rename(columns=rename_map)

    # Zero-pad FIPS to 5 chars
    wide["fips"] = wide["fips"].astype(str).str.zfill(5)

    # Keep only our desired output columns (some measures may be absent)
    out_cols = ["fips", "county"] + [name for name, _ in MEASURES if name in wide.columns]
    return wide[out_cols]


def main():
    print("Fetching CDC PLACES data for NC counties...")
    records = fetch_all_nc_records()
    print(f"Total records fetched: {len(records)}")

    df = pivot_to_counties(records)
    print(f"Pivoted to {len(df)} counties × {len(df.columns)} columns")

    df.to_csv(OUT_FILE, index=False)
    print(f"Saved → {OUT_FILE}")
    print("\nColumns:")
    for c in df.columns:
        print(f"  {c}")


if __name__ == "__main__":
    main()
