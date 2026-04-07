"""
Generate poster-ready visualizations for NC Exposome Knowledge Graph.
Outputs high-resolution PNGs suitable for academic poster printing.

Usage:
    pip install matplotlib seaborn pandas numpy
    python tools/generate_poster_figures.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import seaborn as sns
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "poster_figures"
OUT.mkdir(exist_ok=True)

# ── load data ────────────────────────────────────────────────────────────
se   = pd.read_csv(ROOT / "Socioeconomic/nc_exposome_data.csv")
env  = pd.read_csv(ROOT / "Environmental_GDB_NPDES/data/processed/county_environment_2024.csv")
hlth = pd.read_csv(ROOT / "Health/data/processed/cdc_places_nc_counties.csv")
chr_ = pd.read_csv(ROOT / "Health/data/processed/chr_2025_nc_expanded.csv")

# ── color palette ────────────────────────────────────────────────────────
C_ENV    = "#2ecc71"   # green
C_HEALTH = "#e74c3c"   # red
C_SOCIO  = "#3498db"   # blue
C_META   = "#9b59b6"   # purple
C_BG     = "#fafafa"
FONT     = "sans-serif"

plt.rcParams.update({
    "font.family": FONT,
    "font.size": 12,
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 13,
    "figure.facecolor": C_BG,
    "axes.facecolor": "white",
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.3,
})


# =========================================================================
# FIGURE 1 — KG Architecture / Data Pipeline Diagram
# =========================================================================
def fig_architecture():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    def box(x, y, w, h, text, color, fontsize=11, alpha=0.85):
        rect = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.15",
                              facecolor=color, edgecolor="grey",
                              alpha=alpha, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color="white",
                wrap=True)

    def arrow(x1, y1, x2, y2, color="grey"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                    lw=2, connectionstyle="arc3,rad=0.0"))

    # ── Title ──
    ax.text(7, 7.5, "NC Exposome Knowledge Graph — Data Pipeline",
            ha="center", va="center", fontsize=20, fontweight="bold",
            color="#2c3e50")

    # ── Layer 1: Data Sources ──
    ax.text(1.8, 6.7, "Data Sources", fontsize=13, fontweight="bold",
            color="#7f8c8d", ha="center")
    box(0.2, 5.6, 3.2, 0.9, "EJScreen v23\nNC DEQ\nNOAA NCEI", C_ENV)
    box(0.2, 4.4, 3.2, 0.9, "CDC PLACES 2024\nCHR 2025", C_HEALTH)
    box(0.2, 3.2, 3.2, 0.9, "US Census 2022\nCHR Demographics", C_SOCIO)

    # ── Layer 2: Processing Modules ──
    ax.text(5.8, 6.7, "Processing Modules", fontsize=13, fontweight="bold",
            color="#7f8c8d", ha="center")
    box(4.2, 5.6, 3.2, 0.9, "Environmental\n~2,000 triples", C_ENV)
    box(4.2, 4.4, 3.2, 0.9, "Health\n~81,000 triples", C_HEALTH)
    box(4.2, 3.2, 3.2, 0.9, "Socioeconomic\n~15,000 triples", C_SOCIO)

    # ── Arrows: Sources → Modules ──
    for y in [6.05, 4.85, 3.65]:
        arrow(3.4, y, 4.2, y)

    # ── Layer 3: Unified KG ──
    box(8.2, 3.8, 2.6, 2.2,
        "Unified\nRDF Graph\n\n~98,000\ntriples\n100 counties",
        "#34495e", fontsize=12)

    # ── Arrows: Modules → Unified ──
    arrow(7.4, 6.05, 8.2, 5.6)
    arrow(7.4, 4.85, 8.2, 4.9)
    arrow(7.4, 3.65, 8.2, 4.2)

    # ── Layer 4: Ontologies ──
    ax.text(9.5, 2.6, "Ontology Annotations", fontsize=11,
            fontweight="bold", color="#7f8c8d", ha="center")
    ontos = ["SOSA/SSN", "PROV-O", "RDF Data Cube",
             "ExO / ECTO", "ENVO / NCIT"]
    for i, o in enumerate(ontos):
        ax.text(8.3 + (i % 3) * 1.5, 2.1 - (i // 3) * 0.5, o,
                fontsize=9, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#ecf0f1",
                          edgecolor="#bdc3c7", linewidth=1))

    # ── Layer 5: Outputs ──
    box(11.6, 5.2, 2.0, 1.0, "SPARQL\nEndpoint", "#8e44ad", fontsize=11)
    box(11.6, 3.8, 2.0, 1.0, "ROBOKOP\nSubmission", "#e67e22", fontsize=11)
    box(11.6, 2.4, 2.0, 1.0, "Poster\nVisualization", "#16a085", fontsize=11)

    arrow(10.8, 5.5, 11.6, 5.7)
    arrow(10.8, 4.9, 11.6, 4.3)
    arrow(10.8, 4.3, 11.6, 2.9)

    fig.savefig(OUT / "fig1_architecture.png")
    plt.close(fig)
    print("  [1/6] Architecture diagram saved")


# =========================================================================
# FIGURE 2 — Correlation Heatmap across Key Indicators
# =========================================================================
def fig_correlation_heatmap():
    # merge socioeconomic + env
    merged = se.copy()
    env_cols = ["fips", "pm25_mean", "ozone_8hr_avg", "impaired_stream_miles",
                "npdes_permits_count", "avg_temp_f", "annual_precip_in"]
    env_sub = env[[c for c in env_cols if c in env.columns]].copy()
    if "fips" in env_sub.columns:
        merged = merged.merge(env_sub, on="fips", how="left")

    # pick interesting columns
    cols = [c for c in [
        "poverty_rate", "median_income", "unemployment_rate",
        "education_bachelor_pct", "uninsured_pct",
        "obesity_pct", "diabetes_pct", "physical_inactivity_pct",
        "mental_health_days", "excessive_drinking_pct",
        "pm25", "pm25_mean",
    ] if c in merged.columns]

    rename = {
        "poverty_rate": "Poverty Rate",
        "median_income": "Median Income",
        "unemployment_rate": "Unemployment",
        "education_bachelor_pct": "Bachelor's Degree %",
        "uninsured_pct": "Uninsured %",
        "obesity_pct": "Obesity %",
        "diabetes_pct": "Diabetes %",
        "physical_inactivity_pct": "Physical Inactivity %",
        "mental_health_days": "Mental Health Days",
        "excessive_drinking_pct": "Excessive Drinking %",
        "pm25": "PM2.5 (SE)",
        "pm25_mean": "PM2.5 (Env)",
    }

    sub = merged[cols].rename(columns=rename).dropna(axis=1, how="all")
    corr = sub.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    sns.heatmap(corr, mask=mask, cmap=cmap, center=0,
                square=True, linewidths=0.8,
                annot=True, fmt=".2f", annot_kws={"size": 9},
                cbar_kws={"shrink": 0.75, "label": "Pearson r"}, ax=ax)
    ax.set_title("Cross-Domain Indicator Correlations\n(100 NC Counties)",
                 pad=15)
    fig.savefig(OUT / "fig2_correlation_heatmap.png")
    plt.close(fig)
    print("  [2/6] Correlation heatmap saved")


# =========================================================================
# FIGURE 3 — Top/Bottom Counties by Composite Risk Score
# =========================================================================
def fig_risk_ranking():
    df = se.copy()
    # z-score normalize risk indicators (higher = worse)
    risk_cols = ["poverty_rate", "obesity_pct", "diabetes_pct",
                 "physical_inactivity_pct", "uninsured_pct",
                 "mental_health_days"]
    risk_cols = [c for c in risk_cols if c in df.columns]

    for c in risk_cols:
        mu, sd = df[c].mean(), df[c].std()
        df[f"z_{c}"] = (df[c] - mu) / sd

    z_cols = [f"z_{c}" for c in risk_cols]
    df["risk_score"] = df[z_cols].mean(axis=1)
    df = df.sort_values("risk_score", ascending=False)

    top10 = df.head(10)
    bot10 = df.tail(10).iloc[::-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=False)

    # Highest risk
    colors_top = [C_HEALTH] * 10
    ax1.barh(top10["county"], top10["risk_score"], color=colors_top,
             edgecolor="white", linewidth=0.5)
    ax1.set_xlabel("Composite Risk Score (z-score)")
    ax1.set_title("10 Highest-Risk Counties", color=C_HEALTH)
    ax1.invert_yaxis()

    # Lowest risk
    colors_bot = [C_ENV] * 10
    ax2.barh(bot10["county"], bot10["risk_score"], color=colors_bot,
             edgecolor="white", linewidth=0.5)
    ax2.set_xlabel("Composite Risk Score (z-score)")
    ax2.set_title("10 Lowest-Risk Counties", color="#27ae60")
    ax2.invert_yaxis()

    fig.suptitle("County Health-Risk Ranking\n(Poverty, Obesity, Diabetes, "
                 "Inactivity, Uninsured, Mental Health)",
                 fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_risk_ranking.png")
    plt.close(fig)
    print("  [3/6] Risk ranking saved")


# =========================================================================
# FIGURE 4 — Scatter: Poverty vs Diabetes (colored by Obesity)
# =========================================================================
def fig_poverty_diabetes_scatter():
    df = se.dropna(subset=["poverty_rate", "diabetes_pct", "obesity_pct"])

    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(df["poverty_rate"], df["diabetes_pct"],
                    c=df["obesity_pct"], cmap="YlOrRd", s=80,
                    edgecolors="grey", linewidth=0.5, alpha=0.85)
    cbar = plt.colorbar(sc, ax=ax, shrink=0.8)
    cbar.set_label("Obesity Prevalence (%)", fontsize=12)

    # trend line
    z = np.polyfit(df["poverty_rate"], df["diabetes_pct"], 1)
    xs = np.linspace(df["poverty_rate"].min(), df["poverty_rate"].max(), 100)
    ax.plot(xs, np.polyval(z, xs), "--", color="grey", linewidth=1.5,
            label=f"Linear fit (slope={z[0]:.2f})")

    # label a few extreme counties
    for _, row in df.nlargest(3, "diabetes_pct").iterrows():
        ax.annotate(row["county"],
                    (row["poverty_rate"], row["diabetes_pct"]),
                    fontsize=8, ha="left", xytext=(5, 5),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              alpha=0.7))
    for _, row in df.nsmallest(3, "diabetes_pct").iterrows():
        ax.annotate(row["county"],
                    (row["poverty_rate"], row["diabetes_pct"]),
                    fontsize=8, ha="left", xytext=(5, -10),
                    textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white",
                              alpha=0.7))

    r = df["poverty_rate"].corr(df["diabetes_pct"])
    ax.text(0.05, 0.95, f"Pearson r = {r:.3f}",
            transform=ax.transAxes, fontsize=12,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    ax.set_xlabel("Poverty Rate (%)")
    ax.set_ylabel("Diabetes Prevalence (%)")
    ax.set_title("Socioeconomic–Health Pathway:\nPoverty Rate vs Diabetes "
                 "Prevalence (colored by Obesity)")
    ax.legend(loc="lower right")
    fig.savefig(OUT / "fig4_poverty_diabetes.png")
    plt.close(fig)
    print("  [4/6] Poverty-diabetes scatter saved")


# =========================================================================
# FIGURE 5 — Ontology Mapping Overview (Sankey-like diagram)
# =========================================================================
def fig_ontology_map():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(7, 9.5, "Ontology Mapping Architecture",
            ha="center", fontsize=20, fontweight="bold", color="#2c3e50")

    # ── Column 1: Domains ──
    domains = [
        ("Environmental\nIndicators", C_ENV, ["PM2.5", "Ozone", "RSEI Toxic",
         "Impaired Waters", "NPDES Permits", "Avg Temp", "Precipitation"]),
        ("Health\nOutcomes", C_HEALTH, ["Obesity", "Diabetes", "Asthma",
         "Depression", "COPD", "Heart Disease", "Stroke"]),
        ("Socioeconomic\nFactors", C_SOCIO, ["Poverty Rate", "Median Income",
         "Unemployment", "Education", "Uninsured", "Child Poverty"]),
    ]

    y_start = 8.2
    for i, (title, color, items) in enumerate(domains):
        y = y_start - i * 2.8
        rect = FancyBboxPatch((0.3, y - 0.9), 3.0, 2.0,
                              boxstyle="round,pad=0.15",
                              facecolor=color, alpha=0.15,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(1.8, y + 0.85, title, ha="center", fontsize=12,
                fontweight="bold", color=color)
        for j, item in enumerate(items):
            ax.text(1.8, y + 0.4 - j * 0.28, f"  {item}", fontsize=8,
                    ha="center", color="#2c3e50")

    # ── Column 2: RDF Representation ──
    ax.text(5.8, 8.8, "RDF Pattern", fontsize=13, fontweight="bold",
            color="#7f8c8d", ha="center")
    rdf_box = FancyBboxPatch((4.3, 3.5), 3.0, 5.0,
                             boxstyle="round,pad=0.2",
                             facecolor="#ecf0f1", edgecolor="#bdc3c7",
                             linewidth=1.5)
    ax.add_patch(rdf_box)
    rdf_lines = [
        ("sosa:Observation", "#2c3e50", True),
        ("", "", False),
        ("  hasFeatureOfInterest", "#7f8c8d", False),
        ("    → ex:county/FIPS", C_SOCIO, False),
        ("", "", False),
        ("  observedProperty", "#7f8c8d", False),
        ("    → ex:indicator/*", "#e67e22", False),
        ("", "", False),
        ("  hasSimpleResult", "#7f8c8d", False),
        ("    → numeric value", "#2c3e50", False),
        ("", "", False),
        ("  prov:wasDerivedFrom", "#7f8c8d", False),
        ("    → ex:dataset/*", C_META, False),
        ("", "", False),
        ("  schema:temporal", "#7f8c8d", False),
        ("    → year", "#2c3e50", False),
    ]
    for j, (line, color, bold) in enumerate(rdf_lines):
        if not line:
            continue
        ax.text(4.6, 8.0 - j * 0.28, line, fontsize=8,
                fontfamily="monospace", color=color,
                fontweight="bold" if bold else "normal")

    # ── Arrows domain → RDF ──
    for y in [7.3, 4.9, 2.5]:
        ax.annotate("", xy=(4.3, 6.0), xytext=(3.3, y),
                    arrowprops=dict(arrowstyle="-|>", color="#bdc3c7",
                                    lw=1.5, connectionstyle="arc3,rad=0.1"))

    # ── Column 3: Ontologies ──
    ax.text(10.5, 8.8, "Ontology Classes", fontsize=13, fontweight="bold",
            color="#7f8c8d", ha="center")

    ontologies = [
        ("NCIT (NCI Thesaurus)", "#c0392b",
         ["C3283 Obesity", "C2985 Diabetes", "C26927 Asthma",
          "C14215 Mental Health"]),
        ("ECTO (Env. Conditions)", "#27ae60",
         ["0000460 PM2.5 Exposure", "0000095 Poverty Exposure",
          "0000090 Income Exposure"]),
        ("ExO (Exposure Ontology)", "#2980b9",
         ["0000113 Air Pollution", "0000089 Socioeconomic",
          "0000083 Obesity", "0000084 Behavioral"]),
        ("ENVO (Environment)", "#16a085",
         ["00002005 Air", "00000015 Water"]),
    ]

    y_pos = 8.2
    for title, color, items in ontologies:
        rect = FancyBboxPatch((8.5, y_pos - 0.2), 4.0,
                              0.4 + len(items) * 0.3,
                              boxstyle="round,pad=0.1",
                              facecolor=color, alpha=0.1,
                              edgecolor=color, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(10.5, y_pos + 0.05, title, fontsize=10,
                fontweight="bold", ha="center", color=color)
        for j, item in enumerate(items):
            ax.text(10.5, y_pos - 0.3 - j * 0.28, item, fontsize=8,
                    ha="center", color="#2c3e50")
        y_pos -= (0.7 + len(items) * 0.3)

    # ── Arrows RDF → Ontologies ──
    ax.annotate("", xy=(8.5, 6.5), xytext=(7.3, 6.0),
                arrowprops=dict(arrowstyle="-|>", color="#bdc3c7",
                                lw=1.5, connectionstyle="arc3,rad=0.05"))
    ax.text(7.6, 6.4, "rdfs:subClassOf\nex:exposureClass",
            fontsize=7, color="#7f8c8d", ha="center", style="italic")

    fig.savefig(OUT / "fig5_ontology_map.png")
    plt.close(fig)
    print("  [5/6] Ontology mapping diagram saved")


# =========================================================================
# FIGURE 6 — Summary Stats Infographic
# =========================================================================
def fig_summary_stats():
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(7, 4.6, "NC Exposome Knowledge Graph — At a Glance",
            ha="center", fontsize=20, fontweight="bold", color="#2c3e50")

    stats = [
        ("~98,000", "RDF Triples", "#2c3e50"),
        ("100", "NC Counties", C_SOCIO),
        ("80+", "Indicators", C_HEALTH),
        ("4", "Data Domains", C_ENV),
        ("8", "Ontologies\nUsed", C_META),
        ("6", "Data\nSources", "#e67e22"),
    ]

    for i, (num, label, color) in enumerate(stats):
        x = 1.2 + i * 2.1
        rect = FancyBboxPatch((x - 0.8, 0.8), 1.8, 3.0,
                              boxstyle="round,pad=0.2",
                              facecolor=color, alpha=0.08,
                              edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.1, 2.9, num, ha="center", va="center",
                fontsize=30, fontweight="bold", color=color)
        ax.text(x + 0.1, 1.6, label, ha="center", va="center",
                fontsize=12, color="#2c3e50", fontweight="bold")

    # ── Bottom bar: tech stack ──
    ax.text(7, 0.35, "Python  |  rdflib  |  SOSA/SSN  |  PROV-O  |  "
            "RDF Data Cube  |  ExO / ECTO / ENVO / NCIT  |  SPARQL",
            ha="center", fontsize=10, color="#95a5a6",
            style="italic")

    fig.savefig(OUT / "fig6_summary_stats.png")
    plt.close(fig)
    print("  [6/6] Summary stats infographic saved")


# =========================================================================
# RUN ALL
# =========================================================================
if __name__ == "__main__":
    print(f"Saving poster figures to: {OUT}/\n")
    fig_architecture()
    fig_correlation_heatmap()
    fig_risk_ranking()
    fig_poverty_diabetes_scatter()
    fig_ontology_map()
    fig_summary_stats()
    print(f"\nDone! All 6 figures saved to {OUT}/")
    print("  fig1_architecture.png     — KG data pipeline diagram")
    print("  fig2_correlation_heatmap.png — Cross-domain correlations")
    print("  fig3_risk_ranking.png     — Top/bottom risk counties")
    print("  fig4_poverty_diabetes.png — Socioeconomic-health scatter")
    print("  fig5_ontology_map.png     — Ontology mapping architecture")
    print("  fig6_summary_stats.png    — Summary statistics infographic")
