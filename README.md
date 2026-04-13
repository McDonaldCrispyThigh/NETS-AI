# Synthetic Urban Intelligence
## Validating Commercial Geographies via AI Agents

**Honors Thesis Project**

**Principal Investigator:** Congyuan Zheng, University of Colorado Boulder  
**Advisors:** Prof. Jessica Finlay (CU Boulder) · Prof. Michael Esposito (U of Minnesota) · Yue Sun (Postdoc, CU Boulder)

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
python code/main.py --task gym --zips 55401 55402 55403
```

**Available tasks:** `library` · `park` · `coffee` · `gym` · `grocery` · `civic` · `religion` · `pharmacy`

```bash
# 4. (Pharmacy only) Validate AI output against NPPES NPI Registry
python code/validate_nppes.py --ai-csv data/Minneapolis_pharmacy_YYYYMMDD_HHMMSS.csv
python code/validate_nppes.py --ai-csv data/Minneapolis_pharmacy_YYYYMMDD_HHMMSS.csv --use-zips --output data/validation_result.csv
```

---

## 3. Repository Structure

```
NETS-AI/
├── code/
│   ├── main.py             # CLI entry point (argparse)
│   └── agent_workflow.py   # NETSAgentWorkflow class (search → classify → save)
├── skills/
│   ├── google_maps.py      # Google Maps Places API wrapper
│   └── yelp.py             # Yelp Fusion API wrapper (reserved for future use)
├── docs/
│   ├── PROMPT_GUIDE.md     # Prompt engineering rules and NAICS decision logic
│   ├── Methodology.md      # Full research methodology
│   └── nets_schema.json    # Output field definitions (22 columns)
├── data/                   # Generated CSV outputs (git-ignored, .gitkeep preserves folder)
├── .env.example            # API key template
├── requirements.txt        # Python dependencies (UTF-8)
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
| Business Search | Google Maps Places API |
| Secondary Enrichment | Yelp Fusion API (reserved) |
| Data Output | pandas → CSV |
| Spatial Analysis | ArcGIS Pro (external) |

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

---

## 7. Sprint Progress

| Sprint | Goal | Status |
|--------|------|--------|
| Sprint 1 | Build basic OpenAI Agent | ✅ Done |
| Sprint 2 | Improve prompt stability & NAICS logic | ✅ Done |
| Sprint 3 | Pilot data collection — Minneapolis coffee & library | ✅ Done |
| Sprint 4 | Compare AI data vs NETS · ArcGIS visualization | 🔄 In Progress |

---

## 8. Key Findings (Pilot)

- **267** unique coffee shops collected across 17 Minneapolis ZIP codes.
- **~92%** NAICS match rate on full dataset; **100%** on verified final dataset (60 records).
- Main misclassification: music venues with early morning hours misidentified as coffee shops.
- AI-estimated `Year_Established` mirrors NETS's own opacity — errors expose shared limitations.

---

## 9. Methodology & Prompt Design

- [`docs/Methodology.md`](docs/Methodology.md) — Research design, validation approach, limitations.
- [`docs/PROMPT_GUIDE.md`](docs/PROMPT_GUIDE.md) — Prompt architecture, NAICS decision rules, model settings.
