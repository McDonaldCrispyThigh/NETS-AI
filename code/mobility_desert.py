"""Mobility-weighted pharmacy desert analysis.

Formulation
-----------
For each census tract t:
  - carless(t) = ACS B08201_002 / B08201_001 (share of households with 0 vehicles)
  - d(t) = distance from tract centroid to nearest AI-collected pharmacy
  - T_walk  = 0.5 mi = 804.7 m  (Qato pedestrian threshold)
  - T_drive = 2.0 mi = 3218.7 m (rough 4-5 minute urban drive)

Mobility-weighted desert score per tract:
  MWDR(t) = carless(t) * I[d(t) > T_walk]
          + (1 - carless(t)) * I[d(t) > T_drive]

This is bounded in [0, 1] and represents the share of tract residents whose
typical mode (walk if carless, drive otherwise) does not reach a pharmacy
within their effective threshold.

Outputs
-------
- data/figures_board/_mobility_desert_tract.csv (per-tract)
- data/figures_board/_mobility_desert_quartile.json (Q1-Q4 summary)
- data/figures_board/_threshold_sensitivity.json (0.5 / 1.0 / 2.0 mi by quartile)
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

DATA = Path("data")
OUT = DATA / "figures_board"
OUT.mkdir(parents=True, exist_ok=True)

T_WALK_M  = 804.7   # 0.5 mi
T_DRIVE_M = 3218.7  # 2.0 mi

# ── Load tract polygons (TIGER 2023, MN counties 053 + 123) ──
tract = gpd.read_file("zip://data/tl_2023_27_tract.zip").to_crs(4326)
tract = tract[tract["COUNTYFP"].isin(["053", "123"])].copy()
print(f"tracts (Hennepin+Ramsey): {len(tract)}")

# ── Merge ACS + vehicles ──
acs = pd.read_csv("data/acs_tracts_2023.csv", dtype={"GEOID": str})
veh = pd.read_csv("data/acs_tracts_vehicles_2023.csv", dtype={"GEOID": str})
tract["GEOID"] = tract["GEOID"].astype(str)
tract = tract.merge(acs, on="GEOID", how="left").merge(veh, on="GEOID", how="left")

# Drop tracts with no income or no households (no analytic basis)
tract = tract[tract["med_hh_income"].notna() & (tract["total_hh"] > 0)].copy()
print(f"tracts after merge: {len(tract)}")

# ── Load AI pharmacy points ──
tp = pd.read_csv("data/audit2_tp_analysis_20260414_172017.csv")
fp = pd.read_csv("data/audit2_fp_analysis_20260414_172017.csv")
ai = pd.concat([tp, fp], ignore_index=True).dropna(subset=["Latitude", "Longitude"])
ai_gdf = gpd.GeoDataFrame(
    ai, geometry=gpd.points_from_xy(ai["Longitude"], ai["Latitude"]),
    crs="EPSG:4326",
)

# Project to UTM 15N (EPSG:26915) for accurate metric distances in MN
proj = "EPSG:26915"
tract_p = tract.to_crs(proj)
ai_p    = ai_gdf.to_crs(proj)

# ── Tract centroids and nearest-pharmacy distance ──
tract_p["centroid"] = tract_p.geometry.centroid
centroids = gpd.GeoDataFrame(
    tract_p[["GEOID", "med_hh_income", "total_pop", "carless_rate", "total_hh"]],
    geometry=tract_p["centroid"],
    crs=proj,
)
nearest = gpd.sjoin_nearest(centroids, ai_p[["geometry"]], how="left",
                             distance_col="dist_m")
# Aggregate (sjoin_nearest may return >1 if ties at exactly equal distance)
nearest = nearest.groupby("GEOID", as_index=False).agg({
    "med_hh_income": "first",
    "total_pop": "first",
    "carless_rate": "first",
    "total_hh": "first",
    "dist_m": "min",
})

# ── Classify ──
nearest["qato_desert"]      = (nearest["dist_m"] > T_WALK_M).astype(int)
nearest["walk_inaccessible"] = (nearest["dist_m"] > T_WALK_M).astype(int)
nearest["drive_inaccessible"] = (nearest["dist_m"] > T_DRIVE_M).astype(int)

# Mobility-weighted desert score (population-weighted within tract)
nearest["carless_pop"] = nearest["total_pop"] * nearest["carless_rate"]
nearest["car_pop"]     = nearest["total_pop"] * (1 - nearest["carless_rate"])
nearest["mwdr_pop"]    = (
    nearest["carless_pop"] * nearest["walk_inaccessible"]
    + nearest["car_pop"]   * nearest["drive_inaccessible"]
)
nearest["mwdr_score"]  = np.where(
    nearest["total_pop"] > 0,
    nearest["mwdr_pop"] / nearest["total_pop"],
    0.0,
)

# ── Income quartile assignment ──
qcuts = nearest["med_hh_income"].quantile([0.25, 0.5, 0.75]).values
def quartile(x):
    if x <= qcuts[0]: return 1
    if x <= qcuts[1]: return 2
    if x <= qcuts[2]: return 3
    return 4
nearest["Qinc"] = nearest["med_hh_income"].apply(quartile)

# ── Per-quartile aggregation ──
def agg_q(df, q):
    sub = df[df["Qinc"] == q]
    n = len(sub)
    qato_rate = sub["qato_desert"].mean() * 100 if n else 0
    # Population-weighted MWDR for the quartile
    pop_total = sub["total_pop"].sum()
    pop_inaccessible = sub["mwdr_pop"].sum()
    mwdr = (pop_inaccessible / pop_total * 100) if pop_total else 0
    median_carless = sub["carless_rate"].median() * 100
    median_dist_mi = sub["dist_m"].median() / 1609.34
    return {
        "Qinc": q, "tracts": n,
        "median_carless_pct": round(median_carless, 1),
        "median_dist_mi": round(median_dist_mi, 2),
        "qato_desert_rate_pct": round(qato_rate, 1),
        "mwdr_pct": round(mwdr, 1),
    }

qsummary = [agg_q(nearest, q) for q in (1, 2, 3, 4)]
print("--- quartile summary ---")
for r in qsummary: print(r)
(OUT / "_mobility_desert_quartile.json").write_text(json.dumps(qsummary, indent=2))

# Overall MSA
overall_pop = nearest["total_pop"].sum()
overall_inaccess = nearest["mwdr_pop"].sum()
overall_qato = nearest["qato_desert"].mean() * 100
overall_mwdr = overall_inaccess / overall_pop * 100
print(f"--- overall ---")
print(f"Qato desert rate (tract): {overall_qato:.1f}%")
print(f"MWDR (population):        {overall_mwdr:.1f}%")

# ── Threshold sensitivity (0.5 / 1.0 / 2.0 mi) ──
thresh_rows = []
for q in (1, 2, 3, 4):
    sub = nearest[nearest["Qinc"] == q]
    row = {"Qinc": q, "tracts": len(sub)}
    for label, t_mi in (("0.5 mi", 0.5), ("1.0 mi", 1.0), ("2.0 mi", 2.0)):
        t_m = t_mi * 1609.34
        row[f"desert_pct_{label}"] = round((sub["dist_m"] > t_m).mean() * 100, 1)
    thresh_rows.append(row)
print("--- threshold sensitivity ---")
for r in thresh_rows: print(r)
(OUT / "_threshold_sensitivity.json").write_text(json.dumps(thresh_rows, indent=2))

# Save per-tract for figure use
nearest.to_csv(OUT / "_mobility_desert_tract.csv", index=False)
print(f"wrote {OUT/'_mobility_desert_tract.csv'}")
