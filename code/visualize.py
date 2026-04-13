"""
visualize.py  --  Generate spatial/statistical figures for NETS-AI thesis.

Reads outputs from spatial_analysis.py. Run AFTER spatial_analysis.py.

Usage
-----
    python code/visualize.py

Outputs (saved to data/figures/, gitignored)
    figure1_coverage_map.png        Coverage map with income choropleth
    figure2_income_scatter.png      Tract income vs pharmacy count
    figure3_wayback_distribution.png  Wayback snapshot distribution
"""

import os
import sys
import zipfile
import tempfile
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")   # non-interactive backend; safe for all platforms
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from pathlib import Path
from scipy import stats

_CODE_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT     = os.path.abspath(os.path.join(_CODE_DIR, ".."))

DATA_DIR    = os.path.join(_ROOT, "data")
FIGURES_DIR = os.path.join(DATA_DIR, "figures")

_CHAIN_KW = frozenset({
    "cvs", "walgreens", "rite aid", "walmart", "target",
    "costco", "kroger", "hy-vee", "hyvee", "cub",
})


def is_chain(name: str) -> bool:
    n = str(name).lower()
    return any(kw in n for kw in _CHAIN_KW)


def _load_tract_gdf(acs_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """Load TIGER/Line shapefile and merge ACS data."""
    cache_path = os.path.join(DATA_DIR, "tl_2023_27_tract.zip")
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(cache_path, "r") as z:
            z.extractall(tmp)
        shp = next(Path(tmp).glob("*.shp"))
        gdf = gpd.read_file(str(shp))
    gdf = gdf[gdf["COUNTYFP"].isin(["053", "123"])].copy()
    gdf = gdf.to_crs(epsg=4326)
    gdf["GEOID"] = gdf["GEOID"].astype(str)
    acs_df["GEOID"] = acs_df["GEOID"].astype(str)
    gdf = gdf.merge(acs_df, on="GEOID", how="left")
    return gdf


def load_data():
    """Load all required files for visualization."""
    ai_df  = pd.read_csv(os.path.join(DATA_DIR, "spatial_ai_tracts.csv"))
    fn_df  = pd.read_csv(os.path.join(DATA_DIR, "spatial_nppes_fn_tracts.csv"))
    acs_df = pd.read_csv(os.path.join(DATA_DIR, "acs_tracts_2023.csv"),
                         dtype={"GEOID": str})
    gdf    = _load_tract_gdf(acs_df)
    return ai_df, fn_df, gdf


# ---- Figure 1: Coverage map ----

def figure1_coverage_map(ai_df: pd.DataFrame, fn_df: pd.DataFrame,
                          gdf: gpd.GeoDataFrame) -> None:
    """
    Choropleth by median household income (5 quantiles, YlOrRd).
    Blue dots = AI-collected pharmacies.
    Red triangles = NPPES possible-missed-retail FN records with coordinates.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Separate tracts with and without income data
    gdf_data = gdf[gdf["med_hh_income"].notna() & (gdf["med_hh_income"] > 0)].copy()
    gdf_na   = gdf[~(gdf["med_hh_income"].notna() & (gdf["med_hh_income"] > 0))]

    gdf_na.plot(ax=ax, color="#d9d9d9", linewidth=0.3, edgecolor="white")

    if not gdf_data.empty:
        gdf_data["q"] = pd.qcut(gdf_data["med_hh_income"], q=5,
                                  labels=False, duplicates="drop")
        cmap = matplotlib.colormaps.get_cmap("YlOrRd").resampled(5)
        for q in range(5):
            sub = gdf_data[gdf_data["q"] == q]
            if not sub.empty:
                sub.plot(ax=ax, color=cmap(q), linewidth=0.3,
                         edgecolor="white", alpha=0.85)

    # AI pharmacy points
    ai_valid = ai_df[ai_df["Latitude"].notna() & ai_df["Longitude"].notna()]
    ax.scatter(ai_valid["Longitude"], ai_valid["Latitude"],
               c="#1f78b4", s=30, zorder=5, alpha=0.9)

    # NPPES possible-missed-retail with coordinates
    fn_missed = fn_df[
        (fn_df.get("FN_Category", "") == "possible_missed_retail")
        & fn_df["Latitude"].notna()
        & fn_df["Longitude"].notna()
    ]
    if not fn_missed.empty:
        ax.scatter(fn_missed["Longitude"], fn_missed["Latitude"],
                   c="#e31a1c", s=35, zorder=5, alpha=0.9, marker="^")

    # Legend
    if not gdf_data.empty:
        cmap = matplotlib.colormaps.get_cmap("YlOrRd").resampled(5)
        income_patches = [
            mpatches.Patch(color=cmap(i), label=f"Income Quintile Q{i+1}")
            for i in range(5)
        ]
    else:
        income_patches = []

    point_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#1f78b4",
               markersize=8, label=f"AI-Collected Pharmacy (n={len(ai_valid)})"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#e31a1c",
               markersize=8,
               label=f"NPPES-Only Possible Retail (n={len(fn_missed)})"),
        mpatches.Patch(color="#d9d9d9", label="No income data"),
    ]
    ax.legend(handles=income_patches + point_handles,
              loc="lower right", fontsize=8, framealpha=0.9, title="Legend")

    ax.set_title(
        "AI-Collected vs NPPES-Only Pharmacies\n"
        "Minneapolis MSA by Median Household Income Quintile",
        fontsize=13, fontweight="bold", pad=12,
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    out = os.path.join(FIGURES_DIR, "figure1_coverage_map.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {out}")


# ---- Figure 2: Income scatter ----

def figure2_income_scatter(ai_df: pd.DataFrame) -> None:
    """
    Scatter plot: tract median income (x) vs AI pharmacy count (y).
    Bubble size = tract population. Color = percent non-white.
    OLS regression line with r and p values.
    """
    needed_cols = {"GEOID", "med_hh_income", "total_pop", "pct_nonwhite", "Company"}
    missing = needed_cols - set(ai_df.columns)
    if missing:
        print(f"    Figure 2: missing columns {missing}, skipping.")
        return

    tract_df = (
        ai_df.dropna(subset=["GEOID"])
        .groupby("GEOID")
        .agg(
            n_pharm=("Company",        "count"),
            income =("med_hh_income",  "first"),
            pop    =("total_pop",      "first"),
            pct_nw =("pct_nonwhite",   "first"),
        )
        .query("income > 0 and pop > 0")
        .dropna(subset=["income", "pop"])
        .reset_index()
    )

    if len(tract_df) < 3:
        print("    Figure 2: fewer than 3 tracts with data, skipping.")
        return

    fig, ax = plt.subplots(figsize=(10, 7))

    sizes = ((tract_df["pop"] / tract_df["pop"].max()) * 200 + 20).clip(20, 220)
    norm  = mcolors.Normalize(vmin=tract_df["pct_nw"].min(),
                               vmax=tract_df["pct_nw"].max())
    sc = ax.scatter(
        tract_df["income"], tract_df["n_pharm"],
        s=sizes, c=tract_df["pct_nw"],
        cmap="PuRd", norm=norm,
        alpha=0.75, edgecolors="grey", linewidths=0.4, zorder=3,
    )
    plt.colorbar(sc, ax=ax, label="% Non-White Population")

    slope, intercept, r, p, _ = stats.linregress(
        tract_df["income"], tract_df["n_pharm"]
    )
    x_line = np.linspace(tract_df["income"].min(), tract_df["income"].max(), 100)
    ax.plot(x_line, slope * x_line + intercept,
            color="#333333", linewidth=1.5, linestyle="--",
            label=f"OLS fit  r={r:.2f}, p={p:.3f}")

    ax.set_xlabel("Median Household Income ($)", fontsize=11)
    ax.set_ylabel("AI-Collected Pharmacies in Tract", fontsize=11)
    ax.set_title(
        "Pharmacy Coverage by Neighborhood Income\n"
        "(bubble size = tract population, color = % non-white)",
        fontsize=12, fontweight="bold",
    )
    ax.legend(fontsize=9)
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    out = os.path.join(FIGURES_DIR, "figure2_income_scatter.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {out}")


# ---- Figure 3: Wayback distribution ----

def figure3_wayback_distribution(ai_df: pd.DataFrame) -> None:
    """
    Grouped bar chart: Wayback snapshot bucket vs pharmacy count.
    Two bars per bucket: chain vs independent (by name keyword).
    """
    if "Wayback_Snapshot_Count" not in ai_df.columns:
        print("    Figure 3: Wayback_Snapshot_Count not found, skipping.")
        return

    df = ai_df.copy()
    df["Is_Chain"] = df["Company"].apply(is_chain)

    def _bucket(v) -> str:
        try:
            v = int(v)
        except (TypeError, ValueError):
            return "Unknown"
        if v < 0:
            return "Chain\n(sentinel -1)"
        if v == 0:
            return "No Web\n(0 yrs)"
        if v <= 5:
            return "Small\n(1-5 yrs)"
        if v <= 10:
            return "Moderate\n(6-10 yrs)"
        return "Established\n(10+ yrs)"

    bucket_order = [
        "Chain\n(sentinel -1)", "No Web\n(0 yrs)", "Small\n(1-5 yrs)",
        "Moderate\n(6-10 yrs)", "Established\n(10+ yrs)",
    ]
    df["bucket"] = df["Wayback_Snapshot_Count"].apply(_bucket)

    chains = df[df["Is_Chain"]]["bucket"].value_counts()
    indeps = df[~df["Is_Chain"]]["bucket"].value_counts()

    x     = np.arange(len(bucket_order))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width / 2, [chains.get(b, 0) for b in bucket_order],
           width, label="Chain Pharmacy",       color="#1f78b4", alpha=0.85)
    ax.bar(x + width / 2, [indeps.get(b, 0) for b in bucket_order],
           width, label="Independent Pharmacy", color="#ff7f00", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(bucket_order, fontsize=10)
    ax.set_xlabel("Wayback Machine Snapshot Coverage", fontsize=11)
    ax.set_ylabel("Number of Pharmacies", fontsize=11)
    ax.set_title(
        "Wayback Machine Coverage by Pharmacy Type\n"
        "(AI-collected Minneapolis pharmacies)",
        fontsize=12, fontweight="bold",
    )
    ax.legend(fontsize=10)
    ax.yaxis.grid(True, alpha=0.35)
    ax.set_axisbelow(True)

    out = os.path.join(FIGURES_DIR, "figure3_wayback_distribution.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved: {out}")


# ---- Main ----

def main() -> None:
    os.makedirs(FIGURES_DIR, exist_ok=True)

    required = [
        os.path.join(DATA_DIR, "spatial_ai_tracts.csv"),
        os.path.join(DATA_DIR, "spatial_nppes_fn_tracts.csv"),
        os.path.join(DATA_DIR, "tl_2023_27_tract.zip"),
        os.path.join(DATA_DIR, "acs_tracts_2023.csv"),
    ]
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        print("ERROR: Run spatial_analysis.py first. Missing:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print(">>> Loading data ...")
    ai_df, fn_df, gdf = load_data()
    print(f"    AI joined: {len(ai_df)} rows | FN joined: {len(fn_df)} rows")

    print(">>> Figure 1: Coverage map ...")
    figure1_coverage_map(ai_df, fn_df, gdf)

    print(">>> Figure 2: Income scatter ...")
    figure2_income_scatter(ai_df)

    print(">>> Figure 3: Wayback distribution ...")
    figure3_wayback_distribution(ai_df)

    print(f"\n>>> visualize.py complete. Figures saved to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
