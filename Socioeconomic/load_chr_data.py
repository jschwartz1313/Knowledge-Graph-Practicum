"""
Script to explore County Health Rankings 2025 data structure
"""

import pandas as pd

# Load the NC-specific file
chr_file = 'county health rankings/2025 County Health Rankings North Carolina Data - v3.xlsx'

print("=" * 80)
print("County Health Rankings 2025 - North Carolina Data")
print("=" * 80)

# Check available sheets
xl_file = pd.ExcelFile(chr_file)
print(f"\n📋 Available sheets:")
for i, sheet in enumerate(xl_file.sheet_names, 1):
    print(f"  {i}. {sheet}")

# Load the main data sheet (usually "Ranked Measure Data" or similar)
print(f"\n📊 Loading main data sheet...")

# Try data sheets (skip intro)
possible_sheets = ['Select Measure Data', 'Additional Measure Data', 'Ranked Measure Data', 'Ranked Measures', 'Data']

df = None
for sheet_name in possible_sheets:
    if sheet_name in xl_file.sheet_names:
        print(f"  Found sheet: {sheet_name}")
        df = pd.read_excel(chr_file, sheet_name=sheet_name)
        break

if df is None:
    # Use second sheet (skip introduction)
    sheet_name = xl_file.sheet_names[1] if len(xl_file.sheet_names) > 1 else xl_file.sheet_names[0]
    print(f"  Using sheet: {sheet_name}")
    df = pd.read_excel(chr_file, sheet_name=sheet_name)

print(f"\n✓ Loaded {len(df)} rows × {len(df.columns)} columns")

print(f"\n📋 Column names:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print(f"\n🔍 First few rows:")
print(df.head(3))

print(f"\n📍 Unique counties: {df['County'].nunique() if 'County' in df.columns else 'N/A'}")

# Look for health indicators
print(f"\n🏥 Looking for health indicators...")
health_keywords = ['obesity', 'diabetes', 'smoking', 'physical', 'mental', 'insurance']

health_cols = []
for col in df.columns:
    col_lower = str(col).lower()
    if any(keyword in col_lower for keyword in health_keywords):
        health_cols.append(col)

print(f"  Found {len(health_cols)} health-related columns:")
for col in health_cols[:20]:  # Show first 20
    print(f"    - {col}")

# Show sample values for key indicators
if health_cols:
    print(f"\n📊 Sample data:")
    sample_cols = ['County'] if 'County' in df.columns else []
    sample_cols.extend(health_cols[:5])
    print(df[sample_cols].head(10))

print("\n" + "=" * 80)
