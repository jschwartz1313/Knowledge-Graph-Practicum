"""
parse_chr_expanded.py
Extracts a comprehensive set of health outcome and social determinant columns
from the CHR 2025 North Carolina Excel file.

Outputs:
    chr_2025_nc_expanded.csv  — one row per county (100 NC counties)

Column sources:
    Select Measure Data sheet    — YPLL, low birth weight, poor/fair health,
                                   flu vaccinations, access to exercise,
                                   food environment index, primary care rate,
                                   mental health provider rate, preventable
                                   hospitalizations, mammography screening,
                                   severe housing problems, income ratio,
                                   injury death rate
    Additional Measure Data sheet — life expectancy, premature age-adjusted
                                   mortality, child mortality, infant mortality,
                                   frequent physical/mental distress, diabetes,
                                   HIV, obesity, suicides, loneliness, food
                                   insecurity, insufficient sleep, teen births,
                                   STI (chlamydia) rate, excessive drinking,
                                   drug overdose mortality, adult smoking,
                                   physical inactivity, uninsured adults/
                                   children, homicide rate, motor vehicle
                                   mortality, firearm fatality rate
"""

import pandas as pd
from pathlib import Path

CHR_FILE = Path(__file__).parent.parent.parent / "Socioeconomic" / \
    "county health rankings" / \
    "2025 County Health Rankings North Carolina Data - v3.xlsx"
OUT_FILE = Path(__file__).parent.parent / "data" / "processed" / "chr_2025_nc_expanded.csv"


# ---------------------------------------------------------------------------
# Column selections — (output_name, sheet_col_index)
# Row 0 = measure group header, Row 1 = column label, Row 2+ = data (row 2 = NC state)
# ---------------------------------------------------------------------------

SELECT_COLS = {
    # identifiers
    "fips":                         0,
    "county":                       2,
    # health outcomes
    "ypll_rate":                     5,   # Years of Potential Life Lost per 100k
    "low_birth_weight_pct":         42,   # % Low Birth Weight
    "poor_or_fair_health_pct":      71,   # % Fair or Poor Health
    "injury_death_rate":            195,  # Injury Deaths per 100k
    # health behaviours / access
    "flu_vaccinations_pct":         75,   # % Vaccinated (flu)
    "access_exercise_pct":          82,   # % With Access to Exercise Opportunities
    "food_environment_index":       84,   # Food Environment Index (0–10, higher = better)
    "primary_care_rate":            87,   # Primary Care Physicians per 100k
    "mental_health_provider_rate":  91,   # Mental Health Providers per 100k
    "preventable_hosp_rate":        98,   # Preventable Hospitalizations per 100k Medicare
    "mammography_pct":              105,  # % with Annual Mammogram
    # social determinants
    "severe_housing_pct":           117,  # % Severe Housing Problems
    "income_ratio":                 183,  # 80th/20th Percentile Income Ratio
}

ADDITIONAL_COLS = {
    # identifiers (used for merge — not re-emitted)
    "_fips":                        0,
    # health outcomes
    "life_expectancy":              3,    # Average life expectancy (years)
    "premature_age_adj_mortality":  28,   # Premature age-adjusted death rate per 100k
    "child_mortality_rate":         53,   # Child mortality rate per 100k
    "infant_mortality_rate":        78,   # Infant mortality rate per 1,000 live births
    "suicide_rate":                 117,  # Suicide rate (age-adjusted) per 100k
    "homicide_rate":                287,  # Homicide rate per 100k
    "motor_vehicle_mortality_rate": 312,  # Motor vehicle crash deaths per 100k
    "firearm_fatality_rate":        337,  # Firearm fatalities per 100k
    "drug_overdose_mortality_rate": 187,  # Drug overdose deaths per 100k
    # health behaviours / prevalence
    "frequent_physical_distress_pct": 102,  # % Frequent Physical Distress
    "diabetes_prevalence_pct":      105,  # % Adults with Diabetes
    "hiv_prevalence_rate":          109,  # HIV Prevalence per 100k
    "obesity_prevalence_pct":       110,  # % Adults with Obesity
    "frequent_mental_distress_pct": 113,  # % Frequent Mental Distress
    "adult_smoking_pct":            211,  # % Adults Currently Smoking
    "physical_inactivity_pct":      214,  # % Physically Inactive
    "excessive_drinking_pct":       178,  # % Excessive Drinking
    "insufficient_sleep_pct":       149,  # % Insufficient Sleep
    "teen_birth_rate":              152,  # Teen Birth Rate per 1,000 females 15-19
    "chlamydia_rate":               177,  # Chlamydia cases per 100k
    "loneliness_pct":               142,  # % Feeling Lonely
    # access / social determinants
    "food_insecurity_pct":          148,  # % Food Insecure
    "uninsured_adults_pct":         218,  # % Uninsured Adults
    "uninsured_children_pct":       222,  # % Uninsured Children
}


def _read_sheet(sheet_name: str, col_map: dict) -> pd.DataFrame:
    """Read selected columns from a CHR sheet (skipping state-level row 2)."""
    max_col = max(col_map.values())
    df_raw = pd.read_excel(
        CHR_FILE,
        sheet_name=sheet_name,
        header=None,
        usecols=range(max_col + 1),
    )
    # Row 0 = group headers, Row 1 = column names, Row 2 = NC state total, Row 3+ = counties
    data = df_raw.iloc[3:].reset_index(drop=True)  # skip state row

    result = pd.DataFrame()
    for out_name, idx in col_map.items():
        result[out_name] = data.iloc[:, idx].values

    return result


def main():
    print(f"Reading: {CHR_FILE}")

    sel = _read_sheet("Select Measure Data", SELECT_COLS)
    add = _read_sheet("Additional Measure Data", ADDITIONAL_COLS)

    # Normalise FIPS to zero-padded 5-char string
    for df in (sel, add):
        fips_col = "fips" if "fips" in df.columns else "_fips"
        df[fips_col] = (
            pd.to_numeric(df[fips_col], errors="coerce")
            .fillna(0)
            .astype(int)
            .astype(str)
            .str.zfill(5)
        )

    add = add.rename(columns={"_fips": "fips"})

    # Merge on FIPS
    merged = sel.merge(add, on="fips", how="inner")

    # Drop rows without a valid county name (state-level or blank rows)
    merged = merged[merged["county"].notna() & (merged["county"].astype(str).str.strip() != "")]

    # Numeric coercion for all non-identifier columns
    id_cols = {"fips", "county"}
    for col in merged.columns:
        if col not in id_cols:
            merged[col] = pd.to_numeric(merged[col], errors="coerce")

    merged.to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(merged)} rows × {len(merged.columns)} columns → {OUT_FILE}")
    print("\nColumns:")
    for c in merged.columns:
        print(f"  {c}")


if __name__ == "__main__":
    main()
