# Synthetic Urban Intelligence
## Validating Commercial Geographies via AI Agents

**Honors Thesis Project**

**Principal Investigator:** Congyuan Zheng, University of Colorado Boulder  
**Committee:** Prof. Jessica M. Finlay (CU Boulder Geography, Thesis Advisor) · Prof. Stephen Becker (CU Boulder Applied Mathematics) · Prof. William Travis (CU Boulder Geography, Honors Representative)  
**Mentors:** Yue Sun (Postdoctoral Researcher, University of Minnesota study team)

---

## 1. Project Goal

### Academic Goal

Investigate the structural and methodological problems of the **National Establishment Time-Series (NETS)** database and evaluate whether AI-generated business data can serve as a viable alternative or supplement.

### Technical Goal

Build a reproducible AI Agent that collects real-world business data via public APIs, classifies it using GPT-4o-mini, and outputs NETS-compatible structured datasets.

---

## 2. Quick Start

```bash
# 1. Clone and set up environment
git clone https://github.com/McDonaldCrispyThigh/NETS-AI.git
cd NETS-AI
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Add API keys
cp .env.example .env   # then fill in your keys

# 3. Run a collection task
python code/main.py --task coffee
python code/main.py --task library --city Minneapolis
python code/main.py --task pharmacy --city Minneapolis-StPaul --zips 55401 55402 ...
```

**Available tasks:** `library` · `park` · `coffee` · `gym` · `grocery` · `civic` · `religion` · `pharmacy`

```bash
# 4. (Pharmacy only) Validate AI output against MN Board of Pharmacy
python code/validate_board.py --ai-csv data/Minneapolis-StPaul_pharmacy_YYYYMMDD_HHMMSS.csv

# 5. Multi-stage validity audit (institutional vs retail FN)
python code/audit_board_validation.py

# 6. Mobility-weighted desert analysis (requires ACS vehicle data)
python code/fetch_acs_vehicles.py
python code/mobility_desert.py

# 7. Generate thesis figures (8 figures total)
python code/visualize.py                      # figure1-3 (coverage, desert, wayback)
python code/generate_figures_v3.py            # figure4-6 (wayback x match, chain/indep, FN hierarchy)
python code/generate_north_mpls_map.py        # figure7 (North Mpls focus)
python code/generate_holc_overlay.py          # figure8 (HOLC overlay)
python code/generate_mobility_figures.py      # figure9-10 (MWDR, threshold sensitivity)
python code/three_source_venn.py              # figure11 (three-source coverage)

# 8. Bootstrap confidence intervals + supplementary analyses
python code/bootstrap_metrics.py
python code/supplementary_analyses.py         # logistic regression, MAUP, centroid sensitivity
```

**Reproducibility note**: complete prompt template, API parameters,
RapidFuzz protocol, and bootstrap random seeds are documented in
`docs/thesis/chapters/appendix_b_reproducibility.tex` (rendered as
Appendix B in `docs/thesis/main.pdf`).

---

## 3. Repository Structure

```
NETS-AI/
├── code/
│   ├── main.py                 # CLI entry point (argparse)
│   ├── agent_workflow.py       # NETSAgentWorkflow class (search -> classify -> save)
│   ├── spatial_analysis.py     # ACS + TIGER tract join, NPPES FN classification, desert stats
│   ├── visualize.py            # Figures 1 / 2a / 2b / 3 (geopandas + contextily, 1200 DPI)
│   └── validate_nppes.py       # NPPES NPI Registry ground-truth validation
├── skills/
│   ├── google_maps.py          # Google Maps Places API wrapper (2x2 grid search per ZIP)
│   ├── wayback_agent.py        # Wayback Machine CDX enrichment
│   └── yelp.py                 # Yelp Fusion API wrapper (reserved)
├── docs/
│   ├── Methodology.md          # Full research methodology
│   ├── API_LIMITATIONS.md      # Hard constraints + biases for all data sources
│   ├── IMPLEMENTATION_STATUS.md# Gap tracking: planned vs. running
│   ├── PROMPT_GUIDE.md         # Prompt engineering rules and NAICS decision logic
│   └── nets_schema.json        # Output field definitions (22 columns)
├── data/
│   └── figures/                # Thesis figures (1200 DPI PNG)
│       ├── figure1_coverage_map.png
│       ├── figure2a_desert_map.png
│       ├── figure2b_distance_scatter.png
│       └── figure3_wayback_distribution.png
├── .env.example                # API key template
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 4. Environment Variables

Create a `.env` file (see `.env.example`):

```
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
YELP_API_KEY=...
```

---

## 5. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| AI Classification | OpenAI GPT-4o-mini (`temperature=0.0`) |
| Business Search | Google Maps Places API (2x2 location-biased grid per ZIP) |
| Secondary Enrichment | Yelp Fusion API (reserved) |
| Historical Signal | Wayback Machine CDX API |
| Data Output | pandas -> CSV |
| Spatial Analysis | geopandas + matplotlib + contextily |
| ZIP Centroids | pgeocode |

---

## 6. Output Schema

All runs produce a CSV with 22 columns. See [`docs/nets_schema.json`](docs/nets_schema.json) for full field definitions. Key columns:

| Column | Source | Description |
|--------|--------|-------------|
| `Company` | Google Maps | Business name |
| `Calculated_NAICS` | GPT-4o-mini | Assigned 6-digit NAICS code |
| `Is_Target_Match` | derived | Whether NAICS matches expected category |
| `Confidence` | GPT-4o-mini | High / Low |
| `Latitude`, `Longitude` | Google Maps | WGS84 coordinates |
| `Employees_Estimated` | GPT-4o-mini | Estimated headcount |
| `Year_Established` | GPT-4o-mini | Estimated founding year |
| `Wayback_Snapshot_Count` | Wayback CDX | Years with archived snapshots (chain proxy) |

---

## 7. Sprint Progress

| Sprint | Goal | Status |
|--------|------|--------|
| Sprint 1 | Build basic OpenAI Agent | Done |
| Sprint 2 | Improve prompt stability & NAICS logic | Done |
| Sprint 3 | Pilot data collection -- Minneapolis coffee & library | Done |
| Sprint 4 | Compare AI data vs NETS · spatial visualization | Done |
| Sprint 5 | Full MSA pharmacy dataset · pharmacy desert analysis · thesis figures | Done |

---

## 8. Key Findings (Full MSA Pharmacy Dataset)

**Data collection** -- Twin Cities MSA, 60 ZIP codes, 2x2 location-biased grid search:

- **399** unique pharmacies collected across **101** ZIP codes
- **99.2%** NAICS match rate (446110 Pharmacies & Drug Stores)
- **94.5%** high-confidence classifications
- 270 chain / 129 independent (by name-keyword classification)

**Validation vs. NPPES NPI Registry** (872 active records, same ZIPs):

| Metric | Value |
|--------|-------|
| Precision | 38.8% |
| Recall | 17.8% |
| F1 | 24.4% |
| Possible missed retail (FN) | 252 |

**Pharmacy desert analysis** (Qato et al. 2014, 0.5-mile threshold):

| Income Quartile | Desert Rate |
|----------------|-------------|
| Q1 (lowest) | 65.3% |
| Q2 | 83.8% |
| Q3 | 91.5% |
| Q4 (highest) | 94.9% |
| **Overall** | **83.9%** |

North Minneapolis (55411/55412): 16 of 18 tracts classified as pharmacy deserts.

Low precision/recall against NPPES reflects known NPPES limitations (corporate legal names, specialty/non-retail entries, and closed/acquired chains inflate the registry count). See [`docs/API_LIMITATIONS.md`](docs/API_LIMITATIONS.md).

---

## 9. Methodology & Prompt Design

- [`docs/Methodology.md`](docs/Methodology.md) -- Research design, validation approach, limitations.
- [`docs/PROMPT_GUIDE.md`](docs/PROMPT_GUIDE.md) -- Prompt architecture, NAICS decision rules, model settings.
- [`docs/API_LIMITATIONS.md`](docs/API_LIMITATIONS.md) -- Hard constraints and biases for all data sources.
