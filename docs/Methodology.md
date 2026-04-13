# Research Methodology — NETS-AI

**Project:** Synthetic Urban Intelligence: Validating Commercial Geographies via AI Agents  
**Author:** Congyuan Zheng  
**Institution:** University of Colorado Boulder  
**Advisors:** Prof. Jessica Finlay, Prof. Michael Esposito, Yue Sun (Postdoc)

---

## 1. Research Questions

1. Can an AI agent generate business establishment data that structurally resembles NETS?
2. Are AI-generated classifications (NAICS codes) accurate compared to ground truth?
3. Do AI-generated data errors reveal similar limitations embedded within NETS itself?

---

## 2. Study Area

**City:** Minneapolis, Minnesota  
**ZIP codes covered:** 55401–55415, 55454, 55455 (17 ZIP codes, full city coverage)  
**Business categories:** Libraries, Parks, Coffee Shops, Gyms, Grocery Stores,
Civic Organizations, Religious Organizations

---

## 3. Data Collection Pipeline

### 3.1 Source APIs

| API | Purpose | Limit strategy |
|-----|---------|----------------|
| Google Maps Places API | Primary business search + details | Loop 17 ZIP codes to bypass 60-result/query cap |
| Yelp Fusion API | Secondary enrichment (reserved) | 5 results/call; not yet integrated into main pipeline |
| OpenAI GPT-4o-mini | NAICS classification + metadata estimation | `temperature=0.0` for determinism |

### 3.2 De-duplication

Google Places API returns overlapping results across ZIP code queries.
De-duplication is performed using `place_id` (Google's unique identifier per
establishment) before any AI processing occurs.

### 3.3 AI Classification

See [`PROMPT_GUIDE.md`](PROMPT_GUIDE.md) for full prompt design and
decision logic. In brief:

- The model receives structured facts (hours, attributes, reviews) for each place.
- It assigns a 6-digit NAICS code and a `Confidence` label (High/Low).
- `temperature=0.0` ensures reproducibility — same input → same output.

---

## 4. Output Schema

See [`nets_schema.json`](nets_schema.json) for the full field list.

Key fields aligned to NETS variables:

| NETS Variable | AI Equivalent | Source |
|---------------|---------------|--------|
| Company name  | `Company`     | Google Maps |
| NAICS code    | `Calculated_NAICS` | GPT-4o-mini |
| Employees     | `Employees_Estimated` | GPT estimate |
| Year est.     | `Year_Established` | GPT estimate |
| Address       | `Street_Address` | Google Maps |
| Lat/Lng       | `Latitude`, `Longitude` | Google Maps |

---

## 5. Validation Approach

### 5.1 Internal validation (NAICS match rate)

`Is_Target_Match = (Calculated_NAICS == Target_NAICS)`

Match rate is computed per category and used as a proxy for classification accuracy.
A high match rate indicates the agent correctly identifies the business type.

### 5.2 External validation (vs. NETS)

- Spatial join: AI-generated records are joined to the NETS dataset by address/coordinates.
- Attribute comparison: NAICS codes, employee counts, and establishment years are compared.
- Visualization: ArcGIS Pro is used to map discrepancies spatially.

---

## 6. Pilot Study Results (Minneapolis Coffee Shops)

| Dataset | Records | Match Rate (NAICS 722515) |
|---------|---------|---------------------------|
| FULL_CITY_DATASET | 267 | ~92% |
| Final_Dataset (verified) | 60 | 100% |

**Key finding:** AI correctly identifies most coffee shops; main errors occur
when a place is a bar that opens early (e.g., music venues with morning hours).

---

## 7. Limitations

1. **Historical reconstruction:** GPT cannot reliably estimate `Year_Established`
   without external corroboration. This mirrors a known weakness in NETS (self-reported years).
2. **Closed businesses:** Google Maps does not reliably mark permanently closed
   establishments; some inactive businesses may appear as active.
3. **Review bias:** Only 5 reviews per place are available; low-review businesses
   are classified primarily on name and hours.
4. **Spatial coverage:** ZIP-code looping strategy maximizes recall but may still
   miss businesses at ZIP boundaries.

---

## 8. Reproducibility Checklist

- [x] All API calls logged with parameters
- [x] `temperature=0.0` for GPT (deterministic)
- [x] Timestamped output files (no overwriting)
- [x] De-duplication via `place_id` before AI processing
- [ ] Seed control for any future stochastic components
- [ ] Full NETS comparison dataset archived in `/data`
