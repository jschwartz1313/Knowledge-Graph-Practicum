"""
build_chr_health_rdf.py
Converts chr_2025_nc_expanded.csv into RDF triples (Turtle) following the
same SOSA + PROV-O + schema.org + RDF-Data-Cube pattern used by the
environmental module (90_build_environment_rdf.py).

Input:   Socioeconomic/chr_2025_nc_expanded.csv
Output:  Socioeconomic/chr_health_2025.ttl
"""

from pathlib import Path
import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, XSD

BASE  = Namespace("http://example.org/nc-exposome/")
SOSA  = Namespace("http://www.w3.org/ns/sosa#")
PROV  = Namespace("http://www.w3.org/ns/prov#")
QB    = Namespace("http://purl.org/linked-data/cube#")
SCHEMA = Namespace("http://schema.org/")
RDFS  = Namespace("http://www.w3.org/2000/01/rdf-schema#")
NCIT  = Namespace("http://purl.obolibrary.org/obo/NCIT_")
ECTO  = Namespace("http://purl.obolibrary.org/obo/ECTO_")

DATA_YEAR = 2025
SRC_NODE  = BASE["dataset/CHR_2025_NC"]

# ---------------------------------------------------------------------------
# Indicator metadata: output_col -> (label, unit, ontology_type)
# ontology_type = None if no mapping available
# ---------------------------------------------------------------------------
INDICATORS = {
    # Mortality / life span
    "life_expectancy":               ("Life Expectancy",                      "years",         None),
    "ypll_rate":                     ("Years of Potential Life Lost Rate",     "per 100k",      None),
    "premature_age_adj_mortality":   ("Premature Age-Adjusted Mortality Rate", "per 100k",      None),
    "child_mortality_rate":          ("Child Mortality Rate",                  "per 100k",      None),
    "infant_mortality_rate":         ("Infant Mortality Rate",                 "per 1k births", None),
    "injury_death_rate":             ("Injury Death Rate",                     "per 100k",      None),
    "suicide_rate":                  ("Suicide Rate (Age-Adjusted)",           "per 100k",      None),
    "homicide_rate":                 ("Homicide Rate",                         "per 100k",      None),
    "motor_vehicle_mortality_rate":  ("Motor Vehicle Mortality Rate",          "per 100k",      None),
    "firearm_fatality_rate":         ("Firearm Fatality Rate",                 "per 100k",      None),
    "drug_overdose_mortality_rate":  ("Drug Overdose Mortality Rate",          "per 100k",      None),
    # Health outcomes / prevalence
    "low_birth_weight_pct":          ("Low Birth Weight",                      "%",             None),
    "poor_or_fair_health_pct":       ("Poor or Fair Health",                   "%",             None),
    "frequent_physical_distress_pct":("Frequent Physical Distress",            "%",             None),
    "frequent_mental_distress_pct":  ("Frequent Mental Distress",              "%",             None),
    "diabetes_prevalence_pct":       ("Diabetes Prevalence",                   "%",             NCIT["C2985"]),
    "hiv_prevalence_rate":           ("HIV Prevalence Rate",                   "per 100k",      None),
    "obesity_prevalence_pct":        ("Adult Obesity Prevalence",              "%",             NCIT["C3283"]),
    "teen_birth_rate":               ("Teen Birth Rate",                       "per 1k females 15-19", None),
    "chlamydia_rate":                ("Chlamydia Rate",                        "per 100k",      None),
    # Health behaviours
    "adult_smoking_pct":             ("Adult Smoking",                         "%",             None),
    "physical_inactivity_pct":       ("Physical Inactivity",                   "%",             None),
    "excessive_drinking_pct":        ("Excessive Drinking",                    "%",             None),
    "insufficient_sleep_pct":        ("Insufficient Sleep",                    "%",             None),
    # Health access
    "primary_care_rate":             ("Primary Care Physicians Rate",          "per 100k",      None),
    "mental_health_provider_rate":   ("Mental Health Provider Rate",           "per 100k",      None),
    "preventable_hosp_rate":         ("Preventable Hospitalization Rate",      "per 100k Medicare", None),
    "mammography_pct":               ("Mammography Screening",                 "%",             None),
    "flu_vaccinations_pct":          ("Flu Vaccinations",                      "%",             None),
    "access_exercise_pct":           ("Access to Exercise Opportunities",      "%",             None),
    # Social determinants
    "food_environment_index":        ("Food Environment Index",                "0-10",          ECTO["0000095"]),
    "food_insecurity_pct":           ("Food Insecurity",                       "%",             ECTO["0000095"]),
    "loneliness_pct":                ("Feelings of Loneliness",                "%",             None),
    "severe_housing_pct":            ("Severe Housing Problems",               "%",             None),
    "income_ratio":                  ("Income Inequality Ratio (80/20)",       "ratio",         ECTO["0000090"]),
    "uninsured_adults_pct":          ("Uninsured Adults",                      "%",             None),
    "uninsured_children_pct":        ("Uninsured Children",                    "%",             None),
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

    # Declare provenance dataset node
    g.add((SRC_NODE, RDF.type, PROV.Entity))
    g.add((SRC_NODE, SCHEMA.name, Literal("County Health Rankings 2025 North Carolina")))
    g.add((SRC_NODE, SCHEMA.publisher, Literal("University of Wisconsin Population Health Institute")))
    g.add((SRC_NODE, SCHEMA.temporalCoverage, Literal("2025")))

    # Declare indicator nodes
    for col, (label, unit, ont) in INDICATORS.items():
        ind = BASE[f"indicator/{col}"]
        g.add((ind, RDF.type, QB.MeasureProperty))
        g.add((ind, RDFS.label, Literal(label)))
        g.add((ind, SCHEMA.unitText, Literal(unit)))
        if ont:
            g.add((ind, RDFS.subClassOf, ont))

    # Emit one Observation per (county, indicator) pair
    for _, row in df.iterrows():
        fips   = str(row["fips"]).zfill(5)
        county = BASE[f"county/{fips}"]

        for col, (label, unit, _) in INDICATORS.items():
            val = row.get(col)
            if pd.isna(val):
                continue
            ind = BASE[f"indicator/{col}"]
            obs = BASE[f"obs/{col}/{fips}/{DATA_YEAR}"]

            # Core SOSA triple pattern
            g.add((obs, RDF.type,                    SOSA.Observation))
            g.add((obs, RDF.type,                    QB.Observation))
            g.add((obs, SOSA.hasFeatureOfInterest,   county))
            g.add((obs, SOSA.observedProperty,       ind))
            g.add((obs, SOSA.resultTime,             Literal(f"{DATA_YEAR}-12-31", datatype=XSD.date)))
            g.add((obs, SOSA.hasSimpleResult,        Literal(float(val), datatype=XSD.float)))
            # schema.org aliases (for SPARQL compatibility with existing examples)
            g.add((obs, SCHEMA.location,             county))
            g.add((obs, BASE["measuredIndicator"],   ind))
            g.add((obs, SCHEMA.value,                Literal(float(val), datatype=XSD.float)))
            g.add((obs, SCHEMA.unitText,             Literal(unit)))
            g.add((obs, SCHEMA.temporal,             Literal(str(DATA_YEAR), datatype=XSD.gYear)))
            # Provenance
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

    triple_count = len(g)
    print(f"Wrote {triple_count:,} triples → {out_path}")


if __name__ == "__main__":
    main()
