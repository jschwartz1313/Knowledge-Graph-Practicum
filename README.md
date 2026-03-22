# NC Exposome Knowledge Graph — Practicum Project

**Course:** INLS/COMP Practicum
**Supervisor:** Dr. Arcot Rajasekar, RENCI / UNC Chapel Hill
**Goal:** Build a North Carolina county-level exposome knowledge graph and contribute it to [ROBOKOP](https://robokop.renci.org/) at RENCI.

---

## What This Project Is

An "exposome" is the totality of environmental exposures a person experiences across their lifetime. This project operationalizes that concept at the North Carolina county level by integrating data from four domains:

| Domain | Sources | Coverage |
|--------|---------|----------|
| **Environmental** | EJScreen v23, NC DEQ Impaired Waters, NCDEQ NPDES, NOAA NCEI Normals 1991–2020 | Air quality, water quality, climate |
| **Health Outcomes** | CDC PLACES 2024, County Health Rankings 2025 | 28 PLACES indicators + 37 CHR indicators |
| **Socioeconomic** | CHR 2025 (demographics, income, education, housing) | ~15 SE indicators |
| **County Metadata** | FIPS codes, NC county names | All 100 NC counties |

All data is emitted as **RDF (Turtle)** triples following:
- **SOSA/SSN** — for observations (sensor/measurement semantics)
- **PROV-O** — for provenance (dataset lineage)
- **RDF Data Cube (QB)** — for statistical observations
- **schema.org** — for location, value, and temporal metadata
- **NCIT, ECTO, ExO, ENVO** — for ontology-grounded indicator semantics

---

## Repository Structure

```
Knowledge-Graph-Practicum/
├── Environmental_GDB_NPDES/
│   ├── scripts/
│   │   ├── 01_ejscreen_to_county.py         # EJScreen CSV → county aggregates
│   │   ├── 02_impaired_streams_to_county.py  # NC DEQ impaired waters → county totals
│   │   ├── 03_npdes_active_to_county.py      # NPDES permit counts by county
│   │   ├── 04_normals_to_county_cog.py       # NOAA climate normals → county averages
│   │   └── 90_build_environment_rdf.py       # Merges all env data → TTL triples
│   ├── data/processed/
│   │   ├── county_environment_2024.csv       # Merged flat file
│   │   └── county_environment_2024.ttl       # RDF output (~4,900 lines)
│   └── README.md
│
├── Health/
│   ├── scripts/
│   │   ├── fetch_cdc_places.py               # Fetch CDC PLACES via Socrata API
│   │   ├── parse_chr_expanded.py             # Parse CHR 2025 Excel → flat CSV
│   │   ├── build_cdc_places_rdf.py           # CDC PLACES → TTL triples
│   │   └── build_chr_health_rdf.py           # CHR 2025 → TTL triples
│   └── data/processed/
│       ├── cdc_places_nc_counties.csv        # CDC PLACES flat file (28 indicators × 100 counties)
│       ├── cdc_places_2024.ttl               # RDF output (~37,984 lines)
│       ├── chr_2025_nc_expanded.csv          # CHR flat file (37 indicators × 100 counties)
│       └── chr_health_2025.ttl               # RDF output (~50,541 lines)
│
├── Socioeconomic/
│   ├── enhance_kg_with_ontologies.py         # Builds SE RDF with ontology annotations
│   ├── nc_exposome_kg_ontology.ttl           # RDF output (~17,276 lines)
│   ├── nc_exposome_kg.nt                     # N-Triples format
│   └── ONTOLOGY_ENHANCEMENT.md              # Ontology mapping documentation
│
├── tools/
│   └── normalize_nc_fips.py                 # FIPS normalization utility
│
└── README.md                                # This file
```

---

## Current State (March 2026)

### Triple Counts

| Module | Output File | Lines | Est. Triples |
|--------|------------|-------|-------------|
| Environmental | `county_environment_2024.ttl` | ~4,900 | ~2,000 |
| Health / CDC PLACES | `cdc_places_2024.ttl` | ~37,984 | ~35,000 |
| Health / CHR 2025 | `chr_health_2025.ttl` | ~50,541 | ~46,000 |
| Socioeconomic | `nc_exposome_kg_ontology.ttl` | ~17,276 | ~15,000 |
| **Total** | | **~111k lines** | **~98,000 triples** |

### Ontology Coverage

Every indicator across all four modules is annotated with:

| Predicate | Purpose | Ontologies Used |
|-----------|---------|----------------|
| `rdfs:subClassOf` | Links the indicator to its condition/measure class | NCIT, ECTO, ENVO |
| `ex:exposureClass` | Links to the relevant ExO exposure category | ExO (Exposure Ontology) |
| `ex:environmentClass` | Links to the environmental context | ENVO |
| `schema:unitText` | Physical unit of measurement | — |
| `prov:wasDerivedFrom` | Source dataset provenance node | — |

**Key ontologies:**
- **NCIT** (`http://purl.obolibrary.org/obo/NCIT_`) — disease/health outcome terms
- **ECTO** (`http://purl.obolibrary.org/obo/ECTO_`) — environmental condition/exposure terms
- **ExO** (`http://purl.obolibrary.org/obo/ExO_`) — exposure categories
- **ENVO** (`http://purl.obolibrary.org/obo/ENVO_`) — environment context terms

### Triple Pattern

Each data point becomes a `sosa:Observation` structured as:

```turtle
ex:obs/pm25_mean/37063/2024
    a sosa:Observation, qb:Observation ;
    sosa:hasFeatureOfInterest  ex:county/37063 ;
    sosa:observedProperty      ex:indicator/pm25_mean ;
    sosa:hasSimpleResult       9.32 ;
    sosa:resultTime            "2024-12-31"^^xsd:date ;
    schema:location            ex:county/37063 ;
    schema:value               9.32 ;
    schema:temporal            "2024"^^xsd:gYear ;
    prov:wasDerivedFrom        ex:dataset/EJScreen_v23 ;
    qb:dataSet                 ex:nc_exposome_dataset .
```

---

## What Remains

### 1. ROBOKOP Submission (Primary Goal)

ROBOKOP ([robokop.renci.org](https://robokop.renci.org/)) is RENCI's flagship biomedical knowledge graph reasoner. Contributing our data to the underlying knowledge graph is the primary deliverable of this practicum.

**What we know:**
- ROBOKOP is built on top of KGX/Biolink Model — a formal schema for biomedical knowledge graphs
- Formal KGX submission requires nodes to use Biolink Model types (e.g., `biolink:GeographicLocation`, `biolink:Disease`) and CURIE-format IDs from standard databases (UMLS, MONDO, HP, etc.)
- **However**, RENCI may also have a public or community submission pathway with lower barriers than the core KGX pipeline

**Next steps for submission:**
- [ ] Contact Dr. Rajasekar / RENCI team to confirm submission format requirements
- [ ] Investigate whether ROBOKOP accepts SOSA/PROV-O format directly, or requires Biolink conversion
- [ ] If Biolink is required: write a conversion script that maps our SOSA observations to Biolink `Association` edges with CURIE identifiers
- [ ] If a simpler pathway exists: prepare a submission package (TTL files + provenance metadata)

**Biolink conversion outline (if needed):**
- County nodes → `biolink:GeographicLocation` with `id: FIPS:37063`
- Indicator nodes → `biolink:NamedThing` or domain-specific Biolink class
- Observation edges → `biolink:Association` with `subject`, `predicate`, `object`, `publications` (provenance)
- Map existing NCIT/ECTO/ExO/ENVO IDs to Biolink-compatible `category` and `relation` fields

### 2. Unified Graph / SPARQL Endpoint

Currently the four modules produce separate TTL files. To make the KG queryable:
- [ ] Merge all TTL files into a single unified graph file (or a named-graph collection)
- [ ] Load into a triplestore (Apache Jena Fuseki, Oxigraph, or similar)
- [ ] Expose a public SPARQL endpoint
- [ ] Validate cross-domain queries (e.g., "counties with high PM2.5 and high asthma rates")

A draft SPARQL examples file exists at `Socioeconomic/SPARQL_EXAMPLES.md`.

### 3. County Identity Nodes

Currently county URIs (`ex:county/37063`) are bare nodes — they have no labels, names, or geographic metadata attached. Adding:
```turtle
ex:county/37063
    a schema:AdministrativeArea ;
    schema:name "Durham County" ;
    schema:identifier "37063" ;
    schema:containedInPlace ex:state/NC .
```
would significantly improve graph navigability and support more expressive SPARQL queries.

### 4. Validation and Quality Checks

- [ ] Verify all 100 NC counties are present across all modules (some edge cases exist with FIPS normalization)
- [ ] Check for null/missing values in critical columns
- [ ] Run SHACL or ShEx validation against the SOSA observation shape
- [ ] Confirm ontology term IDs are resolvable (some ECTO/ExO IDs may need verification)

### 5. Documentation

- [ ] Module-level READMEs for Health/ (currently missing)
- [ ] Data dictionary: one row per indicator, with definition, unit, source, and ontology term
- [ ] Provenance metadata: version and access date for each source dataset

---

## Running the Pipelines

### Dependencies

```bash
pip install pandas rdflib openpyxl requests
```

### Environmental Module

```bash
# Run preprocessing scripts 01–04, then:
python Environmental_GDB_NPDES/scripts/90_build_environment_rdf.py
# Output: Environmental_GDB_NPDES/data/processed/county_environment_2024.ttl
```

### Health Module

```bash
# Fetch CDC PLACES data (requires internet):
python Health/scripts/fetch_cdc_places.py

# Parse CHR 2025 Excel (file must be present in Socioeconomic/county health rankings/):
python Health/scripts/parse_chr_expanded.py

# Build RDF:
python Health/scripts/build_cdc_places_rdf.py
python Health/scripts/build_chr_health_rdf.py
```

### Socioeconomic Module

```bash
python Socioeconomic/enhance_kg_with_ontologies.py
# Output: Socioeconomic/nc_exposome_kg_ontology.ttl
```

---

## Data Sources

| Source | URL | Notes |
|--------|-----|-------|
| EJScreen v23 | [epa.gov/ejscreen](https://www.epa.gov/ejscreen) | Air quality, RSEI toxic index |
| NC DEQ Impaired Waters | [deq.nc.gov](https://deq.nc.gov) | 303(d) listed impaired streams |
| NCDEQ NPDES | [deq.nc.gov](https://deq.nc.gov) | Active discharge permits |
| NOAA NCEI Normals 1991–2020 | [ncei.noaa.gov](https://www.ncei.noaa.gov) | Gridded temperature & precipitation |
| CDC PLACES 2024 | [data.cdc.gov/resource/swc5-untb.json](https://data.cdc.gov/resource/swc5-untb.json) | 28 county-level health indicators |
| County Health Rankings 2025 | [countyhealthrankings.org](https://www.countyhealthrankings.org) | 37 county-level health/social indicators |

---

## Contact

- **PI / Supervisor:** Dr. Arcot Rajasekar — RENCI, UNC Chapel Hill
- **Knowledge Graph Platform:** [ROBOKOP](https://robokop.renci.org/)
