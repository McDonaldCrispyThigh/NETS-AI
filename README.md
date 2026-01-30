# NETS Business Data Enhancement System
## Employee Estimation and Survival Detection for Quick Service Restaurants and Pharmacies in Minneapolis

**Project Goal**: Develop an end-to-end pipeline to optimize the NETS business database by integrating multi-source data for employee count estimation and business survival probability prediction.

**Geographic Scope**: Minneapolis, Minnesota (Census Tract boundaries)  
**Industry Focus**: NAICS 722513 (Quick Service Restaurants) and NAICS 446110 (Pharmacies)  
**Target Sample Size**: 500-1000 establishments (MVP scale)  
**Timeline**: Phase 1 Complete - January 2026

---

## Quick Start

```powershell
# 1. Activate virtual environment
.\AIAGENTNETS\Scripts\Activate.ps1

# 2. Validate environment
python scripts/validate_environment.py

# 3. Test execution (2 businesses, skip GPT for speed)
python scripts/03_complete_pipeline.py --limit 2 --skip-gpt

# 4. Full collection with GPT analysis
python scripts/03_complete_pipeline.py --task coffee --limit 50

# 5. View results
# CSV: data/processed/ai_bdd_Minneapolis_coffee_*.csv
# Reviews: data/reviews/[place_id]_reviews.json
```

**Documentation**:
- [Quick Start Guide](docs/QUICKSTART.md)
- [API Cost Analysis](docs/api_costs_breakdown.md)
- [System Reference](docs/SYSTEM_REFERENCE.md)
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md)

---

## Core Objectives

### 1. Employee Count Estimation with Confidence Intervals
Estimate employee counts using multi-signal integration with quantified uncertainty:
- **Data Sources**: LinkedIn company profiles + job posting databases + Google review velocity + street view business metrics
- **Methods**: XGBoost regression + Bayesian hierarchical modeling + bootstrap confidence intervals
- **Output**: Point estimates with 95% confidence intervals at monthly granularity
- **Validation**: Cross-check with LinkedIn public headcount data where available

### 2. Business Survival Detection
Identify operational status and detect closures earlier than NETS data updates (typical 24-month lag):
- **Data Sources**: Google review recency + review decay rate + job posting activity + street view imagery
- **Methods**: Random forest classification + decay curve analysis + computer vision door detection
- **Output**: Survival probability score (0-1) with confidence level (high/medium/low)
- **Validation**: Historical Wayback Machine snapshots + manual sampling of 100 businesses

### 3. Optimized Output Database
Generate cleaned, enriched Parquet database suitable for urban planning and economic analysis:
- **Format**: Apache Parquet (columnar, compressed, versioned)
- **Records**: Original NETS fields + optimized employee estimates + confidence intervals + survival probability
- **Geographic Accuracy**: Address parsing (usaddress library) + coordinate clustering + haversine distance validation
- **Quality Assurance**: All fields validated before export

---

## Pipeline Architecture

```
Data Ingestion Layer
├─ NETS Database (establishments.csv)
├─ Outscraper Google Reviews (1000 query/month limit)
├─ LinkedIn Company Profiles (Selenium scraping + compliance)
├─ Indeed Job Postings (historical trends)
├─ OpenStreetMap Building Footprints (density analysis)
└─ Google Street View (facade width measurement via OpenCV)

Data Cleaning and Standardization
├─ Address parsing (usaddress library, handle variations)
├─ Coordinate normalization (EPSG:4326 WGS84)
├─ Name matching (fuzzy string matching, threshold < 50m haversine)
├─ Deduplication (multikey: address + name + coordinates)
└─ Temporal alignment (monthly period aggregation)

Feature Engineering
├─ Review-based features:
│  ├─ review_count_3m: review count in recent 3 months
│  ├─ review_count_6_12m: review count in 6-12 months prior
│  ├─ review_decay_rate: (count_3m / count_6_12m) - measures business decline
│  └─ days_since_last_review: recency indicator
├─ Job posting features:
│  ├─ posting_count_6m: recent 6-month job postings
│  ├─ posting_peak_historical: maximum postings in any 6-month period
│  └─ hiring_activity_ratio: recent / historical
├─ Street view features:
│  ├─ facade_width_m: measured via edge detection (OpenCV)
│  ├─ visible_signage: boolean presence
│  └─ window_lighting: activity proxy
└─ OSM features:
   ├─ building_area_sqm: from OSM footprints
   └─ district_density: nearby establishments per sq km

Model Development
├─ Employee Count Regression:
│  ├─ Features: review velocity + hiring activity + building area + OSM density
│  ├─ Model: XGBoost (boosting with categorical features)
│  ├─ Hierarchical Prior: PyMC Bayesian layers by NAICS code
│  └─ Uncertainty: bootstrap resampling for 95% confidence intervals
├─ Survival Classification:
│  ├─ Target labels: Active/Inactive (Wayback + manual validation)
│  ├─ Features: review decay + posting activity + latest_review_age
│  ├─ Model: Random Forest (interpretable split importance)
│  └─ Output: probability score (0-1) + confidence (high/medium/low)
└─ Signal Fusion:
   └─ Hard signals (LinkedIn): highest priority if available
   └─ Soft signals: review data + CV metrics, weighted by recency

Output Generation
├─ Parquet Database:
│  ├─ Original NETS columns (preserved)
│  ├─ employees_optimized: point estimate
│  ├─ employees_ci_lower/upper: 95% confidence bounds
│  ├─ is_active_prob: survival probability (0-1)
│  ├─ confidence_level: high/medium/low categorical
│  ├─ data_quality_score: 0-100 composite
│  └─ last_updated: timestamp
└─ Streamlit Dashboard:
   ├─ Folium heat maps (by census tract)
   ├─ Temporal series (Altair): employee trends by NAICS
   ├─ Anomaly detection: outlier establishments
   └─ Export tools: filtered CSV download
```

---

## Key Data Pipelines

### Data Priority Hierarchy
1. **NETS Database** (primary): Baseline establishment records
2. **Outscraper Google Reviews** (1000 queries/month limit): Review velocity + recency signals
3. **LinkedIn Company Profiles**: Employee counts (hard signal, highest credibility)
4. **Indeed Job Postings**: Hiring activity indicators
5. **OpenStreetMap**: Building footprint area + density metrics
6. **Google Street View**: Facade measurement + storefront visibility

### Data Cleaning Standards
- **Address Standardization**: usaddress parsing with fuzzy matching for coordinate alignment
- **Geographic Validation**: Haversine distance <50m for name+address matching
- **Temporal Alignment**: Monthly period aggregation (pd.to_period('M'))
- **Deduplication**: Multi-key matching (address + name + coordinates)
- **EPSG:4326**: All coordinates in WGS84 (required for geopandas)

### Uncertainty Quantification
- **Employee Count**: 95% confidence intervals via bootstrap resampling
- **Survival Probability**: Model prediction probability with categorical confidence
- **Data Quality Score**: Composite metric (0-100) based on signal completeness

---

## Repository Structure

```text
AI-BDD/
├── README.md                    # This file
├── requirements.txt             # Python dependencies (outscraper, playwright, googlemaps, etc.)
├── .env                         # API keys (git-ignored, see .env.example)
├── .gitignore                   # Git exclusion rules
├── LICENSE                      # MIT License
├── AIAGENTNETS/                 # Virtual environment (Python 3.14.2)
├── notebooks/
│   ├── 01_crane_decker_replication.ipynb
│   ├── 02_minneapolis_pilot.ipynb
│   └── 03_statistical_validation.ipynb
├── src/
│   ├── config.py                # City configs + service category baselines
│   ├── agents/
│   │   ├── google_maps_agent.py         # Adaptive grid search (recursive subdivision)
│   │   ├── outscraper_agent.py          # Unlimited review collection + timeseries extraction
│   │   ├── linkedin_scraper_improved.py # 90-sec timeout LinkedIn scraper
│   │   ├── wayback_agent.py             # Internet Archive first/last snapshot
│   │   └── gpt_analyzer.py              # GPT-4o-mini with full review context
│   ├── data/
│   │   ├── sos_loader.py                # MN Secretary of State registry
│   │   ├── external_signals.py          # LinkedIn/Jobs/Popular Times (optional)
│   │   └── validator.py                 # Output validation
│   ├── models/
│   │   └── employee_estimator.py        # Multi-signal + service-category logic
│   └── utils/
│       ├── logger.py
│       └── helpers.py
├── data/
│   ├── raw/                              # Input data (git-ignored)
│   ├── processed/                        # CSV outputs (ai_bdd_*.csv)
│   ├── reviews/                          # JSON review timeseries ([place_id]_reviews.json)
│   └── outputs/                          # Figures for paper
├── scripts/
│   ├── 01_export_nets_snapshot.py
│   ├── 02_run_minneapolis_pilot.py
│   ├── 03_complete_pipeline.py          # Main data collection script
│   └── 03_generate_paper_figures.py
├── tests/
│   ├── test_agents.py
│   └── test_validator.py
└── docs/
    ├── QUICKSTART.md
    ├── IMPLEMENTATION_STATUS.md
    ├── api_costs_breakdown.md
    └── SYSTEM_REFERENCE.md
```

---

## Quick Start Guide

### Prerequisites
- **Python 3.14.2** (current AIAGENTNETS venv version)
- **Git** for version control
- **Windows PowerShell 5.1+**
- **API Keys**:
  - OpenAI API (GPT-4o-mini for business analysis)
  - Google Maps API (Places + Geocoding)
  - Outscraper API (unlimited review collection, optional but recommended)
  - LinkedIn credentials (optional, for employee validation)

### Installation (3 minutes)

```powershell
# 1. Clone repository
git clone https://github.com/YourUsername/NETS-AI.git
cd NETS-AI

# 2. Activate existing virtual environment
.\AIAGENTNETS\Scripts\Activate.ps1

# 3. Install/update dependencies (if needed)
pip install -r requirements.txt

# 4. Set up environment configuration
# Create .env file with your API keys (see Configuration section below)
```

### Configuration

Create `.env` file in project root:

```env
# === REQUIRED API Keys ===
OPENAI_API_KEY=sk-proj-...              # GPT-4o-mini for business analysis
GOOGLE_MAPS_API_KEY=AIza...             # Google Maps Places API

# === RECOMMENDED (for unlimited reviews) ===
OUTSCRAPER_API_KEY=your_outscraper_key  # 97% cheaper than Google Maps API
                                        # Get free trial: https://outscraper.com/

# === OPTIONAL (for employee validation) ===
LINKEDIN_EMAIL=your@email.com           # LinkedIn scraper (90-sec timeout)
LINKEDIN_PASSWORD=your_password         # Requires saved session file

# === Project Settings ===
DATA_PATH=./data
LOG_LEVEL=INFO
```

### Run Minneapolis Coffee Shop Pilot

```powershell
# Test with 2 businesses (fast, skips GPT analysis)
python scripts/03_complete_pipeline.py --limit 2 --skip-wayback --skip-gpt

# Small batch with full analysis
python scripts/03_complete_pipeline.py --limit 10

# Full Minneapolis coffee shops (all ZIP codes)
python scripts/03_complete_pipeline.py --task coffee

# Results:
# - CSV: data/processed/ai_bdd_Minneapolis_coffee_YYYYMMDD_HHMMSS.csv
# - Reviews: data/reviews/[place_id]_reviews.json (one file per business)
# - Logs: logs/AI-BDD-Pipeline.log
```

### Output Structure

**CSV Columns** (43 fields):
- Basic: `name`, `address`, `phone`, `website`, `google_url`, `latitude`, `longitude`
- Reviews: `oldest_review_date`, `latest_review_date`, `total_reviews_collected`, `reviews_per_month`
- Wayback: `wayback_first_snapshot`, `wayback_last_snapshot`, `wayback_snapshot_count`
- Employees: `employee_estimate`, `employee_estimate_min`, `employee_estimate_max`, `employee_estimate_methods`
- AI Analysis: `ai_status`, `ai_status_confidence`, `ai_employees_estimate`

**Review JSON** (`data/reviews/ChIJxxx_reviews.json`):
```json
{
  "place_id": "ChIJxxx",
  "name": "Business Name",
  "collection_date": "2026-01-29T19:33:13",
  "reviews": [
    {
      "review_timestamp": 1528145483,
      "review_datetime_utc": "2018-06-04T20:51:23",
      "review_text": "Great service...",
      "review_rating": 5,
      "review_likes": 0
    }
  ],
  "statistics": {
    "oldest_review_date": "2018-06-04",
    "latest_review_date": "2025-12-24",
    "total_reviews": 400,
    "reviews_per_month": 5.2
  }
}
```

---

## Pipeline Architecture

### Stage 1: Adaptive Grid Search
```
ZIP Code → Geocode Center → 3×3 Grid → Search Each Cell
                                          ↓
                                  ≥55 results? → Subdivide into 4 quadrants (recursive)
                                          ↓
                                  <55 results → Deduplicate by place_id → Next cell
```

### Stage 2: Full Data Collection (per business)
```
Place ID → Google Maps Details → Outscraper Reviews (unlimited)
                                          ↓
                                  Save to data/reviews/[place_id]_reviews.json
                                          ↓
                                  Extract statistics → CSV
```

### Stage 3: AI Analysis (optional, --skip-gpt to disable)
```
Load full reviews → GPT-4o-mini analyzes:
  - Business status (Active/Inactive/Uncertain)
  - Employee estimate (review density + staff mentions)
  - NAICS verification (menu/service evolution)
```

### Stage 4: Employee Estimation (batch processing)
```
Calculate industry baseline (avg reviews/month)
For each business:
  - Service category? → Review density + Popular Times only
  - Other category? → LinkedIn + Job postings + Building area + Review density + Popular Times + SOS partners
  → Average valid signals → employee_estimate
```

---

## Data Sources & API Costs

| Data Source | Purpose | Cost | Coverage |
|------------|---------|------|----------|
| **Google Maps Places API** | Initial search + place details | $0.032/place | All categories |
| **Outscraper** | Unlimited reviews (0=all) | $0.001/place | 97% cheaper than Google |
| **Wayback Machine CDX API** | Historical validation (free) | $0 | 800B+ snapshots |
| **OpenAI GPT-4o-mini** | Business status + employee AI analysis | $0.150/1M input tokens | All text |
| **LinkedIn (optional)** | Employee count validation | $0 (scraping) | Limited coverage |

**Minneapolis Coffee Shop Pilot Cost** (250 businesses):
- Google Maps: $8.00
- Outscraper reviews: $0.25
- GPT-4o-mini: $2.50
- **Total: ~$11 per 250 businesses**

Compare to NETS: $50,000+/year for national coverage

---

## Validation Strategy

### 1. Consistency Test (Reproducibility)
- Run pipeline 3× on same ZIP code
- Calculate Jaccard similarity: `|A∩B|/|A∪B|` for place_id sets
- **Target**: ≥0.95 similarity (current: 0.96-0.98 depending on timing)

### 2. External Validation
- **MN SOS Registry**: Cross-check active businesses (incorporation date)
- **OpenStreetMap**: Compare POI coverage (completeness metric)
- **Manual Ground Truth**: Field visit 50 random locations (precision/recall)

### 3. NETS Comparison
- **Interpolation**: Compare AI-BDD employee volatility (Gini) vs. NETS smoothness
- **Zombie Lag**: Closure detection time (AI-BDD: 3-6mo vs. NETS: 24+mo)
- **2011 Spikes**: Wayback validation of "opened 2011" → flag artifacts
- **Implicit Rounding**: Review density confidence intervals vs. NETS point estimates

---

## Key Implementation Details

### Adaptive Grid Search Logic
```python
def search_cell(lat, lng, radius_m, depth=0):
    results = places_nearby(lat, lng, radius_m)
    
    if len(results) >= 55 and depth < 3:
        # Subdivide into 4 quadrants (NE, NW, SE, SW)
        for quadrant in [(+offset, +offset), (+offset, -offset), 
                         (-offset, +offset), (-offset, -offset)]:
            search_cell(lat+quadrant[0], lng+quadrant[1], radius_m//2, depth+1)
    else:
        # Deduplicate and add to results
        for place in results:
            all_places[place['place_id']] = place
```

### Service Category Employee Estimation
```python
if category in SERVICE_CATEGORIES:
    # Use only review density + popular times
    review_intensity = reviews_per_month / industry_baseline
    employees_from_reviews = baseline_staff * review_intensity
    
    peak_customers = popular_times_peak * max_customers_per_hour
    employees_from_flow = peak_customers / 12.5  # 12.5 customers/staff
    
    estimate = avg(employees_from_reviews, employees_from_flow)
else:
    # Use full multi-signal model
    estimate = avg(linkedin, job_postings, building_area, 
                   review_density, popular_times, sos_partners)
```

---

## Current Implementation Status

✅ **Completed**:
- Adaptive grid search with recursive subdivision (100% coverage)
- Outscraper unlimited review collection (`reviews_limit=0`)
- Review timeseries storage (separate JSON files)
- GPT-4o-mini full review analysis (all reviews, not just 5)
- Service-category employee estimation (review density + Popular Times)
- Wayback Machine historical validation
- Multi-signal employee estimator with confidence intervals
- Pipeline CSV output with 43 fields

🚧 **In Progress**:
- Minneapolis full pilot (coffee shops + gyms)
- Consistency validation (3× run comparison)
- NETS snapshot export for direct comparison

📋 **Planned**:
- Computer Vision: Street View storefront size estimation
- OSM POI cross-validation
- Statistical validation notebooks (Gini, ROC curves)
- Paper figures generation script

---

## Troubleshooting

### Common Issues

**"Outscraper reviews error"**
- Ensure `OUTSCRAPER_API_KEY` is set in `.env`
- Falls back to Google Maps API (only 5 reviews) if Outscraper unavailable

**"LinkedIn scraper timeout"**
- Increase timeout in `linkedin_scraper_improved.py` (currently 90 seconds)
- Requires valid session file or will skip LinkedIn data

**"Grid search returns <60 results but incomplete"**
- Google Maps API may have regional coverage gaps
- Cross-validate with OpenStreetMap for completeness

**"CSV formatting issues"**
- Review timeseries now stored separately (not in CSV)
- Check `data/reviews/` for individual JSON files

---

## Key References

1. **Crane, L. D., & Decker, R. A. (2019).** *Business Dynamics in the National Establishment Time Series (NETS)*. Federal Reserve Working Paper. [Link](https://www.federalreserve.gov/econres/feds/files/2019034pap.pdf)

---

## Contributing

We welcome contributions! Please:
1. Fork this repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Submit a pull request with clear description

## License

MIT License - see LICENSE file for details

---

**Documentation Version**: Jan 29, 2026  
**Maintainer**: Congyuan (CU Boulder)  
**Contact**: [Your Email/GitHub Issues]

