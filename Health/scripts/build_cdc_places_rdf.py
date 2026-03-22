"""
build_cdc_places_rdf.py
Converts cdc_places_nc_counties.csv into RDF triples (Turtle) following the
same SOSA + PROV-O + schema.org + RDF-Data-Cube pattern used by the rest of
the NC Exposome Knowledge Graph.

Input:   Socioeconomic/cdc_places_nc_counties.csv
Output:  Socioeconomic/cdc_places_2024.ttl
"""

from pathlib import Path
import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, XSD

BASE   = Namespace("http://example.org/nc-exposome/")
SOSA   = Namespace("http://www.w3.org/ns/sosa#")
PROV   = Namespace("http://www.w3.org/ns/prov#")
QB     = Namespace("http://purl.org/linked-data/cube#")
SCHEMA = Namespace("http://schema.org/")
RDFS   = Namespace("http://www.w3.org/2000/01/rdf-schema#")
NCIT   = Namespace("http://purl.obolibrary.org/obo/NCIT_")
ECTO   = Namespace("http://purl.obolibrary.org/obo/ECTO_")

DATA_YEAR = 2024
SRC_NODE  = BASE["dataset/CDC_PLACES_2024"]

# ---------------------------------------------------------------------------
# Indicator metadata: csv_col -> (label, unit, ontology_type)
# ---------------------------------------------------------------------------
INDICATORS = {
    # Chronic disease outcomes
    "arthritis_pct":               ("Arthritis among Adults",                     "%", NCIT["C26882"]),
    "high_blood_pressure_pct":     ("High Blood Pressure among Adults",            "%", NCIT["C3117"]),
    "cancer_pct":                  ("Cancer (excl. skin) among Adults",            "%", NCIT["C9305"]),
    "asthma_pct":                  ("Current Asthma among Adults",                 "%", NCIT["C28397"]),
    "coronary_heart_disease_pct":  ("Coronary Heart Disease among Adults",         "%", NCIT["C26732"]),
    "copd_pct":                    ("COPD among Adults",                           "%", NCIT["C3199"]),
    "depression_pct":              ("Depression among Adults",                     "%", NCIT["C2981"]),
    "diabetes_pct":                ("Diabetes among Adults",                       "%", NCIT["C2985"]),
    "high_cholesterol_pct":        ("High Cholesterol among Adults (screened)",    "%", None),
    "obesity_pct":                 ("Obesity among Adults",                        "%", NCIT["C3283"]),
    "stroke_pct":                  ("Stroke among Adults",                         "%", NCIT["C3390"]),
    "teeth_lost_pct":              ("All Teeth Lost among Adults 65+",             "%", None),
    "kidney_disease_pct":          ("Chronic Kidney Disease among Adults",         "%", None),
    # Health behaviours
    "binge_drinking_pct":          ("Binge Drinking among Adults",                 "%", None),
    "current_smoking_pct":         ("Current Smoking among Adults",                "%", ECTO["0000460"]),
    "physical_inactivity_pct":     ("No Leisure-Time Physical Activity",           "%", None),
    "short_sleep_pct":             ("Short Sleep Duration (<7 hrs)",               "%", None),
    # Preventive care / screenings
    "annual_checkup_pct":          ("Annual Checkup among Adults",                 "%", None),
    "cholesterol_screen_pct":      ("Cholesterol Screening among Adults",          "%", None),
    "colorectal_screen_pct":       ("Colorectal Cancer Screening (ages 45-75)",    "%", None),
    "mammography_pct":             ("Mammography Use among Women 50-74",           "%", None),
    "dental_visit_pct":            ("Dental Visit in Past Year",                   "%", None),
    # Disability
    "hearing_disability_pct":      ("Hearing Disability among Adults",             "%", None),
    "vision_disability_pct":       ("Vision Disability among Adults",              "%", None),
    "cognitive_disability_pct":    ("Cognitive Disability among Adults",           "%", None),
    "mobility_disability_pct":     ("Mobility Disability among Adults",            "%", None),
    "selfcare_disability_pct":     ("Self-Care Disability among Adults",           "%", None),
    # Insurance
    "no_health_insurance_pct":     ("No Health Insurance among Adults 18-64",      "%", None),
}


def build_graph(df: pd.DataFrame) -> Graph:
    g = Graph()
    g.bind("ex",     BASE)
    g.bind("sosa",   SOSA)
    g.bind("prov",   PROV)
    g.bind("qb",     QB)
    g.bind("schema", SCHEMA)
    g.bind("rdfs",   RDFS)
    g.bind("ncit",   NCIT)
    g.bind("ecto",   ECTO)
    g.bind("xsd",    XSD)

    # Provenance dataset node
    g.add((SRC_NODE, RDF.type,             PROV.Entity))
    g.add((SRC_NODE, SCHEMA.name,          Literal("CDC PLACES: Local Data for Better Health, County Data 2024")))
    g.add((SRC_NODE, SCHEMA.publisher,     Literal("Centers for Disease Control and Prevention (CDC)")))
    g.add((SRC_NODE, SCHEMA.temporalCoverage, Literal("2024")))

    # Declare indicator nodes
    for col, (label, unit, ont) in INDICATORS.items():
        ind = BASE[f"indicator/{col}"]
        g.add((ind, RDF.type,           QB.MeasureProperty))
        g.add((ind, RDFS.label,         Literal(label)))
        g.add((ind, SCHEMA.unitText,    Literal(unit)))
        if ont:
            g.add((ind, RDFS.subClassOf, ont))

    # One Observation per (county, indicator) pair
    for _, row in df.iterrows():
        fips   = str(row["fips"]).zfill(5)
        county = BASE[f"county/{fips}"]

        for col, (label, unit, _) in INDICATORS.items():
            val = row.get(col)
            if pd.isna(val):
                continue
            ind = BASE[f"indicator/{col}"]
            obs = BASE[f"obs/{col}/{fips}/{DATA_YEAR}"]

            g.add((obs, RDF.type,                   SOSA.Observation))
            g.add((obs, RDF.type,                   QB.Observation))
            g.add((obs, SOSA.hasFeatureOfInterest,  county))
            g.add((obs, SOSA.observedProperty,      ind))
            g.add((obs, SOSA.resultTime,            Literal(f"{DATA_YEAR}-12-31", datatype=XSD.date)))
            g.add((obs, SOSA.hasSimpleResult,       Literal(float(val), datatype=XSD.float)))
            g.add((obs, SCHEMA.location,            county))
            g.add((obs, BASE["measuredIndicator"],  ind))
            g.add((obs, SCHEMA.value,               Literal(float(val), datatype=XSD.float)))
            g.add((obs, SCHEMA.unitText,            Literal(unit)))
            g.add((obs, SCHEMA.temporal,            Literal(str(DATA_YEAR), datatype=XSD.gYear)))
            g.add((obs, PROV.wasDerivedFrom,        SRC_NODE))
            g.add((obs, QB.dataSet,                 BASE["nc_exposome_dataset"]))

    return g


def main():
    processed = Path(__file__).parent.parent / "data" / "processed"
    in_path  = processed / "cdc_places_nc_counties.csv"
    out_path = processed / "cdc_places_2024.ttl"

    df = pd.read_csv(in_path, dtype={"fips": str})
    print(f"Loaded {len(df)} counties from {in_path.name}")

    g = build_graph(df)
    g.serialize(str(out_path), format="turtle")

    print(f"Wrote {len(g):,} triples → {out_path}")


if __name__ == "__main__":
    main()
