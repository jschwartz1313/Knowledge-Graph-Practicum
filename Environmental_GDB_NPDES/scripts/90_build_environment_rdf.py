
#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from rdflib import Graph, Namespace, Literal, RDF, XSD

"""
Merge all environmental indicators and emit RDF (SOSA + PROV-O).
"""

PROC = Path('Environmental_GDB_NPDES/data/processed'); PROC.mkdir(parents=True, exist_ok=True)

ejs = pd.read_csv(PROC / '_ejscreen_county.csv', dtype={'county_fips':str}).rename(columns={'county_fips':'fips'})
imp = pd.read_csv(PROC / '_impaired_streams_by_county.csv', dtype={'fips':str})
npd = pd.read_csv(PROC / '_npdes_active_by_county.csv', dtype={'fips':str})
nrm = pd.read_csv(PROC / '_ncei_normals_by_county.csv', dtype={'fips':str})

df = ejs.merge(imp, on='fips', how='left').merge(npd, on='fips', how='left').merge(nrm, on='fips', how='left')

df['county'] = None
# Use EJScreen year as label
if 'year' in df.columns:
    df['year'] = 2024
else:
    df['year'] = 2024

cols = ['fips','county','year','pm25_mean','ozone_8hr_avg','rsei_tox_air',
        'impaired_stream_miles','npdes_permits_count','avg_temp_f','annual_precip_in']
out = df[cols]
out.to_csv(PROC / 'county_environment_2024.csv', index=False)

# RDF
BASE = Namespace('http://example.org/nc-exposome/')
SOSA = Namespace('http://www.w3.org/ns/sosa#')
PROV = Namespace('http://www.w3.org/ns/prov#')

g = Graph(); g.bind('ex', BASE); g.bind('sosa', SOSA); g.bind('prov', PROV)

IND = {
  'pm25_mean': BASE['indicator/pm25_mean'],
  'ozone_8hr_avg': BASE['indicator/ozone_8hr_avg'],
  'rsei_tox_air': BASE['indicator/rsei_tox_air'],
  'impaired_stream_miles': BASE['indicator/impaired_stream_miles'],
  'npdes_permits_count': BASE['indicator/npdes_permits_count'],
  'avg_temp_f': BASE['indicator/avg_temp_f'],
  'annual_precip_in': BASE['indicator/annual_precip_in']
}
SRC = {
  'pm25_mean': BASE['dataset/EJScreen_v23'],
  'ozone_8hr_avg': BASE['dataset/EJScreen_v23'],
  'rsei_tox_air': BASE['dataset/EJScreen_v23'],
  'impaired_stream_miles': BASE['dataset/NCDEQ_ImpairedWaters'],
  'npdes_permits_count': BASE['dataset/NCDEQ_NPDES_ActiveOnly'],
  'avg_temp_f': BASE['dataset/NOAA_NCEI_GriddedNormals_1991_2020'],
  'annual_precip_in': BASE['dataset/NOAA_NCEI_GriddedNormals_1991_2020']
}

for _, r in out.iterrows():
    county = BASE[f"county/{r['fips']}"]
    for k, ind in IND.items():
        val = r.get(k)
        if pd.notna(val):
            obs = BASE[f"obs/{k}/{r['fips']}/{int(r['year'])}"]
            g.add((obs, RDF.type, SOSA.Observation))
            g.add((obs, SOSA.hasFeatureOfInterest, county))
            g.add((obs, SOSA.observedProperty, ind))
            g.add((obs, SOSA.resultTime, Literal(f"{int(r['year'])}-12-31", datatype=XSD.date)))
            try:
                g.add((obs, SOSA.hasSimpleResult, Literal(float(val))))
            except Exception:
                pass
            g.add((obs, PROV.wasDerivedFrom, SRC[k]))

g.serialize((PROC / 'county_environment_2024.ttl').as_posix(), format='turtle')
print('Wrote', (PROC / 'county_environment_2024.ttl').as_posix())
