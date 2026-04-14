# Research Methodology

**Project:** Synthetic Urban Intelligence: Validating Commercial Geographies via AI Agents  
**Author:** Congyuan Zheng  
**Institution:** University of Colorado Boulder  
**Advisors:** Prof. Jessica Finlay, Prof. Michael Esposito, Yue Sun (Postdoc)  
**Last updated:** 2026-04-13

---

## 1. Research Questions

1. Can an AI agent generate business establishment data that structurally resembles the National Establishment Time-Series (NETS) database?
2. Are AI-generated business classifications (NAICS codes) accurate when validated against an independent ground truth?
3. Do systematic errors in AI-generated data expose analogous structural limitations embedded within NETS itself?

---

## 2. Study Area and Scope

**Primary geography:** Minneapolis-St. Paul Metropolitan Statistical Area (MSA), Minnesota.

**ZIP codes covered:** 60 ZIP codes spanning the City of Minneapolis (55401-55415, 55454, 55455), the City of St. Paul (55101-55108, 55116-55119, 55130), and inner-ring suburbs including Roseville, Richfield, Edina, Bloomington, Brooklyn Park, and Coon Rapids.

**Business category:** Retail pharmacies (NAICS 446110, Pharmacies and Drug Stores). This category was selected because (a) pharmacy access is a well-studied public health outcome with established spatial thresholds (Qato et al., 2014), (b) a regulatory ground truth dataset exists (MN Board of Pharmacy licensure database, pending receipt), and (c) the category spans both large chains and small independent operators, creating meaningful variation in digital visibility.

**Pilot categories** (Minneapolis only, 17 ZIP codes): libraries, parks, coffee shops, gyms, grocery stores, civic organizations, religious organizations. These pilots established pipeline performance benchmarks before full-MSA deployment.

---

## 3. AI Agent Data Collection Pipeline

The collection pipeline proceeds through four sequential stages.

### Stage 1: Search

Business locations are retrieved using the Google Maps Places Text Search API (`places()` endpoint). To overcome the API's hard limit of 60 results per query (3 pages x 20 results), each target ZIP code is divided into a 2x2 location-biased grid. The centroid of each ZIP code is resolved using the `pgeocode` library, and four offset query points are derived at approximately +/-780 m latitude and +/-790 m longitude from the centroid. Each grid point issues an independent location-biased search, and results are de-duplicated by Google's `place_id` identifier before further processing.

This grid strategy increases recall in dense urban areas. In testing on ZIP 55113 (Roseville), the grid approach recovered approximately 4x more unique results than a single centroid query. For sparse suburban ZIPs, the per-ZIP result count is constrained by the true number of establishments rather than the API cap.

### Stage 2: Enrichment

For each unique `place_id`, the Place Details API retrieves: business name, formatted address, phone number, business status, price level, opening hours, website URL, and up to 5 reviews. Reviews are requested with `reviews_sort="newest"` to ensure that the recorded `Last_Review_Date` reflects the most recent available date rather than an algorithmically ranked selection. The Wayback Machine CDX API is queried for each business website to obtain a count of archived snapshot-years, used as a proxy for chain status and web longevity.

### Stage 3: AI Classification

Each enriched record is submitted to OpenAI GPT-4o-mini for NAICS classification and metadata estimation. The model receives: business name, address, type labels, opening hours, price level, review excerpts, and a structured classification prompt specifying the target NAICS hierarchy. The model outputs: a 6-digit NAICS code, a confidence label (High/Low), a brief reasoning string, and estimated employee count and founding year. Temperature is set to 0.0 for deterministic, reproducible output.

### Stage 4: Quality Assurance

The pipeline applies two quality filters. First, `Is_Target_Match` flags records where the assigned NAICS code matches the target category (446110 for pharmacies). Second, records with `Business_Status != OPERATIONAL` are retained in the dataset but flagged. Final datasets are saved as timestamped CSV files to prevent overwriting.

---

## 4. Ground Truth Construction

### 4.1 NPPES NPI Registry (Interim Ground Truth)

The National Plan and Provider Enumeration System (NPPES) NPI Registry is used as the primary ground truth for the current analysis phase. NPPES is queried at the ZIP code level using the `validate_nppes.py` module, which retrieves all active pharmacy NPI records (taxonomy code 333600000X) within the target ZIP codes.

AI-collected pharmacy names are matched to NPPES records using fuzzy string similarity (RapidFuzz token sort ratio, threshold 0.75). For each AI record, the highest-scoring NPPES match above threshold is recorded as a true positive. AI records with no NPPES match above threshold are classified as false positives. NPPES records not matched by any AI record are classified as false negatives.

NPPES false negatives are further categorized into four classes based on business name pattern matching:
- **Closed / Acquired Chain**: Records matching names of known-closed chains (Snyder Drug, Osco, Phar-Mor)
- **Corporate Legal Name (non-retail)**: Records where the NPI holder is a corporate parent rather than a retail location (e.g., SUPERVALU PHARMACIES INC)
- **Specialty / Non-Retail**: Records matching specialty pharmacy patterns (mail-order, compounding, infusion, oncology)
- **Possible Missed Retail**: Remaining records that may represent active retail pharmacies missed by the AI collection

### 4.2 Known Limitations of NPPES as Ground Truth

NPPES indexes by licensure, not by consumer-facing retail presence. It includes corporate legal entities, specialty pharmacies, and previously active establishments that may no longer operate. These structural issues inflate the false negative count and suppress precision and recall figures relative to what a retail-only ground truth would produce. The metrics reported here (Precision 38.8%, Recall 17.8%, F1 24.4%) should be interpreted with this caveat.

### 4.3 Planned Primary Ground Truth: MN Board of Pharmacy

A formal data request has been submitted to the Minnesota Board of Pharmacy for the current licensure database of active retail pharmacy locations. Upon receipt, `validate_mnbop.py` will be implemented with the same interface as `validate_nppes.py`. NPPES validation will continue as a secondary cross-check. The MN Board dataset is expected to substantially improve precision and recall figures by restricting the ground truth to currently licensed retail dispensaries.

---

## 5. Validation Framework

The validation framework uses a triangulated comparison structure across three data sources:

**Comparison A (AI vs. NPPES):** Fuzzy name match at ZIP level. Reports precision, recall, F1, and false negative categorization. Currently active; results reported in Section 8 of the analysis summary.

**Comparison B (AI vs. MN Board of Pharmacy):** Direct match against regulatory licensure data. Planned; pending receipt of licensure dataset.

**Comparison C (AI vs. NETS):** Spatial join of AI-collected records to the NETS database by address or coordinates, followed by attribute comparison (NAICS code, employee count, establishment year). Planned for thesis analysis phase.

This triangulated approach is motivated by the recognition that no single administrative dataset constitutes a perfect ground truth. Discrepancies between sources are analytically meaningful: they reveal where each dataset's construction logic produces systematic gaps.

---

## 6. Spatial Analysis Methods

### 6.1 Tract-Level Socioeconomic Data

Census tract boundaries are obtained from the TIGER/Line 2023 shapefile (Hennepin and Ramsey counties, 472 tracts). Tract-level socioeconomic variables are retrieved from the American Community Survey (ACS) 5-year 2023 estimates (2019-2023) via the Census Data API. Key variables: median household income (`B19013_001E`), total population (`B01003_001E`), and percent non-White population (derived from race/ethnicity tables).

AI-collected pharmacy records and NPPES false negative records are spatially joined to tracts using `geopandas.sjoin` with a point-in-polygon operation in EPSG:4326.

### 6.2 Pharmacy Desert Classification

Following Qato et al. (2014), a census tract is classified as a pharmacy desert if the nearest retail pharmacy is more than 0.5 miles (804 meters) from the tract centroid. Nearest-pharmacy distance is computed using `geopandas.sjoin_nearest` after projecting both the pharmacy point layer and tract centroids to EPSG:3857 (Web Mercator) for accurate metric distance computation. Tract centroids are computed in EPSG:3857 and converted back to EPSG:4326 for the spatial join to avoid the CRS centroid distortion warning.

The 0.5-mile threshold is established in the pharmacy access literature as the maximum walking distance for medication pickup and has been applied in prior studies of urban pharmacy deserts (Qato et al., 2014). Results are reported overall and stratified by income quartile.

### 6.3 Income Quartile Stratification

Tracts are stratified into four income quartiles based on `med_hh_income`. Quartile boundaries are computed across all 472 tracts with non-missing income data. Desert rate, pharmacy density (pharmacies per 1,000 population), and mean nearest-pharmacy distance are reported per quartile.

---

## 7. Known Limitations and Mitigations

1. **Google Maps visibility bias.** The AI dataset overrepresents chain pharmacies and underrepresents independent, low-profile, or recently opened establishments. Mitigation: compare AI data against NPPES and MN Board of Pharmacy to quantify the gap.

2. **60-result API cap per query.** For dense urban ZIPs, a single search query returns at most 60 results. Mitigation: 2x2 location-biased grid search per ZIP. Residual gap: for categories with fewer than 60 establishments per ZIP (true for pharmacies in this MSA), the cap is not the binding constraint. For denser categories, the grid approach recovers additional records.

3. **NPPES structural inflation.** NPPES precision and recall figures reflect NPPES limitations as much as AI data quality. Mitigation: FN categorization and pending replacement with MN Board of Pharmacy data.

4. **GPT estimation uncertainty.** `Year_Established` and `Employees_Estimated` are model estimates without external corroboration. These mirror the opacity of NETS's own self-reported establishment year. Mitigation: treat as directional indicators, not ground truth values.

5. **Tract centroid approximation.** Pharmacy desert classification uses tract centroid distance, not population-weighted centroid. For large or irregular tracts, this may over- or underestimate access for residents near tract boundaries.

6. **ACS temporal mismatch.** Income and population data are ACS 5-year 2023 estimates (2019-2023 average), while pharmacy data reflects 2026 conditions. This temporal gap may introduce measurement error in the income-access relationship.

---

## References

Qato, D. M., Zenk, S., Wilder, J., Harrington, R., Gaskin, D., & Alexander, G. C. (2014). The availability of pharmacies in the United States: 2007-2015. *PLOS ONE*, 12(8), e0183172.

Barnatchez, K., Crane, L. D., & Decker, R. (2017). An assessment of the National Establishment Time-Series (NETS) database. *Finance and Economics Discussion Series*, 2017-110. Board of Governors of the Federal Reserve System.
