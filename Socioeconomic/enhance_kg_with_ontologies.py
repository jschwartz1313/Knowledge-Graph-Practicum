#!/usr/bin/env python3
"""
Enhance NC Exposome Knowledge Graph with Proper Ontology Mappings

This script adds proper ontology URIs from:
- ExO (Exposure Ontology): http://purl.obolibrary.org/obo/ExO_
- ECTO (Environmental Conditions, Treatments and Exposures Ontology): http://purl.obolibrary.org/obo/ECTO_
- ENVO (Environment Ontology): http://purl.obolibrary.org/obo/ENVO_
- NCIT (NCI Thesaurus): http://purl.obolibrary.org/obo/NCIT_
- Additional standard vocabularies: schema.org, PROV-O, DCAT
"""

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from rdflib.namespace import DCTERMS, FOAF
import pandas as pd
import json
from datetime import datetime


# Define namespaces
EXO = Namespace("http://purl.obolibrary.org/obo/ExO_")
ECTO = Namespace("http://purl.obolibrary.org/obo/ECTO_")
ENVO = Namespace("http://purl.obolibrary.org/obo/ENVO_")
NCIT = Namespace("http://purl.obolibrary.org/obo/NCIT_")
SCHEMA = Namespace("http://schema.org/")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
EX = Namespace("http://example.org/nc-exposome/")  # Our local namespace
GEO = Namespace("http://www.opengis.net/ont/geosparql#")
QB = Namespace("http://purl.org/linked-data/cube#")


# Ontology mappings for indicators
ONTOLOGY_MAPPINGS = {
    # Health outcomes - map to NCIT and ExO
    'obesity_pct': {
        'ontology_class': NCIT.C3283,  # Obesity
        'exposure_class': EXO['0000083'],  # obesity exposure
        'label': 'Adult Obesity Prevalence',
        'property': SCHEMA.prevalence
    },
    'diabetes_pct': {
        'ontology_class': NCIT.C2985,  # Diabetes Mellitus
        'exposure_class': EXO['0000002'],  # disease exposure
        'label': 'Diabetes Prevalence',
        'property': SCHEMA.prevalence
    },
    'asthma_pct': {
        'ontology_class': NCIT.C26927,  # Asthma
        'exposure_class': EXO['0000002'],
        'label': 'Asthma Prevalence',
        'property': SCHEMA.prevalence
    },
    'mental_health_days': {
        'ontology_class': NCIT.C14215,  # Mental Health
        'exposure_class': EXO['0000002'],
        'label': 'Poor Mental Health Days',
        'property': SCHEMA.value
    },
    'physical_health_days': {
        'ontology_class': NCIT.C19332,  # Physical Health
        'exposure_class': EXO['0000002'],
        'label': 'Poor Physical Health Days',
        'property': SCHEMA.value
    },

    # Environmental exposures - map to ECTO and ENVO
    'pm25': {
        'ontology_class': ECTO['0000460'],  # particulate matter exposure
        'exposure_class': EXO['0000113'],  # air pollution exposure
        'environment': ENVO['00002005'],  # air
        'label': 'PM2.5 Concentration',
        'property': SCHEMA.value
    },

    # Socioeconomic exposures - map to ECTO
    'poverty_rate': {
        'ontology_class': ECTO['0000095'],  # poverty exposure
        'exposure_class': EXO['0000089'],  # socioeconomic exposure
        'label': 'Poverty Rate',
        'property': SCHEMA.value
    },
    'median_income': {
        'ontology_class': ECTO['0000090'],  # income exposure
        'exposure_class': EXO['0000089'],
        'label': 'Median Household Income',
        'property': SCHEMA.value
    },
    'unemployment_rate': {
        'ontology_class': ECTO['0000096'],  # unemployment exposure
        'exposure_class': EXO['0000089'],
        'label': 'Unemployment Rate',
        'property': SCHEMA.value
    },
    'unemployment_pct': {
        'ontology_class': ECTO['0000096'],
        'exposure_class': EXO['0000089'],
        'label': 'Unemployment Rate',
        'property': SCHEMA.value
    },
    'child_poverty_pct': {
        'ontology_class': ECTO['0000095'],
        'exposure_class': EXO['0000089'],
        'label': 'Child Poverty Rate',
        'property': SCHEMA.value
    },

    # Education - map to ECTO
    'education_bachelor_pct': {
        'ontology_class': ECTO['0000097'],  # education exposure
        'exposure_class': EXO['0000089'],
        'label': 'Bachelor\'s Degree or Higher',
        'property': SCHEMA.value
    },
    'some_college_pct': {
        'ontology_class': ECTO['0000097'],
        'exposure_class': EXO['0000089'],
        'label': 'Some College',
        'property': SCHEMA.value
    },

    # Health behaviors
    'physical_inactivity_pct': {
        'ontology_class': NCIT.C68620,  # Physical Inactivity
        'exposure_class': EXO['0000084'],  # behavioral exposure
        'label': 'Physical Inactivity',
        'property': SCHEMA.prevalence
    },
    'excessive_drinking_pct': {
        'ontology_class': NCIT.C154476,  # Excessive Drinking
        'exposure_class': EXO['0000084'],
        'label': 'Excessive Drinking',
        'property': SCHEMA.prevalence
    },

    # Healthcare access
    'uninsured_pct': {
        'ontology_class': ECTO['0000098'],  # healthcare access exposure
        'exposure_class': EXO['0000089'],
        'label': 'Uninsured Rate',
        'property': SCHEMA.value
    },

    # Demographics
    'population': {
        'ontology_class': NCIT.C17005,  # Population
        'label': 'Total Population',
        'property': SCHEMA.population
    }
}


class EnhancedExposomeKG:
    """Enhanced Knowledge Graph with proper ontology mappings"""

    def __init__(self):
        self.graph = Graph()
        self._bind_namespaces()
        self.dataset_uri = EX.nc_exposome_dataset

    def _bind_namespaces(self):
        """Bind all namespaces to the graph"""
        self.graph.bind('exo', EXO)
        self.graph.bind('ecto', ECTO)
        self.graph.bind('envo', ENVO)
        self.graph.bind('ncit', NCIT)
        self.graph.bind('schema', SCHEMA)
        self.graph.bind('prov', PROV)
        self.graph.bind('dcat', DCAT)
        self.graph.bind('ex', EX)
        self.graph.bind('geo', GEO)
        self.graph.bind('qb', QB)
        self.graph.bind('dcterms', DCTERMS)
        self.graph.bind('foaf', FOAF)

    def add_dataset_metadata(self):
        """Add DCAT metadata about the dataset itself"""
        dataset = self.dataset_uri

        # Dataset description
        self.graph.add((dataset, RDF.type, DCAT.Dataset))
        self.graph.add((dataset, DCTERMS.title,
                       Literal("North Carolina Social-Economic Exposome Knowledge Graph")))
        self.graph.add((dataset, DCTERMS.description,
                       Literal("A comprehensive knowledge graph integrating environmental, "
                              "socioeconomic, and health data for all 100 counties in North Carolina")))
        self.graph.add((dataset, DCTERMS.creator, Literal("NC Exposome Research Team")))
        self.graph.add((dataset, DCTERMS.created,
                       Literal(datetime.now().strftime("%Y-%m-%d"), datatype=XSD.date)))
        self.graph.add((dataset, DCTERMS.license,
                       URIRef("https://creativecommons.org/licenses/by/4.0/")))

        # Data sources as provenance
        census_source = EX.census_source
        self.graph.add((census_source, RDF.type, PROV.Entity))
        self.graph.add((census_source, RDFS.label, Literal("US Census Bureau ACS 2022")))
        self.graph.add((census_source, PROV.wasAttributedTo,
                       URIRef("https://www.census.gov/")))

        chr_source = EX.chr_source
        self.graph.add((chr_source, RDF.type, PROV.Entity))
        self.graph.add((chr_source, RDFS.label, Literal("County Health Rankings 2025")))
        self.graph.add((chr_source, PROV.wasAttributedTo,
                       URIRef("https://www.countyhealthrankings.org/")))

        self.graph.add((dataset, PROV.wasDerivedFrom, census_source))
        self.graph.add((dataset, PROV.wasDerivedFrom, chr_source))

    def add_location(self, fips, county_name, state="North Carolina", population=None):
        """Add a location (county) with proper geo ontology"""
        county_uri = EX[f"county/{fips}"]

        # Type as both a schema.org Place and our Location
        self.graph.add((county_uri, RDF.type, SCHEMA.Place))
        self.graph.add((county_uri, RDF.type, EX.County))

        # Basic properties
        self.graph.add((county_uri, SCHEMA.name, Literal(county_name)))
        self.graph.add((county_uri, SCHEMA.identifier, Literal(fips)))
        # Use proper URI encoding for state (replace space with underscore)
        state_uri = EX[f"state/{state.replace(' ', '_')}"]
        self.graph.add((county_uri, SCHEMA.containedInPlace, state_uri))

        # Geographic info
        self.graph.add((county_uri, GEO.sfWithin, EX.state_north_carolina))

        if population:
            self.graph.add((county_uri, SCHEMA.population,
                          Literal(int(population), datatype=XSD.integer)))

        return county_uri

    def add_indicator_definition(self, indicator_id):
        """Add indicator definition with ontology mappings"""
        if indicator_id not in ONTOLOGY_MAPPINGS:
            return None

        mapping = ONTOLOGY_MAPPINGS[indicator_id]
        indicator_uri = EX[f"indicator/{indicator_id}"]

        # Type as Exposure (from ExO)
        self.graph.add((indicator_uri, RDF.type, EXO['0000000']))  # Exposure
        if 'exposure_class' in mapping:
            self.graph.add((indicator_uri, RDF.type, mapping['exposure_class']))

        # Link to specific ontology class
        if 'ontology_class' in mapping:
            self.graph.add((indicator_uri, RDFS.subClassOf, mapping['ontology_class']))

        # Environment link for environmental exposures
        if 'environment' in mapping:
            self.graph.add((indicator_uri, ECTO['0000000'], mapping['environment']))  # has_environment

        # Label
        self.graph.add((indicator_uri, RDFS.label, Literal(mapping['label'])))

        return indicator_uri

    def add_measurement(self, county_uri, indicator_id, value, unit=None,
                       year=None, source=None):
        """Add a measurement observation using QB (Data Cube) vocabulary"""
        if indicator_id not in ONTOLOGY_MAPPINGS:
            return None

        mapping = ONTOLOGY_MAPPINGS[indicator_id]

        # Create observation URI
        county_fips = str(county_uri).split('/')[-1]
        obs_uri = EX[f"observation/{county_fips}_{indicator_id}_{year or 'unknown'}"]

        # Type as Observation
        self.graph.add((obs_uri, RDF.type, QB.Observation))
        self.graph.add((obs_uri, RDF.type, EX.ExposureMeasurement))

        # Link to location and indicator
        self.graph.add((obs_uri, QB.dataSet, self.dataset_uri))
        self.graph.add((obs_uri, SCHEMA.location, county_uri))
        self.graph.add((obs_uri, EX.measuredIndicator, EX[f"indicator/{indicator_id}"]))

        # Value using proper property
        property_uri = mapping.get('property', SCHEMA.value)

        # Type the value based on indicator
        if unit in ['percent', 'ratio']:
            typed_value = Literal(float(value), datatype=XSD.float)
        elif unit == 'USD':
            typed_value = Literal(int(value), datatype=XSD.integer)
        elif unit == 'count':
            typed_value = Literal(int(value), datatype=XSD.integer)
        else:
            typed_value = Literal(float(value), datatype=XSD.float)

        self.graph.add((obs_uri, property_uri, typed_value))

        # Unit
        if unit:
            self.graph.add((obs_uri, SCHEMA.unitText, Literal(unit)))

        # Temporal
        if year:
            self.graph.add((obs_uri, SCHEMA.temporal,
                          Literal(str(year), datatype=XSD.gYear)))

        # Provenance
        if source:
            source_uri = EX[f"{source.lower()}_source"]
            self.graph.add((obs_uri, PROV.wasDerivedFrom, source_uri))

        return obs_uri

    def add_correlation(self, indicator1_id, indicator2_id, correlation_value,
                       p_value=None, n_samples=None):
        """Add statistical correlation as association"""
        corr_uri = EX[f"correlation/{indicator1_id}_{indicator2_id}"]

        self.graph.add((corr_uri, RDF.type, EX.StatisticalAssociation))
        self.graph.add((corr_uri, SCHEMA.about, EX[f"indicator/{indicator1_id}"]))
        self.graph.add((corr_uri, SCHEMA.about, EX[f"indicator/{indicator2_id}"]))
        self.graph.add((corr_uri, SCHEMA.value,
                      Literal(float(correlation_value), datatype=XSD.float)))

        if p_value is not None:
            self.graph.add((corr_uri, EX.pValue,
                          Literal(float(p_value), datatype=XSD.float)))

        if n_samples is not None:
            self.graph.add((corr_uri, EX.sampleSize,
                          Literal(int(n_samples), datatype=XSD.integer)))

        # Add confidence based on p-value
        if p_value is not None:
            if p_value < 0.001:
                confidence = "high"
            elif p_value < 0.01:
                confidence = "medium"
            elif p_value < 0.05:
                confidence = "low"
            else:
                confidence = "not_significant"
            self.graph.add((corr_uri, EX.confidence, Literal(confidence)))

        return corr_uri

    def export_turtle(self, filename):
        """Export to Turtle format (more readable than N-Triples)"""
        self.graph.serialize(destination=filename, format='turtle')
        print(f"✓ Exported to Turtle: {filename}")

    def export_ntriples(self, filename):
        """Export to N-Triples format"""
        self.graph.serialize(destination=filename, format='nt')
        print(f"✓ Exported to N-Triples: {filename}")

    def export_rdfxml(self, filename):
        """Export to RDF/XML format"""
        self.graph.serialize(destination=filename, format='xml')
        print(f"✓ Exported to RDF/XML: {filename}")

    def get_statistics(self):
        """Get statistics about the knowledge graph"""
        stats = {
            'total_triples': len(self.graph),
            'counties': len(list(self.graph.subjects(RDF.type, EX.County))),
            'indicators': len(list(self.graph.subjects(RDF.type, EXO['0000000']))),
            'observations': len(list(self.graph.subjects(RDF.type, QB.Observation))),
            'correlations': len(list(self.graph.subjects(RDF.type, EX.StatisticalAssociation))),
        }
        return stats


def load_and_convert_data(csv_file='nc_exposome_data.csv'):
    """Load existing data and convert to enhanced KG"""
    print("Loading data from CSV...")
    df = pd.read_csv(csv_file)
    print(f"✓ Loaded {len(df)} counties with {len(df.columns)} columns")

    # Initialize enhanced KG
    kg = EnhancedExposomeKG()

    # Add dataset metadata
    print("\nAdding dataset metadata...")
    kg.add_dataset_metadata()

    # Add locations
    print("\nAdding locations...")
    for _, row in df.iterrows():
        kg.add_location(
            fips=row['fips'],
            county_name=row['county'],
            state="North Carolina",
            population=row.get('population')
        )

    # Add indicator definitions
    print("\nAdding indicator definitions with ontology mappings...")
    for indicator_id in ONTOLOGY_MAPPINGS.keys():
        if indicator_id in df.columns:
            kg.add_indicator_definition(indicator_id)

    # Add measurements
    print("\nAdding measurements...")
    measurement_count = 0
    for _, row in df.iterrows():
        county_uri = EX[f"county/{row['fips']}"]

        for indicator_id, mapping in ONTOLOGY_MAPPINGS.items():
            if indicator_id in df.columns and pd.notna(row[indicator_id]):
                # Determine source and year from context
                if indicator_id in ['obesity_pct', 'diabetes_pct', 'mental_health_days',
                                   'physical_health_days', 'uninsured_pct', 'pm25',
                                   'child_poverty_pct', 'some_college_pct', 'unemployment_pct',
                                   'physical_inactivity_pct', 'excessive_drinking_pct']:
                    source = 'CHR'
                    year = 2025
                else:
                    source = 'Census'
                    year = 2022

                # Determine unit
                if '_pct' in indicator_id or '_rate' in indicator_id:
                    unit = 'percent'
                elif indicator_id == 'median_income':
                    unit = 'USD'
                elif indicator_id == 'population':
                    unit = 'count'
                elif indicator_id == 'pm25':
                    unit = 'μg/m³'
                elif 'days' in indicator_id:
                    unit = 'days'
                else:
                    unit = None

                kg.add_measurement(
                    county_uri=county_uri,
                    indicator_id=indicator_id,
                    value=row[indicator_id],
                    unit=unit,
                    year=year,
                    source=source
                )
                measurement_count += 1

    print(f"✓ Added {measurement_count} measurements")

    # Add correlations
    print("\nCalculating and adding correlations...")
    numeric_cols = [col for col in df.columns
                   if col in ONTOLOGY_MAPPINGS and df[col].notna().sum() > len(df) * 0.7]

    if len(numeric_cols) > 1:
        correlation_matrix = df[numeric_cols].corr()
        correlation_count = 0

        for i, ind1 in enumerate(numeric_cols):
            for j, ind2 in enumerate(numeric_cols):
                if i < j:  # Avoid duplicates
                    corr_value = correlation_matrix.loc[ind1, ind2]
                    if pd.notna(corr_value) and abs(corr_value) > 0.5:
                        kg.add_correlation(ind1, ind2, corr_value)
                        correlation_count += 1

        print(f"✓ Added {correlation_count} significant correlations (|r| > 0.5)")

    return kg


def main():
    """Main execution function"""
    print("=" * 80)
    print("NC Exposome Knowledge Graph Enhancement")
    print("Adding proper ontology mappings (ExO, ECTO, ENVO, NCIT)")
    print("=" * 80)

    # Load and convert data
    kg = load_and_convert_data('nc_exposome_data.csv')

    # Print statistics
    print("\n" + "=" * 80)
    print("Knowledge Graph Statistics:")
    print("=" * 80)
    stats = kg.get_statistics()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    # Export in multiple formats
    print("\n" + "=" * 80)
    print("Exporting Knowledge Graph:")
    print("=" * 80)

    kg.export_turtle('nc_exposome_kg_ontology.ttl')
    kg.export_ntriples('nc_exposome_kg_ontology.nt')
    kg.export_rdfxml('nc_exposome_kg_ontology.rdf')

    print("\n✓ Knowledge graph enhancement complete!")
    print("\nGenerated files:")
    print("  - nc_exposome_kg_ontology.ttl (Turtle format - most readable)")
    print("  - nc_exposome_kg_ontology.nt (N-Triples format)")
    print("  - nc_exposome_kg_ontology.rdf (RDF/XML format)")

    print("\nOntologies used:")
    print("  - ExO: Exposure Ontology")
    print("  - ECTO: Environmental Conditions, Treatments and Exposures Ontology")
    print("  - ENVO: Environment Ontology")
    print("  - NCIT: NCI Thesaurus")
    print("  - Schema.org: Web vocabulary")
    print("  - PROV-O: Provenance Ontology")
    print("  - DCAT: Data Catalog Vocabulary")
    print("  - QB: RDF Data Cube")


if __name__ == '__main__':
    main()
