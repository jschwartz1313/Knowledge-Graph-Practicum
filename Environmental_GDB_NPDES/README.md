
# Environmental Module — North Carolina Exposome KG

## Raw inputs expected
Place these in `Environmental_GDB_NPDES/data/raw/`:

```
Environmental_GDB_NPDES/data/raw/
  ejscreen_blockgroups.csv          # EJScreen national block-group CSV (raw indicators)
  nconemap_counties.geojson         # NC OneMap county polygons with a FIPS/GEOID field
  ImpairedWaters.gdb/               # **FileGDB** (NC DEQ impaired waters, polyline)
  NPDES_Permits.gdb/                # **FileGDB** (NC DEQ NPDES permits, point)
  ncei_normals_temp.tif             # NCEI gridded normals: annual avg temperature (°F)
  ncei_normals_prcp.tif             # NCEI gridded normals: annual precipitation (in)
```

> A FileGDB is a **folder** with many files. Provide the folder path (e.g., `.../ImpairedWaters.gdb`).

## Install
```bash
pip install -r Environmental_GDB_NPDES/requirements.txt
```

## Run order
```bash
# 1) EJScreen: filter to NC (STATEFP=37) and aggregate block groups → county
python Environmental_GDB_NPDES/scripts/01_ejscreen_to_county.py   --ejscreen Environmental_GDB_NPDES/data/raw/ejscreen_blockgroups.csv

# 2) Impaired waters (GDB polylines) → miles per county
python Environmental_GDB_NPDES/scripts/02_impaired_streams_to_county.py   --impaired-gdb Environmental_GDB_NPDES/data/raw/ImpairedWaters.gdb   --counties    Environmental_GDB_NPDES/data/raw/nconemap_counties.geojson

# 3) NPDES (GDB points): filter **Active** → count per county
python Environmental_GDB_NPDES/scripts/03_npdes_active_to_county.py   --npdes-gdb Environmental_GDB_NPDES/data/raw/NPDES_Permits.gdb   --counties  Environmental_GDB_NPDES/data/raw/nconemap_counties.geojson

# 4) NCEI gridded normals → county zonal means
python Environmental_GDB_NPDES/scripts/04_normals_to_county.py   --counties Environmental_GDB_NPDES/data/raw/nconemap_counties.geojson   --temp     Environmental_GDB_NPDES/data/raw/ncei_normals_temp.tif   --prcp     Environmental_GDB_NPDES/data/raw/ncei_normals_prcp.tif

# 5) Merge + RDF
python Environmental_GDB_NPDES/scripts/90_build_environment_rdf.py
```

## Outputs
```
Environmental_GDB_NPDES/data/processed/
  county_environment_2024.csv
  county_environment_2024.ttl
```

### Notes
- **EJScreen**: extracts **raw** PM2.5, Ozone (8‑hr), and RSEI (no percentiles or EJ indexes). Aggregates from block‑group to county by mean.
- **Impaired Waters**: auto‑detects a polyline layer within the GDB (looks for names containing `impair`, `303`, `assess`). Intersects with counties in **EPSG:32119** and sums length in **miles**.
- **NPDES**: auto‑detects a point layer within the GDB (looks for names containing `npdes`, `permit`, `wastewater`). Normalizes a status field, filters to **ACTIVE**, then point‑in‑polygon counts per county.
- **Normals**: computes county zonal means from the gridded rasters.

## RDF provenance IRIs (emitted)
- `ex:dataset/EJScreen_v23`
- `ex:dataset/NCDEQ_ImpairedWaters`
- `ex:dataset/NCDEQ_NPDES_ActiveOnly`
- `ex:dataset/NOAA_NCEI_GriddedNormals_1991_2020`

