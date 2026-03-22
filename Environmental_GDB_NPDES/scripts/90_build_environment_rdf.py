
#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from rdflib import Graph, Namespace, Literal, RDF, RDFS, XSD


"""
Merge all environmental indicators and emit RDF (SOSA + PROV-O).
"""

PROC = Path('Environmental_GDB_NPDES/data/processed'); PROC.mkdir(parents=True, exist_ok=True)

ejs = pd.read_csv(PROC / 'ejscreen_county.csv', dtype={'fips':str})
imp = pd.read_csv(PROC / 'impaired_streams_by_county.csv', dtype={'fips':str})
npd = pd.read_csv(PROC / 'npdes_active_by_county.csv', dtype={'fips':str})
nrm = pd.read_csv(PROC / 'ncei_normals_by_county.csv', dtype={'fips':str})



print("LEFT dtypes:\n", imp.dtypes)      # replace left_df with your actual left DataFrame variable
print("RIGHT dtypes:\n", npd.dtypes)    # replace right_df with your actual right DataFrame variable
print("SAMPLE FIPS LEFT/RIGHT:", imp["fips"].head(3).tolist(), npd["fips"].head(3).tolist())


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
BASE  = Namespace('http://example.org/nc-exposome/')
SOSA  = Namespace('http://www.w3.org/ns/sosa#')
PROV  = Namespace('http://www.w3.org/ns/prov#')
QB    = Namespace("http://purl.org/linked-data/cube#")
SCHEMA = Namespace("http://schema.org/")
ECTO  = Namespace("http://purl.obolibrary.org/obo/ECTO_")
EXO   = Namespace("http://purl.obolibrary.org/obo/ExO_")
ENVO  = Namespace("http://purl.obolibrary.org/obo/ENVO_")

g = Graph()
g.bind('ex', BASE); g.bind('sosa', SOSA); g.bind('prov', PROV)
g.bind('qb', QB);  g.bind('schema', SCHEMA)
g.bind('ecto', ECTO); g.bind('exo', EXO); g.bind('envo', ENVO)

IND = {
  'pm25_mean':            BASE['indicator/pm25_mean'],
  'ozone_8hr_avg':        BASE['indicator/ozone_8hr_avg'],
  'rsei_tox_air':         BASE['indicator/rsei_tox_air'],
  'impaired_stream_miles':BASE['indicator/impaired_stream_miles'],
  'npdes_permits_count':  BASE['indicator/npdes_permits_count'],
  'avg_temp_f':           BASE['indicator/avg_temp_f'],
  'annual_precip_in':     BASE['indicator/annual_precip_in'],
}

# Ontology annotations per indicator:
#   (label, unit, ontology_class, exposure_class, environment_class)
#   ontology_class  → rdfs:subClassOf  (ECTO/ENVO condition/measure term)
#   exposure_class  → ex:exposureClass (ExO exposure category)
#   environment_class → ex:environmentClass (ENVO environmental context)
IND_META = {
  'pm25_mean': (
    "PM2.5 Mean Concentration", "µg/m³",
    ECTO["0000460"],   # particulate matter exposure
    EXO["0000113"],    # air pollution exposure
    ENVO["00002005"],  # air
  ),
  'ozone_8hr_avg': (
    "Ozone 8-Hour Average", "ppb",
    ECTO["0000461"],   # ozone exposure
    EXO["0000113"],
    ENVO["00002005"],
  ),
  'rsei_tox_air': (
    "RSEI Toxic Air Index", "score",
    ECTO["0001235"],   # toxic chemical air exposure
    EXO["0000113"],
    ENVO["00002005"],
  ),
  'impaired_stream_miles': (
    "Impaired Stream Miles", "miles",
    ECTO["0001000"],   # water pollution exposure
    EXO["0000113"],
    ENVO["00000891"],  # water body
  ),
  'npdes_permits_count': (
    "Active NPDES Permit Count", "count",
    ECTO["0001000"],
    EXO["0000113"],
    ENVO["00000891"],
  ),
  'avg_temp_f': (
    "Average Annual Temperature", "°F",
    ENVO["01001203"],  # mean annual air temperature
    None,
    ENVO["01000739"],  # climate
  ),
  'annual_precip_in': (
    "Annual Precipitation", "inches",
    ENVO["01001204"],  # annual precipitation
    None,
    ENVO["01000739"],
  ),
}

# Emit indicator declarations with ontology annotations
for col, ind_uri in IND.items():
  label, unit, ont_class, exp_class, env_class = IND_META[col]
  g.add((ind_uri, RDF.type,        QB.MeasureProperty))
  g.add((ind_uri, RDFS.label,      Literal(label)))
  g.add((ind_uri, SCHEMA.unitText, Literal(unit)))
  if ont_class:
    g.add((ind_uri, RDFS.subClassOf,         ont_class))
  if exp_class:
    g.add((ind_uri, BASE['exposureClass'],   exp_class))
  if env_class:
    g.add((ind_uri, BASE['environmentClass'],env_class))
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


# PATCH to make it compatible with SPARQL_EXAMPLES in 91_sparql_examples.py; add schema.org properties and QB dataset/indicator links

# ALSO add the project's QB + schema.org model so SPARQL_EXAMPLES work
g.add((obs, RDF.type, QB.Observation))                     # qb:Observation
g.add((obs, QB.dataSet, BASE['nc_exposome_dataset']))      # link to dataset
g.add((obs, SCHEMA.location, county))                      # schema:location county
g.add((obs, BASE['measuredIndicator'], ind))               # ex:measuredIndicator indicator

# write value both ways (schema:value is what examples query)
# 'val' is your numeric; ensure it's a float literal
g.add((obs, SCHEMA.value, Literal(float(val))))            # schema:value

# optional: unitText (recommended for impaired miles, temp, precip)
unit_map = {
  'impaired_stream_miles': 'miles',
  'avg_temp_f': 'degree Fahrenheit',
  'annual_precip_in': 'inch',
}
u = unit_map.get(k)
if u:
    g.add((obs, SCHEMA.unitText, Literal(u)))

# project time representation
year = int(r['year'])
g.add((obs, SCHEMA.temporal, Literal(str(year), datatype=XSD.gYear)))  # schema:temporal gYear