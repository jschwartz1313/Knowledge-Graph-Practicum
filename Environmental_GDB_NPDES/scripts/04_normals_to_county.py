
#!/usr/bin/env python3
import argparse
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import pandas as pd

"""
NCEI gridded normals (annual avg temperature & precipitation) → county zonal means.
"""

p = argparse.ArgumentParser()
p.add_argument('--counties', required=True)
p.add_argument('--temp', required=True)
p.add_argument('--prcp', required=True)
p.add_argument('--out', default='Environmental_GDB_NPDES/data/processed/_ncei_normals_by_county.csv')
args = p.parse_args()

Path('Environmental_GDB_NPDES/data/processed').mkdir(parents=True, exist_ok=True)

counties = gpd.read_file(args.counties)
# FIPS field detection
fips_field = next((c for c in counties.columns if c.upper() in {'FIPS','COUNTYFP','COUNTY_FIPS','GEOID','GEOID10'}), None)
if fips_field is None:
    raise SystemExit('County layer: missing FIPS/GEOID field.')
counties['fips'] = counties[fips_field].astype(str).str.zfill(5)

out = pd.DataFrame({'fips': counties['fips']})

with rasterio.open(args.temp) as src:
    c = counties.to_crs(src.crs)
    zs = zonal_stats(c, args.temp, stats=['mean'], nodata=src.nodata)
    out['avg_temp_f'] = [z['mean'] for z in zs]

with rasterio.open(args.prcp) as src:
    c = counties.to_crs(src.crs)
    zs = zonal_stats(c, args.prcp, stats=['mean'], nodata=src.nodata)
    out['annual_precip_in'] = [z['mean'] for z in zs]

out['year'] = 2020
out.to_csv(args.out, index=False)
print('Wrote', args.out)
