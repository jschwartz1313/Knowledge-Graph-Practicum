"""
Parse County Health Rankings 2025 - Complete data from both sheets
"""

import pandas as pd
import numpy as np

chr_file = 'county health rankings/2025 County Health Rankings North Carolina Data - v3.xlsx'

print("=" * 80)
print("County Health Rankings 2025 - Complete Data Parser")
print("=" * 80)

def load_sheet_data(sheet_name):
    """Load and parse a CHR data sheet"""
    df = pd.read_excel(chr_file, sheet_name=sheet_name, header=[0, 1])

    # Get county/FIPS columns
    fips_col = None
    county_col = None

    for col in df.columns:
        col_str = str(col).lower()
        if 'fips' in col_str and fips_col is None:
            fips_col = col
        if 'county' in col_str and county_col is None:
            county_col = col

    return df, fips_col, county_col

# Load both data sheets
print(f"\n📊 Loading 'Select Measure Data'...")
df_select, fips_col_1, county_col_1 = load_sheet_data('Select Measure Data')
print(f"  ✓ {len(df_select)} rows × {len(df_select.columns)} columns")

print(f"\n📊 Loading 'Additional Measure Data'...")
df_additional, fips_col_2, county_col_2 = load_sheet_data('Additional Measure Data')
print(f"  ✓ {len(df_additional)} rows × {len(df_additional.columns)} columns")

# Show what's in Additional sheet
print(f"\n📋 Measures in Additional sheet:")
additional_measures = set()
for col in df_additional.columns:
    if isinstance(col, tuple):
        measure = col[0]
        if not measure.startswith('Unnamed'):
            additional_measures.add(measure)

for i, measure in enumerate(sorted(additional_measures)[:30], 1):  # Show first 30
    print(f"  {i}. {measure}")

# Define all indicators we want with their sheet locations
indicators = [
    # From Select Measure Data
    ('select', 'Poor Mental Health Days', 'Average Number of Mentally Unhealthy Days', 'mental_health_days'),
    ('select', 'Poor Physical Health Days', 'Average Number of Physically Unhealthy Days', 'physical_health_days'),
    ('select', 'Uninsured', '% Uninsured', 'uninsured_pct'),
    ('select', 'Primary Care Physicians', 'Primary Care Physicians Ratio', 'primary_care_ratio'),
    ('select', 'Unemployment', '% Unemployed', 'unemployment_pct'),
    ('select', 'High School Completion', '% High School Completion', 'high_school_completion_pct'),
    ('select', 'Some College', '% Some College', 'some_college_pct'),
    ('select', 'Children in Poverty', '% Children in Poverty', 'child_poverty_pct'),
    ('select', 'Air Pollution: Particulate Matter', 'Average Daily PM2.5', 'pm25'),

    # From Additional Measure Data
    ('additional', 'Adult Obesity', '% Adults with Obesity', 'obesity_pct'),
    ('additional', 'Adult Smoking', '% Smokers', 'smoking_pct'),
    ('additional', 'Diabetes Prevalence', '% Adults with Diabetes', 'diabetes_pct'),
    ('additional', 'Physical Inactivity', '% Physically Inactive', 'physical_inactivity_pct'),
    ('additional', 'Excessive Drinking', '% Excessive Drinking', 'excessive_drinking_pct'),
]

# Extract data
print(f"\n" + "=" * 80)
print("Extracting county health data...")
print("=" * 80)

health_data = []

# Iterate through Select sheet (use it as base)
for idx, row in df_select.iterrows():
    county_name = row[county_col_1]
    fips = row[fips_col_1]

    # Skip state-level or invalid rows
    if pd.isna(county_name) or str(county_name).strip() == 'North Carolina':
        continue

    county_data = {
        'county': str(county_name).strip(),
        'fips': str(fips).strip() if pd.notna(fips) else None,
    }

    # Extract from Select sheet
    for sheet, measure_name, sub_col, our_name in indicators:
        if sheet == 'select':
            for col in df_select.columns:
                if isinstance(col, tuple) and len(col) == 2:
                    if measure_name in col[0] and sub_col in col[1]:
                        try:
                            value = row[col]
                            if pd.notna(value):
                                county_data[our_name] = float(value)
                        except:
                            pass
                        break

    # Extract from Additional sheet (match by FIPS)
    if county_data['fips']:
        add_rows = df_additional[df_additional[fips_col_2] == fips]
        if len(add_rows) > 0:
            add_row = add_rows.iloc[0]
            for sheet, measure_name, sub_col, our_name in indicators:
                if sheet == 'additional':
                    for col in df_additional.columns:
                        if isinstance(col, tuple) and len(col) == 2:
                            if measure_name in col[0] and sub_col in col[1]:
                                try:
                                    value = add_row[col]
                                    if pd.notna(value):
                                        county_data[our_name] = float(value)
                                except:
                                    pass
                                break

    health_data.append(county_data)

df_health = pd.DataFrame(health_data)

print(f"\n✓ Extracted data for {len(df_health)} counties")

print(f"\n📊 Data completeness by indicator:")
for col in sorted(df_health.columns):
    if col not in ['county', 'fips']:
        non_null = df_health[col].notna().sum()
        pct = non_null / len(df_health) * 100 if len(df_health) > 0 else 0
        print(f"  {col:30s}: {non_null:3d}/{len(df_health)} ({pct:5.1f}%)")

print(f"\n📋 Sample data:")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
# Show only columns that exist
sample_cols = ['county', 'obesity_pct', 'diabetes_pct', 'unemployment_pct', 'uninsured_pct']
sample_cols = [c for c in sample_cols if c in df_health.columns]
print(df_health[sample_cols].head(15))

# Save
output_file = 'chr_2025_nc_complete.csv'
df_health.to_csv(output_file, index=False)
print(f"\n💾 Saved complete data to: {output_file}")

print("\n" + "=" * 80)
print("✓ County Health Rankings data successfully parsed!")
print("=" * 80)
