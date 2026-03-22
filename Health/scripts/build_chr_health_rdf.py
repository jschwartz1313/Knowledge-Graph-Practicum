"""
build_chr_health_rdf.py
Converts chr_2025_nc_expanded.csv into RDF triples (Turtle) following the
same SOSA + PROV-O + schema.org + RDF-Data-Cube pattern used by the
environmental module (90_build_environment_rdf.py).

Each indicator node is typed against:
  - Its condition/outcome class in NCIT or ECTO (rdfs:subClassOf)
  - Its ExO exposure class (ex:exposureClass) where applicable

Input:   Health/data/processed/chr_2025_nc_expanded.csv
Output:  Health/data/processed/chr_health_2025.ttl
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
ENVO   = Namespace("http://purl.obolibrary.org/obo/ENVO_")

DATA_YEAR = 2025
SRC_NODE  = BASE["dataset/CHR_2025_NC"]

# ---------------------------------------------------------------------------
# Indicator metadata:
#   col -> (label, unit, ontology_class, exposure_class)
#
#   ontology_class  : NCIT/ECTO/ENVO term for the condition/measure itself
#                     emitted as  ind rdfs:subClassOf <class>
#   exposure_class  : ExO term for the exposure category
#                     emitted as  ind ex:exposureClass <class>
#
# Ontology key:
#   NCIT  http://purl.obolibrary.org/obo/NCIT_
#   ECTO  http://purl.obolibrary.org/obo/ECTO_
#   EXO   http://purl.obolibrary.org/obo/ExO_
#   ENVO  http://purl.obolibrary.org/obo/ENVO_
# ---------------------------------------------------------------------------
INDICATORS = {
    # --- Mortality / life span ---
    "life_expectancy": (
        "Life Expectancy", "years",
        NCIT["C25150"],          # Life Expectancy
        EXO["0000002"],          # biological/health outcome
    ),
    "ypll_rate": (
        "Years of Potential Life Lost Rate", "per 100k",
        NCIT["C25513"],          # Premature Death
        EXO["0000002"],
    ),
    "premature_age_adj_mortality": (
        "Premature Age-Adjusted Mortality Rate", "per 100k",
        NCIT["C25513"],
        EXO["0000002"],
    ),
    "child_mortality_rate": (
        "Child Mortality Rate", "per 100k",
        NCIT["C25513"],
        EXO["0000002"],
    ),
    "infant_mortality_rate": (
        "Infant Mortality Rate", "per 1k births",
        NCIT["C26747"],          # Low Birth Weight / perinatal; closest NCIT for infant mortality
        EXO["0000002"],
    ),
    "injury_death_rate": (
        "Injury Death Rate", "per 100k",
        NCIT["C25488"],          # Injury
        EXO["0000002"],
    ),
    "suicide_rate": (
        "Suicide Rate (Age-Adjusted)", "per 100k",
        NCIT["C25280"],          # Suicide
        EXO["0000084"],          # behavioral exposure
    ),
    "homicide_rate": (
        "Homicide Rate", "per 100k",
        NCIT["C25251"],          # Homicide
        EXO["0000002"],
    ),
    "motor_vehicle_mortality_rate": (
        "Motor Vehicle Mortality Rate", "per 100k",
        NCIT["C25488"],          # Injury
        EXO["0000090"],          # built environment exposure
    ),
    "firearm_fatality_rate": (
        "Firearm Fatality Rate", "per 100k",
        NCIT["C25488"],
        EXO["0000002"],
    ),
    "drug_overdose_mortality_rate": (
        "Drug Overdose Mortality Rate", "per 100k",
        NCIT["C25280"],          # Suicide/self-harm; also covers OD deaths
        EXO["0000087"],          # drug/substance exposure
    ),

    # --- Health outcomes / prevalence ---
    "low_birth_weight_pct": (
        "Low Birth Weight", "%",
        NCIT["C26747"],          # Low Birth Weight
        EXO["0000002"],
    ),
    "poor_or_fair_health_pct": (
        "Poor or Fair Health", "%",
        NCIT["C17047"],          # Health Status
        EXO["0000002"],
    ),
    "frequent_physical_distress_pct": (
        "Frequent Physical Distress", "%",
        NCIT["C19332"],          # Physical Health
        EXO["0000002"],
    ),
    "frequent_mental_distress_pct": (
        "Frequent Mental Distress", "%",
        NCIT["C14215"],          # Mental Health
        EXO["0000002"],
    ),
    "diabetes_prevalence_pct": (
        "Diabetes Prevalence", "%",
        NCIT["C2985"],           # Diabetes Mellitus
        EXO["0000083"],          # metabolic/body weight exposure
    ),
    "hiv_prevalence_rate": (
        "HIV Prevalence Rate", "per 100k",
        NCIT["C14219"],          # HIV Infection
        EXO["0000002"],
    ),
    "obesity_prevalence_pct": (
        "Adult Obesity Prevalence", "%",
        NCIT["C3283"],           # Obesity
        EXO["0000083"],          # body weight exposure
    ),
    "teen_birth_rate": (
        "Teen Birth Rate", "per 1k females 15-19",
        NCIT["C17600"],          # Adolescent Health
        EXO["0000089"],          # socioeconomic exposure
    ),
    "chlamydia_rate": (
        "Chlamydia Rate", "per 100k",
        NCIT["C26926"],          # Chlamydia Infection
        EXO["0000002"],
    ),

    # --- Health behaviours ---
    "adult_smoking_pct": (
        "Adult Smoking", "%",
        NCIT["C68817"],          # Tobacco Use Disorder
        EXO["0000087"],          # tobacco smoke exposure
    ),
    "physical_inactivity_pct": (
        "Physical Inactivity", "%",
        NCIT["C68620"],          # Physical Inactivity
        EXO["0000085"],          # physical activity exposure
    ),
    "excessive_drinking_pct": (
        "Excessive Drinking", "%",
        NCIT["C154476"],         # Alcohol Use Disorder
        EXO["0000086"],          # alcohol exposure
    ),
    "insufficient_sleep_pct": (
        "Insufficient Sleep", "%",
        NCIT["C60540"],          # Sleep Disorder
        EXO["0000084"],          # behavioral exposure
    ),

    # --- Health access ---
    "primary_care_rate": (
        "Primary Care Physicians Rate", "per 100k",
        NCIT["C17480"],          # Health Care Provider
        ECTO["0000098"],         # healthcare access exposure (used as exposure_class)
    ),
    "mental_health_provider_rate": (
        "Mental Health Provider Rate", "per 100k",
        NCIT["C17480"],
        ECTO["0000098"],
    ),
    "preventable_hosp_rate": (
        "Preventable Hospitalization Rate", "per 100k Medicare",
        NCIT["C25218"],          # Hospitalization
        ECTO["0000098"],
    ),
    "mammography_pct": (
        "Mammography Screening", "%",
        NCIT["C17481"],          # Screening
        ECTO["0000098"],
    ),
    "flu_vaccinations_pct": (
        "Flu Vaccinations", "%",
        NCIT["C17481"],
        ECTO["0000098"],
    ),
    "access_exercise_pct": (
        "Access to Exercise Opportunities", "%",
        ENVO["01000739"],        # recreational/built environment
        EXO["0000090"],          # built environment exposure
    ),

    # --- Social determinants ---
    "food_environment_index": (
        "Food Environment Index", "0-10",
        ECTO["0000088"],         # diet/nutrition exposure
        EXO["0000088"],          # diet exposure
    ),
    "food_insecurity_pct": (
        "Food Insecurity", "%",
        ECTO["0000088"],
        EXO["0000088"],
    ),
    "loneliness_pct": (
        "Feelings of Loneliness", "%",
        ECTO["0001105"],         # social isolation exposure
        EXO["0000089"],          # socioeconomic exposure
    ),
    "severe_housing_pct": (
        "Severe Housing Problems", "%",
        ECTO["0001236"],         # housing instability exposure
        EXO["0000090"],          # built environment exposure
    ),
    "income_ratio": (
        "Income Inequality Ratio (80/20)", "ratio",
        ECTO["0000090"],         # income-related exposure
        EXO["0000089"],
    ),
    "uninsured_adults_pct": (
        "Uninsured Adults", "%",
        ECTO["0000098"],         # healthcare access exposure
        EXO["0000089"],
    ),
    "uninsured_children_pct": (
        "Uninsured Children", "%",
        ECTO["0000098"],
        EXO["0000089"],
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
    g.bind("envo",   ENVO)
    g.bind("xsd",    XSD)

    # Declare provenance dataset node
    g.add((SRC_NODE, RDF.type, PROV.Entity))
    g.add((SRC_NODE, SCHEMA.name, Literal("County Health Rankings 2025 North Carolina")))
    g.add((SRC_NODE, SCHEMA.publisher, Literal("University of Wisconsin Population Health Institute")))
    g.add((SRC_NODE, SCHEMA.temporalCoverage, Literal("2025")))

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

    # Emit one Observation per (county, indicator) pair
    for _, row in df.iterrows():
        fips   = str(row["fips"]).zfill(5)
        county = BASE[f"county/{fips}"]

        for col, (label, unit, _, _) in INDICATORS.items():
            val = row.get(col)
            if pd.isna(val):
                continue
            ind = BASE[f"indicator/{col}"]
            obs = BASE[f"obs/{col}/{fips}/{DATA_YEAR}"]

            g.add((obs, RDF.type,                    SOSA.Observation))
            g.add((obs, RDF.type,                    QB.Observation))
            g.add((obs, SOSA.hasFeatureOfInterest,   county))
            g.add((obs, SOSA.observedProperty,       ind))
            g.add((obs, SOSA.resultTime,             Literal(f"{DATA_YEAR}-12-31", datatype=XSD.date)))
            g.add((obs, SOSA.hasSimpleResult,        Literal(float(val), datatype=XSD.float)))
            g.add((obs, SCHEMA.location,             county))
            g.add((obs, BASE["measuredIndicator"],   ind))
            g.add((obs, SCHEMA.value,                Literal(float(val), datatype=XSD.float)))
            g.add((obs, SCHEMA.unitText,             Literal(unit)))
            g.add((obs, SCHEMA.temporal,             Literal(str(DATA_YEAR), datatype=XSD.gYear)))
            g.add((obs, PROV.wasDerivedFrom,         SRC_NODE))
            g.add((obs, QB.dataSet,                  BASE["nc_exposome_dataset"]))

    return g


def main():
    processed = Path(__file__).parent.parent / "data" / "processed"
    in_path  = processed / "chr_2025_nc_expanded.csv"
    out_path = processed / "chr_health_2025.ttl"

    df = pd.read_csv(in_path, dtype={"fips": str})
    print(f"Loaded {len(df)} counties from {in_path.name}")

    g = build_graph(df)
    g.serialize(str(out_path), format="turtle")
    print(f"Wrote {len(g):,} triples → {out_path}")


if __name__ == "__main__":
    main()
