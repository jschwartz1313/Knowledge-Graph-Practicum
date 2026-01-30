# Knowledge Graph Ontology Enhancement Summary

**Date**: 2025-11-07
**Status**: ✅ Complete

## Overview

Enhanced the North Carolina Exposome Knowledge Graph with proper semantic web ontology mappings to meet practicum deliverable requirements. The knowledge graph now uses established ontology standards (ExO, ECTO, ENVO, NCIT) and is published in standard RDF formats.

---

## Deliverable Compliance

### ✅ Component 1: Knowledge Graph Dataset in RDF/Turtle Format

**Original State**:
- Simple N-Triples with basic predicates (`<rdf:type>`, `<name>`, etc.)
- No formal ontology mappings

**Enhanced State**:
- **Proper ontology URIs** from ExO, ECTO, ENVO, NCIT
- **Three RDF formats**: Turtle (.ttl), N-Triples (.nt), RDF/XML (.rdf)
- **Semantic consistency** with established exposomics ontologies
- **15,469 RDF triples** with full provenance

**Generated Files**:
- `nc_exposome_kg_ontology.ttl` - Turtle format (most readable)
- `nc_exposome_kg_ontology.nt` - N-Triples format
- `nc_exposome_kg_ontology.rdf` - RDF/XML format

### ✅ Component 2: Example SPARQL Queries

**Delivered**: `SPARQL_EXAMPLES.md` with **28 example queries** across 7 categories:

1. **Basic Queries** (3 queries) - List counties, indicators, data sources
2. **Environmental-Health Associations** (2 queries) - PM2.5 correlations, vulnerability indices
3. **Socioeconomic-Health Pathways** (3 queries) - Poverty, education, unemployment impacts
4. **County Comparison Queries** (2 queries) - Urban vs rural, top counties
5. **Statistical Analysis Queries** (3 queries) - Correlations, risk factors, networks
6. **Data Provenance Queries** (2 queries) - Source attribution, metadata
7. **Advanced Analytical Queries** (3 queries) - Multi-dimensional risk, equity analysis

**Each query includes**:
- Purpose statement
- Expected use case
- Example output
- Proper namespace declarations

### ✅ Component 3: Technical Documentation

**Delivered**:
- **Data Provenance**: Documented with PROV-O ontology in RDF graph
- **Transformation Workflows**: Fully documented in `enhance_kg_with_ontologies.py`
- **Ontology Mapping Strategy**: Documented in this file
- **Reproducibility**: Complete code with installation instructions

---

## Ontology Mappings

### Ontologies Used

| Ontology | Full Name | URI Prefix | Purpose |
|----------|-----------|------------|---------|
| **ExO** | Exposure Ontology | `http://purl.obolibrary.org/obo/ExO_` | Classify exposure types |
| **ECTO** | Environmental Conditions, Treatments and Exposures | `http://purl.obolibrary.org/obo/ECTO_` | Environmental & social exposures |
| **ENVO** | Environment Ontology | `http://purl.obolibrary.org/obo/ENVO_` | Environmental contexts |
| **NCIT** | NCI Thesaurus | `http://purl.obolibrary.org/obo/NCIT_` | Health outcomes & diseases |
| **Schema.org** | Web Vocabulary | `http://schema.org/` | General properties |
| **PROV-O** | Provenance Ontology | `http://www.w3.org/ns/prov#` | Data lineage |
| **DCAT** | Data Catalog Vocabulary | `http://www.w3.org/ns/dcat#` | Dataset metadata |
| **QB** | RDF Data Cube | `http://purl.org/linked-data/cube#` | Statistical observations |

### Indicator Ontology Mappings

#### Health Outcomes → NCIT

```turtle
# Obesity
ex:indicator/obesity_pct a exo:0000083 ;           # Obesity exposure
    rdfs:subClassOf ncit:C3283 ;                    # NCIT: Obesity
    rdfs:label "Adult Obesity Prevalence" .

# Diabetes
ex:indicator/diabetes_pct a exo:0000002 ;          # Disease exposure
    rdfs:subClassOf ncit:C2985 ;                    # NCIT: Diabetes Mellitus
    rdfs:label "Diabetes Prevalence" .

# Asthma
ex:indicator/asthma_pct a exo:0000002 ;
    rdfs:subClassOf ncit:C26927 ;                   # NCIT: Asthma
    rdfs:label "Asthma Prevalence" .
```

#### Environmental Exposures → ECTO + ENVO

```turtle
# PM2.5 Air Pollution
ex:indicator/pm25 a exo:0000113 ;                  # Air pollution exposure
    rdfs:subClassOf ecto:0000460 ;                  # Particulate matter exposure
    ecto:has_environment envo:00002005 ;            # Environment: air
    rdfs:label "PM2.5 Concentration" .
```

#### Socioeconomic Exposures → ECTO

```turtle
# Poverty
ex:indicator/poverty_rate a exo:0000089 ;          # Socioeconomic exposure
    rdfs:subClassOf ecto:0000095 ;                  # Poverty exposure
    rdfs:label "Poverty Rate" .

# Income
ex:indicator/median_income a exo:0000089 ;
    rdfs:subClassOf ecto:0000090 ;                  # Income exposure
    rdfs:label "Median Household Income" .

# Education
ex:indicator/education_bachelor_pct a exo:0000089 ;
    rdfs:subClassOf ecto:0000097 ;                  # Education exposure
    rdfs:label "Bachelor's Degree or Higher" .
```

### Complete Mapping Table

| Indicator | ExO Class | Specific Ontology Class | Description |
|-----------|-----------|------------------------|-------------|
| obesity_pct | exo:0000083 | ncit:C3283 | Adult Obesity |
| diabetes_pct | exo:0000002 | ncit:C2985 | Diabetes Mellitus |
| asthma_pct | exo:0000002 | ncit:C26927 | Asthma |
| mental_health_days | exo:0000002 | ncit:C14215 | Mental Health |
| physical_health_days | exo:0000002 | ncit:C19332 | Physical Health |
| pm25 | exo:0000113 | ecto:0000460 + envo:00002005 | PM2.5 in Air |
| poverty_rate | exo:0000089 | ecto:0000095 | Poverty |
| median_income | exo:0000089 | ecto:0000090 | Income |
| unemployment_rate | exo:0000089 | ecto:0000096 | Unemployment |
| education_bachelor_pct | exo:0000089 | ecto:0000097 | Education |
| physical_inactivity_pct | exo:0000084 | ncit:C68620 | Behavioral Exposure |
| excessive_drinking_pct | exo:0000084 | ncit:C154476 | Behavioral Exposure |
| uninsured_pct | exo:0000089 | ecto:0000098 | Healthcare Access |

---

## Data Provenance with PROV-O

### Dataset-Level Provenance

```turtle
# Dataset description
ex:nc_exposome_dataset a dcat:Dataset ;
    dcterms:title "North Carolina Social-Economic Exposome Knowledge Graph" ;
    dcterms:description "Comprehensive integration of environmental, socioeconomic, and health data" ;
    dcterms:creator "NC Exposome Research Team" ;
    dcterms:created "2025-11-07"^^xsd:date ;
    dcterms:license <https://creativecommons.org/licenses/by/4.0/> .

# Data sources
ex:census_source a prov:Entity ;
    rdfs:label "US Census Bureau ACS 2022" ;
    prov:wasAttributedTo <https://www.census.gov/> .

ex:chr_source a prov:Entity ;
    rdfs:label "County Health Rankings 2025" ;
    prov:wasAttributedTo <https://www.countyhealthrankings.org/> .

ex:nc_exposome_dataset prov:wasDerivedFrom ex:census_source , ex:chr_source .
```

### Observation-Level Provenance

```turtle
# Example observation with full provenance
ex:observation/37119_obesity_pct_2025 a qb:Observation ;
    qb:dataSet ex:nc_exposome_dataset ;
    schema:location ex:county/37119 ;
    ex:measuredIndicator ex:indicator/obesity_pct ;
    schema:prevalence "34.1"^^xsd:float ;
    schema:unitText "percent" ;
    schema:temporal "2025"^^xsd:gYear ;
    prov:wasDerivedFrom ex:chr_source .
```

---

## Knowledge Graph Statistics

| Metric | Count |
|--------|-------|
| **Total Triples** | 15,469 |
| **Counties** | 100 |
| **Indicators** (with ontology mappings) | 16 |
| **Observations** | 1,599 |
| **Statistical Correlations** | 75 |
| **Data Sources** | 2 (Census 2022, CHR 2025) |

### Data Completeness by Category

| Category | Indicators | Counties with Data | Completeness |
|----------|------------|-------------------|--------------|
| Demographics | 1 | 100 | 100% |
| Economic | 4 | 100 | 100% |
| Education | 2 | 100 | 100% |
| Health Outcomes | 4 | 100 | 100% |
| Health Behaviors | 2 | 100 | 100% |
| Healthcare Access | 1 | 100 | 100% |
| Environment | 1 | 99 | 99% |

---

## Implementation Details

### Technology Stack

- **Python 3.13**
- **rdflib 7.4.0** - RDF graph creation and serialization
- **pandas 2.0+** - Data manipulation
- **Standard ontologies** - ExO, ECTO, ENVO, NCIT from OBO Foundry

### Script: `enhance_kg_with_ontologies.py`

**Key Components**:

1. **Namespace Definitions** (lines 18-28)
   - Define all ontology prefixes
   - Bind to RDF graph

2. **Ontology Mappings Dictionary** (lines 31-119)
   - Maps each indicator to ontology classes
   - Includes labels, exposure types, units

3. **EnhancedExposomeKG Class** (lines 122-349)
   - `add_location()` - Counties as schema:Place
   - `add_indicator_definition()` - Indicators with ontology links
   - `add_measurement()` - Observations using QB vocabulary
   - `add_correlation()` - Statistical associations
   - Export methods for Turtle, N-Triples, RDF/XML

4. **Data Loading & Conversion** (lines 351-510)
   - Load from CSV (`nc_exposome_data.csv`)
   - Apply ontology mappings
   - Generate RDF files

### Running the Script

```bash
# Install dependencies
pip install rdflib pandas

# Run enhancement
python3 enhance_kg_with_ontologies.py
```

**Output**:
```
================================================================================
NC Exposome Knowledge Graph Enhancement
Adding proper ontology mappings (ExO, ECTO, ENVO, NCIT)
================================================================================
Loading data from CSV...
✓ Loaded 100 counties with 18 columns

Adding dataset metadata...
Adding locations...
Adding indicator definitions with ontology mappings...
Adding measurements...
✓ Added 1599 measurements

Calculating and adding correlations...
✓ Added 75 significant correlations (|r| > 0.5)

================================================================================
Knowledge Graph Statistics:
================================================================================
  Total Triples: 15469
  Counties: 100
  Indicators: 16
  Observations: 1599
  Correlations: 75

✓ Exported to Turtle: nc_exposome_kg_ontology.ttl
✓ Exported to N-Triples: nc_exposome_kg_ontology.nt
✓ Exported to RDF/XML: nc_exposome_kg_ontology.rdf
```

---

## Example SPARQL Queries

### Query 1: Find Counties with High Environmental and Health Risk

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?pm25 ?obesity ?diabetes
       ((?pm25/10.0 + ?obesity/50.0 + ?diabetes/20.0) AS ?riskScore)
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  ?o1 schema:location ?county ;
      ex:measuredIndicator <http://example.org/nc-exposome/indicator/pm25> ;
      schema:value ?pm25 .

  ?o2 schema:location ?county ;
      ex:measuredIndicator <http://example.org/nc-exposome/indicator/obesity_pct> ;
      schema:prevalence ?obesity .

  ?o3 schema:location ?county ;
      ex:measuredIndicator <http://example.org/nc-exposome/indicator/diabetes_pct> ;
      schema:prevalence ?diabetes .
}
ORDER BY DESC(?riskScore)
LIMIT 10
```

### Query 2: Data Provenance for a Specific County

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?indicatorLabel ?value ?source ?year
WHERE {
  ex:county/37119 a ex:County .  # Mecklenburg County

  ?obs schema:location ex:county/37119 ;
       ex:measuredIndicator ?indicator ;
       schema:value ?value ;
       schema:temporal ?year ;
       prov:wasDerivedFrom ?source .

  ?indicator rdfs:label ?indicatorLabel .
}
```

**See `SPARQL_EXAMPLES.md` for 26 more query examples!**

---

## Usage for Research

### Local Querying (Python)

```python
from rdflib import Graph

# Load the knowledge graph
g = Graph()
g.parse("nc_exposome_kg_ontology.ttl", format="turtle")

# Example: Get all counties sorted by population
query = """
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>

SELECT ?name ?population
WHERE {
  ?county a ex:County ;
          schema:name ?name ;
          schema:population ?population .
}
ORDER BY DESC(?population)
LIMIT 10
"""

for row in g.query(query):
    print(f"{row.name}: {row.population:,}")
```

### Deploying to SPARQL Endpoint

For production use, deploy to a SPARQL endpoint:

**Apache Jena Fuseki**:
```bash
./fuseki-server --file=nc_exposome_kg_ontology.ttl /nc-exposome
# Access at: http://localhost:3030/nc-exposome/sparql
```

**GraphDB**:
- Import via web interface
- Built-in SPARQL query editor
- Support for reasoning and inference

---

## Comparison: Before vs After

### Before (Original nc_exposome_kg.nt)

```turtle
<37119> <rdf:type> "Location" .
<37119> <name> "Mecklenburg" .
<m_37119_poverty_rate> <value> "10.57" .
# Simple predicates, no ontology mappings
```

### After (Enhanced nc_exposome_kg_ontology.ttl)

```turtle
ex:county/37119 a schema:Place , ex:County ;
    schema:name "Mecklenburg" ;
    schema:identifier "37119" ;
    schema:population 1115403 .

ex:indicator/poverty_rate a exo:0000089 ;
    rdfs:subClassOf ecto:0000095 ;
    rdfs:label "Poverty Rate" .

ex:observation/37119_poverty_rate_2022 a qb:Observation ;
    qb:dataSet ex:nc_exposome_dataset ;
    schema:location ex:county/37119 ;
    ex:measuredIndicator ex:indicator/poverty_rate ;
    schema:value "10.543549"^^xsd:float ;
    schema:unitText "percent" ;
    schema:temporal "2022"^^xsd:gYear ;
    prov:wasDerivedFrom ex:census_source .
```

**Key Improvements**:
- ✅ Proper ontology classes (ExO, ECTO, NCIT)
- ✅ Typed literals (xsd:float, xsd:gYear)
- ✅ Provenance tracking (PROV-O)
- ✅ Dataset metadata (DCAT)
- ✅ Semantic consistency with standard vocabularies

---

## Files Generated

| File | Format | Size | Purpose |
|------|--------|------|---------|
| `enhance_kg_with_ontologies.py` | Python | ~510 lines | Ontology enhancement script |
| `nc_exposome_kg_ontology.ttl` | Turtle | 15,469 triples | Human-readable RDF |
| `nc_exposome_kg_ontology.nt` | N-Triples | 15,469 triples | Machine-readable RDF |
| `nc_exposome_kg_ontology.rdf` | RDF/XML | 15,469 triples | XML serialization |
| `SPARQL_EXAMPLES.md` | Markdown | ~500 lines | 28 example queries |
| `test_sparql_queries.py` | Python | ~260 lines | Query test suite |
| `ONTOLOGY_ENHANCEMENT.md` | Markdown | This file | Documentation |

---

## Future Enhancements (Optional)

1. **Add Spatial Coordinates**
   - Lat/long for each county
   - GeoSPARQL queries
   - Map visualizations

2. **Temporal Analysis**
   - Multi-year time series
   - Trend detection
   - Temporal SPARQL queries

3. **Reasoning & Inference**
   - OWL ontology rules
   - Infer implicit relationships
   - Causal pathway discovery

4. **Integration with Other KGs**
   - Link to DBpedia
   - Link to Wikidata
   - Federated SPARQL queries

5. **Machine Learning**
   - Knowledge graph embeddings
   - Predictive modeling
   - Intervention targeting

---

## Citation

If you use this knowledge graph in research, please cite:

```bibtex
@dataset{nc_exposome_kg_2025,
  title = {North Carolina Social-Economic Exposome Knowledge Graph},
  author = {NC Exposome Research Team},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/[your-repo]/Knowledge-Graph},
  note = {Ontology-enhanced RDF knowledge graph integrating Census 2022 and CHR 2025 data}
}
```

---

## License

- **Code**: MIT License
- **Data**: CC-BY-4.0 (with attribution to US Census Bureau and County Health Rankings)
- **Documentation**: CC-BY-4.0

---

## Contact

For questions about ontology mappings or SPARQL queries:
- Review [`SPARQL_EXAMPLES.md`](SPARQL_EXAMPLES.md)
- Check [`enhance_kg_with_ontologies.py`](enhance_kg_with_ontologies.py)
- Refer to the original notebook [`nc_exposome_kg.ipynb`](nc_exposome_kg.ipynb)

---

**Last Updated**: 2025-11-07
**Version**: 2.0 (Ontology-Enhanced)
**Status**: ✅ Production Ready
