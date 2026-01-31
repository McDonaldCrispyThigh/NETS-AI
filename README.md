# NETS Business Data Enhancement System
## Employee Estimation and Survival Detection for Quick Service Restaurants and Pharmacies in Minneapolis

**Project Goal**: Develop an end-to-end pipeline to optimize the NETS business database by integrating multi-source data for employee count estimation and business survival probability prediction.

**Geographic Scope**: Minneapolis, Minnesota (Census Tract boundaries) 
**Industry Focus**: 
- **Primary**: NAICS 722513 (Limited-Service Restaurants / Quick Service / Fast Food)
- **Secondary**: NAICS 446110 (Pharmacies and Drug Stores)
- **Note**: Coffee shops (NAICS 722515) and gyms (NAICS 713940) excluded from MVP scope

**Target Sample Size**: 500-1000 establishments (MVP baseline) 
**Implementation Status**: Phase 4 (Model Development) - January 2026

**Pipeline Execution Stages**:
- [x] Phase 0: Environment setup and NETS database ingestion
- [x] Phase 1: Multi-source data collection (Outscraper API, LinkedIn scraping)
- [x] Phase 2: Address parsing and coordinate standardization (EPSG:4326)
- [x] Phase 3: Feature engineering (review decay rates, hiring activity metrics)
- [x] Phase 4: Employee regression and survival classification models
- [ ] Phase 5: Signal fusion and Parquet database export
- [ ] Phase 6: Health equity validation (food desert and pharmacy access analysis)

---

## Quick Start

> **CRITICAL**: This pipeline REQUIRES a NETS database snapshot as primary input. 
> External data sources (Google Maps, LinkedIn) supplement but do NOT replace NETS records.
> See `scripts/generate_sample_data.py` for required CSV schema.

```powershell
# 1. Activate virtual environment
.\AIAGENTNETS\Scripts\Activate.ps1

# 2. Check NETS data requirements and schema
python scripts/generate_sample_data.py

# 3. Prepare your NETS CSV data (REQUIRED)
# Test data (5-20 records): tests/fixtures/nets_test_data.csv
# Production data: data/raw/nets_minneapolis_full.csv

# 4. Run pipeline in test mode
python scripts/run_pipeline.py --test

# 5. Run with skip options for faster testing
python scripts/run_pipeline.py --test --skip employees survival

# 6. Production run with your data
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv

# 7. View results in dashboard
streamlit run dashboard/app.py
```

**Documentation**:
- [Quick Start Guide](docs/QUICKSTART.md)
- [Testing Guide](docs/TESTING.md)
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

### 4. Health Equity Validation (MVP Requirement)
Demonstrate impact on public health metrics using optimized NETS data:
- **Food Environment Index**: Compare tract-level fast food density (original NETS vs. survival-weighted counts) in low-income Census Tracts
- **Pharmacy Desert Analysis**: Identify tracts with <1 pharmacy per 10,000 residents using probability-weighted operational counts
- **Zombie Lag Reduction**: Quantify improvement in closure detection accuracy (original NETS typically 12-24 month lag)
- **Validation**: Ground truth comparison with manual field surveys of 100 randomly sampled establishments

---

## Pipeline Architecture

```
Data Ingestion Layer
[|][-] NETS Database (establishments.csv)
[|][-] Outscraper Google Reviews (1000 query/month limit)
[|][-] LinkedIn Company Profiles (Selenium scraping + compliance)
[|][-] Indeed Job Postings (historical trends)
[|][-] OpenStreetMap Building Footprints (density analysis)
[_][-] Google Street View (facade width measurement via OpenCV)

Data Cleaning and Standardization
[|][-] Address parsing (usaddress library, handle variations)
[|][-] Coordinate normalization (EPSG:4326 WGS84)
[|][-] Name matching (fuzzy string matching, threshold < 50m haversine)
[|][-] Deduplication (multikey: address + name + coordinates)
[_][-] Temporal alignment (monthly period aggregation)

Feature Engineering
[|][-] Review-based features:
 [|][-] review_count_3m: review count in recent 3 months
 [|][-] review_count_6_12m: review count in 6-12 months prior
 [|][-] review_decay_rate: (count_3m / count_6_12m) - measures business decline
 [_][-] days_since_last_review: recency indicator
[|][-] Job posting features:
 [|][-] posting_count_6m: recent 6-month job postings
 [|][-] posting_peak_historical: maximum postings in any 6-month period
 [_][-] hiring_activity_ratio: recent / historical
[|][-] Street view features:
 [|][-] facade_width_m: measured via edge detection (OpenCV)
 [|][-] visible_signage: boolean presence
 [_][-] window_lighting: activity proxy
[_][-] OSM features:
 [|][-] building_area_sqm: from OSM footprints
 [_][-] district_density: nearby establishments per sq km

Model Development
[|][-] Employee Count Regression:
 [|][-] Features: review velocity + hiring activity + building area + OSM density
 [|][-] Model: XGBoost (boosting with categorical features)
 [|][-] Hierarchical Prior: PyMC Bayesian layers by NAICS code
 [_][-] Uncertainty: bootstrap resampling for 95% confidence intervals
[|][-] Survival Classification:
 [|][-] Target labels: Active/Inactive (Wayback + manual validation)
 [|][-] Features: review decay + posting activity + latest_review_age
 [|][-] Model: Random Forest (interpretable split importance)
 [_][-] Output: probability score (0-1) + confidence (high/medium/low)
[_][-] Signal Fusion:
 [_][-] Hard signals (LinkedIn): highest priority if available
 [_][-] Soft signals: review data + CV metrics, weighted by recency

Output Generation
[|][-] Parquet Database (PRIMARY OUTPUT):
 [|][-] Path: data/processed/nets_ai_minneapolis.parquet
 [|][-] Advantages: 3-5x smaller than CSV, preserves geospatial types, GeoDataFrame compatible
 [|][-] Original NETS columns (preserved)
 [|][-] employees_optimized: point estimate
 [|][-] employees_ci_lower/upper: 95% confidence bounds
 [|][-] is_active_prob: survival probability (0-1)
 [|][-] confidence_level: high/medium/low categorical
 [|][-] data_quality_score: 0-100 composite
 [_][-] last_updated: timestamp
[_][-] Streamlit Dashboard:
 [|][-] Folium heat maps (by census tract)
 [|][-] Temporal series (Altair): employee trends by NAICS
 [|][-] Anomaly detection: outlier establishments
 [_][-] Export tools: CSV fallback download for Excel compatibility
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
NETS-Enhancement/
[|][-][-] README.md # This file
[|][-][-] requirements.txt # Python dependencies
[|][-][-] .env # API keys (git-ignored, see .env.example)
[|][-][-] .gitignore # Git exclusion rules
[|][-][-] LICENSE # MIT License
[|][-][-] AIAGENTNETS/ # Virtual environment (Python 3.14.2)
[|][-][-] notebooks/
 [|][-][-] 01_crane_decker_replication.ipynb
 [|][-][-] 02_minneapolis_pilot.ipynb
 [_][-][-] 03_statistical_validation.ipynb
[|][-][-] src/
 [|][-][-] config.py # Configuration settings
 [|][-][-] agents/
  [|][-][-] google_maps_agent.py # Adaptive grid search
  [|][-][-] outscraper_agent.py # Review collection
  [|][-][-] linkedin_scraper.py # LinkedIn data scraper
  [|][-][-] wayback_agent.py # Internet Archive
  [_][-][-] gpt_analyzer.py # GPT analysis
 [|][-][-] data/
  [|][-][-] nets_loader.py # NETS data loading
  [|][-][-] pipeline.py # Main data pipeline
  [|][-][-] external_signals.py # External data sources
  [_][-][-] validator.py # Output validation
 [|][-][-] models/
  [|][-][-] bayesian_employee_estimator.py # Employee estimation
  [|][-][-] survival_detector.py # Business survival detection
  [_][-][-] employee_estimator.py # Multi-signal estimation
 [_][-][-] utils/
  [|][-][-] logger.py
  [_][-][-] helpers.py
[|][-][-] data/
 [|][-][-] raw/ # Your NETS CSV files go here
 [|][-][-] processed/ # Pipeline outputs
 [|][-][-] reviews/ # JSON review timeseries
 [_][-][-] outputs/ # Analysis figures
[|][-][-] scripts/
 [|][-][-] generate_sample_data.py # Data requirements documentation
 [|][-][-] run_pipeline.py # Main pipeline runner
 [|][-][-] quickstart.py # Automated setup
 [_][-][-] validate_environment.py # Environment checker
[|][-][-] tests/
 [|][-][-] fixtures/ # Test data goes here
 [|][-][-] test_agents.py
 [_][-][-] test_validator.py
[|][-][-] dashboard/
 [_][-][-] app.py # Streamlit visualization dashboard
[_][-][-] docs/
 [|][-][-] QUICKSTART.md
 [|][-][-] TESTING.md
 [|][-][-] USAGE.md
 [|][-][-] IMPLEMENTATION_STATUS.md
 [|][-][-] api_costs_breakdown.md
 [_][-][-] SYSTEM_REFERENCE.md
```

---

## Quick Start Guide

### Prerequisites
- **Python 3.10-3.11** (PyMC3 compatible; current venv uses 3.11)
- **Git** for version control
- **Windows PowerShell 5.1+**
- **NETS Database Snapshot** (REQUIRED - see Data Requirements section below)
- **API Keys**:
 - OpenAI API (GPT-4o-mini for business analysis)
 - Google Maps API (Places + Geocoding)
 - Outscraper API (unlimited review collection, optional but recommended)
 - LinkedIn credentials (optional, for employee validation)

### Installation (3 minutes)

```powershell
# 1. Clone repository
git clone https://github.com/McDonaldCrispyThigh/NETS-AI.git
cd NETS-AI

# 2. Activate existing virtual environment
.\AIAGENTNETS\Scripts\Activate.ps1

# 3. Install/update dependencies (if needed)
pip install -r requirements.txt

# 4. Check data requirements
python scripts/generate_sample_data.py

# 5. Prepare your NETS data files
# - Test data: tests/fixtures/nets_test_data.csv (5-20 records)
# - Production: data/raw/nets_minneapolis_full.csv (full dataset)
```

### Configuration

Create `.env` file in project root:

```env
# === REQUIRED API Keys ===
OPENAI_API_KEY=sk-proj-... # GPT-4o-mini for business analysis
GOOGLE_MAPS_API_KEY=AIza... # Google Maps Places API

# === RECOMMENDED (for unlimited reviews) ===
OUTSCRAPER_API_KEY=your_outscraper_key # 97% cheaper than Google Maps API
 # Get free trial: https://outscraper.com/

# === OPTIONAL (for employee validation) ===
LINKEDIN_EMAIL=your@email.com # LinkedIn scraper (90-sec timeout)
LINKEDIN_PASSWORD=your_password # Requires saved session file

# === Project Settings ===
DATA_PATH=./data
LOG_LEVEL=INFO
```

### Run Data Enhancement Pipeline

```powershell
# Test mode with minimal data
python scripts/run_pipeline.py --test

# Test mode with verbose output
python scripts/run_pipeline.py --test --verbose --validate

# Skip expensive operations for quick testing
python scripts/run_pipeline.py --test --skip employees survival

# Production run with your NETS data
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv

# Production with validation
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv --validate

# Skip external API calls in production
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv --skip gpt wayback linkedin

# Results:
# - Test output: data/processed/nets_test_output.parquet
# - Production: data/processed/nets_ai_minneapolis.parquet
# - Logs: logs/pipeline.log
```

### Command Line Options

**Pipeline Runner** (`scripts/run_pipeline.py`):
- `--test` - Run in test mode with minimal data
- `--input PATH` - Path to your NETS CSV file (required for production)
- `--skip OPERATIONS` - Skip specific operations: `employees`, `survival`, `gpt`, `wayback`, `linkedin`, `gmaps`
- `--validate` - Run data quality validation
- `--verbose` - Enable detailed logging
- `--naics CODES` - Target specific NAICS codes (default: 722513 446110)
- `--sample-size N` - Limit processing to N records for testing

**Examples**:
```bash
# Quick test without ML models
python scripts/run_pipeline.py --test --skip employees survival

# Process specific NAICS codes only
python scripts/run_pipeline.py --input data.csv --naics 722513 541511

# Sample 100 records for testing
python scripts/run_pipeline.py --input data.csv --sample-size 100
```

### Output Structure

**Parquet Output** (`data/processed/nets_test_output.parquet` or `nets_ai_minneapolis.parquet`):

Core columns (42 fields):
- **Identifiers**: `duns_id`, `company_name`, `place_id`
- **Location**: `latitude`, `longitude`, `street_address`, `city`, `state`, `zip_code`
- **Classification**: `naics_code`, `naics_title`, `sic_code`
- **Temporal**: `year_established`, `year_closed`
- **Employee Estimates**: 
  - `employee_count_raw` - Original NETS data
  - `employees_optimized` - Enhanced estimate with confidence intervals
  - `employees_lower_ci` / `employees_upper_ci` - 95% confidence bounds
- **Survival Detection**:
  - `is_active_prob` - Survival probability (0-1)
  - `confidence_level` - high/medium/low
- **Data Quality**: `data_quality_score` (0-100 composite metric)
- **Enrichment**: LinkedIn employee counts, review statistics, job posting data

**Data Requirements** (`scripts/generate_sample_data.py` shows complete schema):

Required columns in your NETS CSV:
```
duns_id, company_name, naics_code, naics_title, 
latitude, longitude, street_address, city, state, zip_code
```

Optional columns:
```
phone, website, year_established, year_closed, 
employee_count_raw, sic_code
```

---

## Pipeline Architecture

### Main Processing Pipeline

```
NETS CSV Input
  |
  v
Phase 1: Data Loading & Filtering
  - Load NETS database
  - Filter by NAICS codes (722513, 446110)
  - Filter by Minneapolis ZIP codes
  - Filter active establishments
  |
  v
Phase 2: Geospatial Processing
  - Create GeoDataFrame (EPSG:4326)
  - Validate coordinates
  - Spatial clustering
  |
  v
Phase 3: Employee Estimation (optional, --skip employees)
  - Bayesian hierarchical model
  - Multi-signal integration (LinkedIn, reviews, building area)
  - Bootstrap confidence intervals
  |
  v
Phase 4: Survival Detection (optional, --skip survival)
  - Review decay analysis
  - Job posting activity
  - Random forest classification
  - Probability scoring (0-1)
  |
  v
Phase 5: Quality Scoring
  - Data completeness metrics
  - Signal confidence weighting
  - Composite quality score (0-100)
  |
  v
Phase 6: Parquet Export
  - Optimized columnar format
  - Compressed storage
  - Schema validation
  |
  v
Output: Enhanced Parquet Database
```

### Flexible Execution Modes

**Test Mode** (`--test`):
- Uses small test dataset (5-20 records)
- Fast execution (< 30 seconds)
- Validates workflow without production data
- Output: `data/processed/nets_test_output.parquet`

**Production Mode** (default):
- Processes full NETS CSV
- All enhancement features
- Requires `--input` parameter
- Output: `data/processed/nets_ai_minneapolis.parquet`

**Skip Options** (`--skip`):
- `employees` - Skip ML-based employee estimation
- `survival` - Skip business survival detection
- `gpt` - Skip GPT analysis (future feature)
- `wayback` - Skip Wayback Machine validation
- `linkedin` - Skip LinkedIn data collection
- `gmaps` - Skip Google Maps enrichment

---

## Data Requirements

### Input Data Format

Your NETS CSV file must include these columns:

**Required Fields**:
```
duns_id              - Unique business identifier
company_name         - Business name
naics_code           - 6-digit NAICS code (e.g., "722513")
naics_title          - NAICS description
latitude             - GPS latitude
longitude            - GPS longitude
street_address       - Street address
city                 - City name
state                - 2-letter state code (e.g., "MN")
zip_code             - 5-digit ZIP code
```

**Optional Fields** (enhance estimation quality):
```
phone                - Phone number
website              - Website URL
year_established     - Year business was established
year_closed          - Year business closed (null if active)
employee_count_raw   - Raw employee count from NETS
sic_code             - SIC code
```

**Optional Enrichment Columns** (if available):
```
linkedin_employee_count   - Employee count from LinkedIn
review_count_3m           - Recent reviews (last 3 months)
review_count_6_12m        - Historical reviews (6-12 months ago)
last_review_date          - Most recent review date
job_postings_6m           - Recent job postings
estimated_area_sqm        - Building area in square meters
```

### Data File Locations

Run `python scripts/generate_sample_data.py` to see detailed requirements.

**Production Data**:
```
data/raw/nets_minneapolis_full.csv
```
- Full NETS dataset
- Expected: Thousands of records
- For actual analysis

**Test Data**:
```
tests/fixtures/nets_test_data.csv
```
- Small test subset
- Recommended: 5-20 records
- For quick workflow validation

### Target Industries

Current pipeline is optimized for:
- **NAICS 722513**: Limited-Service Restaurants (Quick Service)
- **NAICS 446110**: Pharmacies and Drug Stores

Custom NAICS codes can be specified with `--naics` parameter.

### Geographic Focus

**Minneapolis, Minnesota**:
- Target ZIP codes: 55401-55415
- Census tract boundaries
- Coordinate validation within city bounds
- Haversine distance <50m for matching

---

## Validation Strategy

### 1. Consistency Test (Reproducibility)
- Run pipeline 3 on same ZIP code
- Calculate Jaccard similarity: `|AB|/|AB|` for place_id sets
- **Target**: 0.95 similarity (current: 0.96-0.98 depending on timing)

### 2. External Validation
- **MN SOS Registry**: Cross-check active businesses (incorporation date)
- **OpenStreetMap**: Compare POI coverage (completeness metric)
- **Manual Ground Truth**: Field visit 50 random locations (precision/recall)

### 3. NETS Comparison
- **Interpolation**: Compare AI-BDD employee volatility (Gini) vs. NETS smoothness
- **Zombie Lag**: Closure detection time (AI-BDD: 3-6mo vs. NETS: 24+mo)
- **2011 Spikes**: Wayback validation of "opened 2011" flag artifacts
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
 employees_from_flow = peak_customers / 12.5 # 12.5 customers/staff
 
 estimate = avg(employees_from_reviews, employees_from_flow)
else:
 # Use full multi-signal model
 estimate = avg(linkedin, job_postings, building_area, 
 review_density, popular_times, sos_partners)
```

---

## Current Implementation Status

**Completed Features**:
- NETS data loading and filtering
- Geospatial processing with GeoDataFrame
- Bayesian employee estimation with confidence intervals
- Business survival detection (Random Forest)
- Multi-signal data integration
- Data quality scoring
- Parquet export with schema validation
- Test mode and skip options
- Command-line interface with flexible parameters
- Comprehensive documentation

**In Progress**:
- Minneapolis full dataset processing
- External API integrations (LinkedIn, Google Maps)
- Dashboard visualization enhancements
- Statistical validation notebooks

**Planned Features**:
- Computer Vision: Street View analysis
- OSM building footprint integration
- Additional NAICS code support
- Automated model retraining pipeline
- Real-time data updates

---

## Troubleshooting

### Common Issues

**"Test data not found"**
```bash
# Solution: Create test CSV file
python scripts/generate_sample_data.py  # Shows requirements
# Place your test CSV at: tests/fixtures/nets_test_data.csv
```

**"Input file required"**
```bash
# Solution: Use --test for testing or provide --input for production
python scripts/run_pipeline.py --test
# OR
python scripts/run_pipeline.py --input data/raw/your_file.csv
```

**"Missing required columns"**
```bash
# Solution: Check your CSV has all required columns
python scripts/generate_sample_data.py  # Shows required schema
```

**"Pipeline too slow"**
```bash
# Solution: Skip expensive operations
python scripts/run_pipeline.py --test --skip employees survival
# OR limit sample size
python scripts/run_pipeline.py --input data.csv --sample-size 100
```

**"Environment errors"**
```bash
# Solution: Validate environment
python scripts/validate_environment.py
# Reinstall dependencies if needed
pip install -r requirements.txt
```

### Getting Help

1. Check documentation in `docs/` folder
2. Run with `--verbose` flag for detailed logs
3. Review logs in `logs/` directory
4. Open GitHub issue with error details

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

**Documentation Version**: Jan 30, 2026 
**Repository**: https://github.com/McDonaldCrispyThigh/NETS-AI
**License**: MIT - see LICENSE file for details

