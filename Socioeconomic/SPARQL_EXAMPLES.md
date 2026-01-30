# SPARQL Query Examples for NC Exposome Knowledge Graph

This document provides example SPARQL queries demonstrating how to explore and analyze the North Carolina Exposome Knowledge Graph. These queries showcase associations between environmental variables, socioeconomic indicators, and health outcomes.

## Table of Contents

1. [Basic Queries](#basic-queries)
2. [Environmental-Health Associations](#environmental-health-associations)
3. [Socioeconomic-Health Pathways](#socioeconomic-health-pathways)
4. [County Comparison Queries](#county-comparison-queries)
5. [Statistical Analysis Queries](#statistical-analysis-queries)
6. [Data Provenance Queries](#data-provenance-queries)
7. [Advanced Analytical Queries](#advanced-analytical-queries)

---

## Setup

### Namespaces

All queries use the following namespace prefixes:

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX exo: <http://purl.obolibrary.org/obo/ExO_>
PREFIX ecto: <http://purl.obolibrary.org/obo/ECTO_>
PREFIX envo: <http://purl.obolibrary.org/obo/ENVO_>
PREFIX ncit: <http://purl.obolibrary.org/obo/NCIT_>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
```

---

## Basic Queries

### Query 1.1: List All Counties

Retrieve all counties in the knowledge graph with their names and FIPS codes.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>

SELECT ?county ?name ?fips ?population
WHERE {
  ?county a ex:County ;
          schema:name ?name ;
          schema:identifier ?fips .
  OPTIONAL { ?county schema:population ?population }
}
ORDER BY ?name
```

**Purpose**: Basic inventory of all geographic entities in the knowledge graph.

---

### Query 1.2: List All Indicators with Ontology Mappings

Get all exposure indicators with their ontology classifications.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX exo: <http://purl.obolibrary.org/obo/ExO_>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?indicator ?label ?exposureType ?ontologyClass
WHERE {
  ?indicator a exo:0000000 ;  # Exposure class
             rdfs:label ?label .
  OPTIONAL { ?indicator a ?exposureType . FILTER(?exposureType != exo:0000000) }
  OPTIONAL { ?indicator rdfs:subClassOf ?ontologyClass }
}
ORDER BY ?label
```

**Purpose**: Understand the semantic structure and ontology mappings of indicators.

---

### Query 1.3: Count Observations by Data Source

Get the number of observations from each data source.

```sparql
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?source (COUNT(?obs) AS ?count)
WHERE {
  ?obs a qb:Observation ;
       prov:wasDerivedFrom ?source .
}
GROUP BY ?source
ORDER BY DESC(?count)
```

**Purpose**: Data provenance summary showing data source distribution.

---

## Environmental-Health Associations

### Query 2.1: PM2.5 and Diabetes Correlation by County

Find counties with high PM2.5 exposure and diabetes prevalence.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?pm25 ?diabetes
WHERE {
  # Get county info
  ?county a ex:County ;
          schema:name ?countyName .

  # PM2.5 observation
  ?obs1 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/pm25 ;
        schema:value ?pm25 .

  # Diabetes observation
  ?obs2 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/diabetes_pct ;
        schema:prevalence ?diabetes .

  # Filter for high values
  FILTER(?pm25 > 8.0 && ?diabetes > 11.0)
}
ORDER BY DESC(?pm25)
```

**Purpose**: Identify counties where air quality (PM2.5) correlates with diabetes prevalence.

**Expected Use Case**: Environmental health researchers studying the impact of particulate matter on chronic disease.

---

### Query 2.2: Environmental Vulnerability Index

Calculate a composite environmental vulnerability score for each county.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName
       ?pm25
       ?obesity
       ?diabetes
       ((?pm25/10.0 + ?obesity/50.0 + ?diabetes/20.0) AS ?vulnScore)
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  ?obs1 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/pm25 ;
        schema:value ?pm25 .

  ?obs2 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/obesity_pct ;
        schema:prevalence ?obesity .

  ?obs3 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/diabetes_pct ;
        schema:prevalence ?diabetes .
}
ORDER BY DESC(?vulnScore)
LIMIT 20
```

**Purpose**: Rank counties by environmental and health vulnerability.

---

## Socioeconomic-Health Pathways

### Query 3.1: Poverty and Health Outcomes

Examine the relationship between poverty and multiple health outcomes.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?poverty ?obesity ?diabetes ?mentalHealth
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  # Poverty rate
  ?pov a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ex:indicator/poverty_rate ;
       schema:value ?poverty .

  # Obesity
  ?ob a qb:Observation ;
      schema:location ?county ;
      ex:measuredIndicator ex:indicator/obesity_pct ;
      schema:prevalence ?obesity .

  # Diabetes
  ?dia a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ex:indicator/diabetes_pct ;
       schema:prevalence ?diabetes .

  # Mental health
  ?mh a qb:Observation ;
      schema:location ?county ;
      ex:measuredIndicator ex:indicator/mental_health_days ;
      schema:value ?mentalHealth .

  FILTER(?poverty > 15.0)  # High poverty counties
}
ORDER BY DESC(?poverty)
```

**Purpose**: Identify socioeconomic determinants of health in high-poverty areas.

**Expected Use Case**: Public health interventions targeting areas with concentrated poverty and poor health outcomes.

---

### Query 3.2: Education and Health Behaviors

Explore how education levels correlate with health behaviors.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?education ?inactivity ?drinking
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  # Education (Bachelor's degree or higher)
  ?edu a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ex:indicator/education_bachelor_pct ;
       schema:value ?education .

  # Physical inactivity
  ?inact a qb:Observation ;
         schema:location ?county ;
         ex:measuredIndicator ex:indicator/physical_inactivity_pct ;
         schema:prevalence ?inactivity .

  # Excessive drinking
  ?drink a qb:Observation ;
         schema:location ?county ;
         ex:measuredIndicator ex:indicator/excessive_drinking_pct ;
         schema:prevalence ?drinking .
}
ORDER BY DESC(?education)
```

**Purpose**: Examine relationship between educational attainment and health behaviors.

---

### Query 3.3: Unemployment and Mental Health

Investigate the association between unemployment and mental health outcomes.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?unemployment ?mentalHealthDays ?physicalHealthDays
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  # Unemployment rate
  ?unemp a qb:Observation ;
         schema:location ?county ;
         ex:measuredIndicator ex:indicator/unemployment_rate ;
         schema:value ?unemployment .

  # Mental health days
  ?mh a qb:Observation ;
      schema:location ?county ;
      ex:measuredIndicator ex:indicator/mental_health_days ;
      schema:value ?mentalHealthDays .

  # Physical health days
  ?ph a qb:Observation ;
      schema:location ?county ;
      ex:measuredIndicator ex:indicator/physical_health_days ;
      schema:value ?physicalHealthDays .

  FILTER(?unemployment > 5.0)
}
ORDER BY DESC(?unemployment)
```

**Purpose**: Study mental and physical health impacts of unemployment.

---

## County Comparison Queries

### Query 4.1: Compare Top 5 Populous Counties

Compare health and socioeconomic indicators across the largest counties.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?population ?medianIncome ?poverty ?diabetes
WHERE {
  ?county a ex:County ;
          schema:name ?countyName ;
          schema:population ?population .

  # Median income
  ?inc a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ex:indicator/median_income ;
       schema:value ?medianIncome .

  # Poverty rate
  ?pov a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ex:indicator/poverty_rate ;
       schema:value ?poverty .

  # Diabetes
  ?dia a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ex:indicator/diabetes_pct ;
       schema:prevalence ?diabetes .
}
ORDER BY DESC(?population)
LIMIT 5
```

**Purpose**: Head-to-head comparison of major metropolitan counties.

---

### Query 4.2: Rural vs Urban Health Disparities

Identify health disparities between low and high population counties.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?category
       (AVG(?obesity) AS ?avgObesity)
       (AVG(?diabetes) AS ?avgDiabetes)
       (AVG(?uninsured) AS ?avgUninsured)
WHERE {
  ?county a ex:County ;
          schema:population ?population .

  ?obs1 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/obesity_pct ;
        schema:prevalence ?obesity .

  ?obs2 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/diabetes_pct ;
        schema:prevalence ?diabetes .

  ?obs3 a qb:Observation ;
        schema:location ?county ;
        ex:measuredIndicator ex:indicator/uninsured_pct ;
        schema:value ?uninsured .

  BIND(IF(?population > 100000, "Urban", "Rural") AS ?category)
}
GROUP BY ?category
```

**Purpose**: Calculate average health outcomes for rural vs urban counties.

---

## Statistical Analysis Queries

### Query 5.1: Find Strong Correlations

Retrieve all statistical associations with correlation coefficient > 0.8.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?indicator1Label ?indicator2Label ?correlation
WHERE {
  ?corr a ex:StatisticalAssociation ;
        schema:about ?indicator1 , ?indicator2 ;
        schema:value ?correlation .

  ?indicator1 rdfs:label ?indicator1Label .
  ?indicator2 rdfs:label ?indicator2Label .

  FILTER(?indicator1 != ?indicator2)
  FILTER(ABS(?correlation) > 0.8)
}
ORDER BY DESC(?correlation)
```

**Purpose**: Identify strongest statistical relationships between indicators.

---

### Query 5.2: Protective vs Risk Factors for Diabetes

Find indicators that are positively or negatively correlated with diabetes.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?indicatorLabel ?correlation ?type
WHERE {
  ?corr a ex:StatisticalAssociation ;
        schema:about ex:indicator/diabetes_pct , ?indicator ;
        schema:value ?correlation .

  ?indicator rdfs:label ?indicatorLabel .

  FILTER(?indicator != ex:indicator/diabetes_pct)
  FILTER(ABS(?correlation) > 0.6)

  BIND(IF(?correlation > 0, "Risk Factor", "Protective Factor") AS ?type)
}
ORDER BY DESC(?correlation)
```

**Purpose**: Distinguish protective factors from risk factors for diabetes.

---

### Query 5.3: Correlation Network for Poverty

Find all indicators correlated with poverty rate.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?indicatorLabel ?correlation
WHERE {
  ?corr a ex:StatisticalAssociation ;
        schema:about ex:indicator/poverty_rate , ?indicator ;
        schema:value ?correlation .

  ?indicator rdfs:label ?indicatorLabel .

  FILTER(?indicator != ex:indicator/poverty_rate)
  FILTER(ABS(?correlation) > 0.5)
}
ORDER BY DESC(ABS(?correlation))
```

**Purpose**: Map the network of factors associated with poverty.

---

## Data Provenance Queries

### Query 6.1: Data Source Attribution

Get data source information for all observations in a specific county.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?indicator ?value ?source ?year
WHERE {
  # Mecklenburg County (FIPS: 37119)
  ?county a ex:County ;
          schema:identifier "37119" .

  ?obs a qb:Observation ;
       schema:location ?county ;
       ex:measuredIndicator ?indUri ;
       schema:value ?value ;
       schema:temporal ?year ;
       prov:wasDerivedFrom ?source .

  ?indUri rdfs:label ?indicator .
}
ORDER BY ?indicator
```

**Purpose**: Trace data provenance for transparency and reproducibility.

---

### Query 6.2: Dataset Metadata

Retrieve metadata about the knowledge graph dataset itself.

```sparql
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?title ?description ?created ?license ?source
WHERE {
  ?dataset a dcat:Dataset ;
           dcterms:title ?title ;
           dcterms:description ?description ;
           dcterms:created ?created ;
           dcterms:license ?license .

  OPTIONAL { ?dataset prov:wasDerivedFrom ?source }
}
```

**Purpose**: Access dataset-level metadata for citations and documentation.

---

## Advanced Analytical Queries

### Query 7.1: Multi-Dimensional Health Risk Profile

Create a comprehensive health risk profile combining multiple exposures.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName
       ?poverty ?pm25 ?uninsured
       ?obesity ?diabetes ?inactivity
       ((?poverty/25.0 + ?pm25/10.0 + ?uninsured/20.0 +
         ?obesity/50.0 + ?diabetes/20.0 + ?inactivity/40.0) AS ?riskScore)
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  # Social exposures
  ?o1 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/poverty_rate ; schema:value ?poverty .
  ?o2 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/uninsured_pct ; schema:value ?uninsured .

  # Environmental exposure
  ?o3 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/pm25 ; schema:value ?pm25 .

  # Health outcomes
  ?o4 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/obesity_pct ; schema:prevalence ?obesity .
  ?o5 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/diabetes_pct ; schema:prevalence ?diabetes .
  ?o6 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/physical_inactivity_pct ; schema:prevalence ?inactivity .
}
ORDER BY DESC(?riskScore)
LIMIT 10
```

**Purpose**: Identify counties with highest multi-factor health risk.

**Expected Use Case**: Public health resource allocation and intervention prioritization.

---

### Query 7.2: Socioeconomic Advantage Index

Calculate a socioeconomic advantage composite score.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?countyName ?medianIncome ?education ?employment
       ((?medianIncome/100000.0 + ?education/50.0 + (100-?poverty)/100.0) AS ?advantageScore)
WHERE {
  ?county a ex:County ;
          schema:name ?countyName .

  ?o1 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/median_income ; schema:value ?medianIncome .

  ?o2 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/education_bachelor_pct ; schema:value ?education .

  ?o3 a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/poverty_rate ; schema:value ?poverty .
}
ORDER BY DESC(?advantageScore)
LIMIT 10
```

**Purpose**: Identify counties with highest socioeconomic resources.

---

### Query 7.3: Health Equity Analysis

Compare health outcomes between high and low socioeconomic status counties.

```sparql
PREFIX ex: <http://example.org/nc-exposome/>
PREFIX schema: <http://schema.org/>
PREFIX qb: <http://purl.org/linked-data/cube#>

SELECT ?sesCategory
       (AVG(?obesity) AS ?avgObesity)
       (AVG(?diabetes) AS ?avgDiabetes)
       (AVG(?mentalHealth) AS ?avgMentalHealth)
       (COUNT(?county) AS ?countyCount)
WHERE {
  ?county a ex:County .

  # Income as SES proxy
  ?inc a qb:Observation ; schema:location ?county ;
       ex:measuredIndicator ex:indicator/median_income ; schema:value ?medianIncome .

  # Health outcomes
  ?ob a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/obesity_pct ; schema:prevalence ?obesity .
  ?dia a qb:Observation ; schema:location ?county ;
       ex:measuredIndicator ex:indicator/diabetes_pct ; schema:prevalence ?diabetes .
  ?mh a qb:Observation ; schema:location ?county ;
      ex:measuredIndicator ex:indicator/mental_health_days ; schema:value ?mentalHealth .

  BIND(IF(?medianIncome > 60000, "High SES", "Low SES") AS ?sesCategory)
}
GROUP BY ?sesCategory
```

**Purpose**: Quantify health disparities by socioeconomic status.

---

## Using These Queries

### Online SPARQL Endpoints

If you deploy this knowledge graph to a SPARQL endpoint (e.g., Apache Jena Fuseki, GraphDB), you can run these queries via:

1. **Web Interface**: Most SPARQL endpoints provide a web-based query interface
2. **HTTP API**: Send POST requests to the endpoint
3. **Programming Libraries**: Use libraries like `rdflib` (Python) or `jena` (Java)

### Local Query Execution (Python)

```python
from rdflib import Graph

# Load the knowledge graph
g = Graph()
g.parse("nc_exposome_kg_ontology.ttl", format="turtle")

# Execute a query
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

results = g.query(query)
for row in results:
    print(f"{row.name}: {row.population:,}")
```

### Query Visualization

Results from these queries can be visualized using:
- **Tableau/PowerBI**: For dashboards
- **Gephi**: For network visualizations
- **D3.js**: For interactive web visualizations
- **Python (matplotlib/seaborn)**: For statistical plots

---

## Contact & Contribution

For questions or to contribute additional queries, please contact the NC Exposome Research Team or submit a pull request to the GitHub repository.

---

**License**: CC-BY-4.0
**Last Updated**: 2025-11-07
