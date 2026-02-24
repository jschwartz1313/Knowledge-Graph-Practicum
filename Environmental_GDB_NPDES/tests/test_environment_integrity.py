
import pandas as pd

def test_columns_present():
    df = pd.read_csv('Environmental_GDB_NPDES/data/processed/county_environment_2024.csv', dtype={'fips':str})
    need = {'pm25_mean','ozone_8hr_avg','rsei_tox_air','impaired_stream_miles','npdes_permits_count','avg_temp_f','annual_precip_in'}
    assert need.issubset(df.columns)
