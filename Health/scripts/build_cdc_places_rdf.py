"""
build_cdc_places_rdf.py
Converts cdc_places_nc_counties.csv into RDF triples (Turtle) following the
same SOSA + PROV-O + schema.org + RDF-Data-Cube pattern used by the rest of
the NC Exposome Knowledge Graph.

Each indicator node is typed against:
  - Its condition/outcome class in NCIT or ECTO (rdfs:subClassOf)
  - Its ExO exposure class (ex:exposureClass) where applicable

Input:   Health/data/processed/cdc_places_nc_counties.csv
Output:  Health/data/processed/cdc_places_2024.ttl
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
EXO    = Namespace("http://purl.obolibrary.org/obo/ExO_")

DATA_YEAR = 2024
SRC_NODE  = BASE["dataset/CDC_PLACES_2024"]

# ---------------------------------------------------------------------------
# Indicator metadata:
#   col -> (label, unit, ontology_class, exposure_class)
#
#   ontology_class  : NCIT/ECTO term for the condition/measure itself
#                     emitted as  ind rdfs:subClassOf <class>
#   exposure_class  : ExO or ECTO term for the exposure category
#                     emitted as  ind ex:exposureClass <class>
# ---------------------------------------------------------------------------
INDICATORS = {
    # --- Chronic disease outcomes ---
    "arthritis_pct": (
        "Arthritis among Adults", "%",
        NCIT["C26882"],          # Arthritis
        EXO["0000002"],          # biological/health outcome
    ),
    "high_blood_pressure_pct": (
        "High Blood Pressure among Adults", "%",
        NCIT["C3117"],           # Hypertension
        EXO["0000002"],
    ),
    "cancer_pct": (
        "Cancer (excl. skin) among Adults", "%",
        NCIT["C9305"],           # Cancer
        EXO["0000002"],
    ),
    "asthma_pct": (
        "Current Asthma among Adults", "%",
        NCIT["C28397"],          # Asthma
        EXO["0000113"],          # air pollution exposure (asthma strongly linked)
    ),
    "coronary_heart_disease_pct": (
        "Coronary Heart Disease among Adults", "%",
        NCIT["C26732"],          # Coronary Heart Disease
        EXO["0000002"],
    ),
    "copd_pct": (
        "COPD among Adults", "%",
        NCIT["C3199"],           # COPD
        EXO["0000113"],          # air pollution exposure (COPD linked)
    ),
    "depression_pct": (
        "Depression among Adults", "%",
        NCIT["C2981"],           # Depression
        EXO["0000089"],          # socioeconomic exposure
    ),
    "diabetes_pct": (
        "Diabetes among Adults", "%",
        NCIT["C2985"],           # Diabetes Mellitus
        EXO["0000083"],          # body weight/metabolic exposure
    ),
    "high_cholesterol_pct": (
        "High Cholesterol among Adults (screened)", "%",
        NCIT["C34707"],          # Hypercholesterolemia
        EXO["0000083"],
    ),
    "obesity_pct": (
        "Obesity among Adults", "%",
        NCIT["C3283"],           # Obesity
        EXO["0000083"],
    ),
    "stroke_pct": (
        "Stroke among Adults", "%",
        NCIT["C3390"],           # Stroke
        EXO["0000002"],
    ),
    "teeth_lost_pct": (
        "All Teeth Lost among Adults 65+", "%",
        NCIT["C26786"],          # Dental Caries / Tooth Loss
        EXO["0000088"],          # diet/nutrition exposure
    ),
    "kidney_disease_pct": (
        "Chronic Kidney Disease among Adults", "%",
        NCIT["C26767"],          # Chronic Kidney Disease
        EXO["0000002"],
    ),

    # --- Health behaviours ---
    "binge_drinking_pct": (
        "Binge Drinking among Adults", "%",
        NCIT["C154476"],         # Alcohol Use Disorder
        EXO["0000086"],          # alcohol exposure
    ),
    "current_smoking_pct": (
        "Current Smoking among Adults", "%",
        NCIT["C68817"],          # Tobacco Use Disorder
        EXO["0000087"],          # tobacco smoke exposure
    ),
    "physical_inactivity_pct": (
        "No Leisure-Time Physical Activity", "%",
        NCIT["C68620"],          # Physical Inactivity
        EXO["0000085"],          # physical activity exposure
    ),
    "short_sleep_pct": (
        "Short Sleep Duration (<7 hrs)", "%",
        NCIT["C60540"],          # Sleep Disorder
        EXO["0000084"],          # behavioral exposure
    ),

    # --- Preventive care / screenings ---
    "annual_checkup_pct": (
        "Annual Checkup among Adults", "%",
        NCIT["C17481"],          # Screening/Preventive Care
        ECTO["0000098"],         # healthcare access exposure
    ),
    "cholesterol_screen_pct": (
        "Cholesterol Screening among Adults", "%",
        NCIT["C17481"],
        ECTO["0000098"],
    ),
    "colorectal_screen_pct": (
        "Colorectal Cancer Screening (ages 45-75)", "%",
        NCIT["C17481"],
        ECTO["0000098"],
    ),
    "mammography_pct": (
        "Mammography Use among Women 50-74", "%",
        NCIT["C17481"],
        ECTO["0000098"],
    ),
    "dental_visit_pct": (
        "Dental Visit in Past Year", "%",
        NCIT["C17481"],
        ECTO["0000098"],
    ),

    # --- Disability ---
    "hearing_disability_pct": (
        "Hearing Disability among Adults", "%",
        NCIT["C26696"],          # Hearing Impairment
        EXO["0000002"],
    ),
    "vision_disability_pct": (
        "Vision Disability among Adults", "%",
        NCIT["C26711"],          # Vision Impairment
        EXO["0000002"],
    ),
    "cognitive_disability_pct": (
        "Cognitive Disability among Adults", "%",
        NCIT["C26725"],          # Cognitive Impairment
        EXO["0000002"],
    ),
    "mobility_disability_pct": (
        "Mobility Disability among Adults", "%",
        NCIT["C26714"],          # Mobility Impairment
        EXO["0000002"],
    ),
    "selfcare_disability_pct": (
        "Self-Care Disability among Adults", "%",
        NCIT["C21007"],          # Disability
        EXO["0000002"],
    ),

    # --- Insurance / access ---
    "no_health_insurance_pct": (
        "No Health Insurance among Adults 18-64", "%",
        ECTO["0000098"],         # healthcare access exposure
        EXO["0000089"],          # socioeconomic exposure
    ),
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
    g.bind("exo",    EXO)
    g.bind("xsd",    XSD)

    # Provenance dataset node
    g.add((SRC_NODE, RDF.type,                PROV.Entity))
    g.add((SRC_NODE, SCHEMA.name,             Literal("CDC PLACES: Local Data for Better Health, County Data 2024")))
    g.add((SRC_NODE, SCHEMA.publisher,        Literal("Centers for Disease Control and Prevention (CDC)")))
    g.add((SRC_NODE, SCHEMA.temporalCoverage, Literal("2024")))

    # Declare indicator nodes with full ontology annotations
    for col, (label, unit, ont_class, exp_class) in INDICATORS.items():
        ind = BASE[f"indicator/{col}"]
        g.add((ind, RDF.type,           QB.MeasureProperty))
        g.add((ind, RDFS.label,         Literal(label)))
        g.add((ind, SCHEMA.unitText,    Literal(unit)))
        if ont_class is not None:
            g.add((ind, RDFS.subClassOf, ont_class))
        if exp_class is not None:
            g.add((ind, BASE["exposureClass"], exp_class))

    # One Observation per (county, indicator) pair
    for _, row in df.iterrows():
        fips   = str(row["fips"]).zfill(5)
        county = BASE[f"county/{fips}"]

        for col, (label, unit, _, _) in INDICATORS.items():
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
