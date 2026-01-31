"""
NETS Business Data Enhancement System - Architecture Documentation
End-to-End Pipeline for Employee Estimation and Business Survival Detection
Minneapolis: Quick Service Restaurants (NAICS 722513) and Pharmacies (NAICS 446110)
"""

# NETS Business Data Enhancement System - Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Project Scope](#project-scope)
3. [Pipeline Architecture](#pipeline-architecture)
4. [Data Flow](#data-flow)
5. [Module Specifications](#module-specifications)
6. [Output Specifications](#output-specifications)
7. [Compliance and Quality Standards](#compliance-and-quality-standards)
8. [Quick Start Guide](#quick-start-guide)

---

## System Overview

**Project Name**: NETS Business Data Enhancement System 
**Geographic Focus**: Minneapolis, Minnesota (Census Tract boundaries) 
**Industry Focus**: NAICS 722513 (Quick Service Restaurants) and NAICS 446110 (Pharmacies) 
**Target Sample**: 500-1,000 establishments (MVP scale) 
**Output Format**: Apache Parquet database + Streamlit dashboard 

**Core Innovation**: Multi-source data fusion to:
1. Estimate employee counts with quantified uncertainty (95% confidence intervals)
2. Detect operational status earlier than traditional NETS updates (closure lag: 24+ months)
3. Provide local government and urban planners with real-time business intelligence

---

## Project Scope

### In Scope
- NETS database integration (primary establishment records)
- Google Maps reviews API (review velocity, recency)
- LinkedIn public company profiles (employee headcount)
- Indeed job postings (hiring activity)
- OpenStreetMap building footprints (store area)
- Street view imagery (facade visibility)
- Bayesian hierarchical modeling (employee estimation with CI)
- Random forest classification (survival probability)
- Parquet database export (versioned, compressed)
- Streamlit dashboard (interactive exploration)

### Out of Scope
- Web scraping personal data
- Storage of PII (personal identifiable information)
- Commercial use without NETS license compliance
- Real-time streaming (batch processing only)
- Proprietary ML models (open-source only)

---

## Pipeline Architecture

```
[-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 DATA INGESTION LAYER 
[|][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 NETS CSV Google Maps LinkedIn Indeed OpenStreetMap Street View 
 (baseline) (reviews) (employees) (jobs) (building area) (CV) 
[_][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 
[-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 DATA CLEANING & STANDARDIZATION 
[|][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 Address parsing (usaddress) 
 Coordinate normalization (EPSG:4326 WGS84) 
 Fuzzy name matching (fuzzywuzzy, threshold <50m haversine) 
 Temporal alignment (monthly periods) 
 Deduplication (multi-key: address + name + coordinates) 
[_][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 
[-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 FEATURE ENGINEERING LAYER 
[|][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 Review Features: 
 review_decay_rate = (count_3m/3) / (count_6_12m/6) 
 days_since_last_review (recency indicator) 
 review_sentiment_positive (if available) 
 
 Job Posting Features: 
 hiring_activity_ratio = recent_6m / historical_peak 
 posting_count_changes (trend) 
 
 Building Features: 
 building_area_sqm (from OSM footprints) 
 facade_width_m (OpenCV edge detection) 
 district_density (nearby establishments/sq km) 
[_][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 
[-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 MODELING & PREDICTION LAYER 
[|][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 Module 1: Employee Estimator (Bayesian) 
 Inputs: LinkedIn headcount, review velocity, building area 
 Method: Multi-signal ensemble + XGBoost regression 
 Outputs: point_estimate + ci_lower + ci_upper (95% CI) 
 Hierarchical priors by NAICS code 
 
 Module 2: Survival Detector (Random Forest) 
 Inputs: review decay, recency, job activity, street view 
 Method: Signal fusion with weighted scoring 
 Outputs: is_active_prob (0-1) + confidence_level 
 Risk/protective factor identification 
[_][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 
[-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 QUALITY ASSESSMENT & SCORING LAYER 
[|][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 Composite Quality Score (0-100): 
 Field completeness (20%): non-null ratio 
 Source diversity (20%): count of contributing sources 
 Signal confidence (30%): average model confidence 
 Estimate certainty (30%): inverse of CI width 
[_][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 
[-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 OUTPUT & VISUALIZATION LAYER 
[|][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
 Parquet Database: 
 Format: Apache Parquet (columnar, compressed) 
 Columns: NETS baseline + optimizations + confidence bounds 
 Partitioning: optional by NAICS code, zip code 
 
 Streamlit Dashboard: 
 Maps: Folium heatmaps (employees, survival probability) 
 Charts: Altair time series, distributions 
 Tables: Searchable/filterable establishment records 
 Export: CSV download for selected records 
[_][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-][-]
```

---

## Data Flow

### Phase 1: Data Loading (src/data/nets_loader.py)
```
NETS CSV
 
 [|][-] Filter by state (MN)
 [|][-] Filter by NAICS (722513, 446110)
 [|][-] Filter by ZIP codes (Minneapolis)
 [|][-] Filter by establishment year (2015+, optional)
 
 [_][-] Output: Pandas DataFrame (N records)
```

### Phase 2: External Data Integration (src/data/pipeline.py:enrich_with_external_sources)
```
LinkedIn Data match by DUNS_ID or company name
Outscraper Reviews match by place_id + name
Job Postings match by location + NAICS
OSM Building Footprints spatial join by lat/lon
Street View query Google API by coordinates

Merge strategy:
 Primary key: DUNS_ID (if available)
 Secondary key: fuzzy match (company_name + address)
 Spatial fallback: haversine distance <50m
```

### Phase 3: Feature Engineering
```
For each establishment:
 1. Extract review signals (if Outscraper data available)
 2. Calculate decay rate: (reviews_3m / 3) / (reviews_6_12m / 6)
 3. Extract job posting trends
 4. Retrieve building area from OSM
 5. Query street view for visual indicators

Result: Feature matrix ready for modeling
```

### Phase 4: Employee Estimation (src/models/bayesian_employee_estimator.py)
```
For each establishment:
 1. Check LinkedIn data (highest credibility)
 [_][-] If available: use directly + 10% CI margin
 
 2. Otherwise: ensemble of lower-priority signals
 [|][-] Review velocity: baseline * (recent_monthly / avg_monthly)
 [|][-] Building area: area_sqm * employees_per_sqm
 [|][-] Job postings: baseline * hiring_intensity_multiplier
 [_][-] Combine with weights: LinkedIn(50%) > Reviews(30%) > Area(15%) > Jobs(5%)
 
 3. Apply NAICS-specific constraints
 [_][-] Clamp between min_employees and max_employees
 
 4. Calculate confidence interval
 [_][-] Bootstrap resampling or PyMC posterior distribution
```

### Phase 5: Survival Detection (src/models/survival_detector.py)
```
For each establishment:
 1. Evaluate review recency
 [|][-] <30 days: strong positive signal (score=1.0)
 [|][-] 30-180 days: declining activity (score=0.4)
 [_][-] 180+ days: likely inactive (score=0.1)
 
 2. Calculate review decay rate
 [_][-] Trend of falling/stable/growing reviews
 
 3. Assess job posting activity
 [_][-] Active hiring = operational signal
 
 4. Street view analysis
 [_][-] Facade/signage visibility + lighting (evening hours)
 
 5. Weighted signal fusion
 [_][-] review_recency(35%) + decay(30%) + jobs(20%) + street_view(15%)
 
 6. Output: is_active_prob (0-1) + risk/protective factors
```

### Phase 6: Quality Scoring & Export
```
For each record:
 1. Calculate composite quality score (0-100)
 2. Prepare columns per PARQUET_OUTPUT_SCHEMA
 3. Add metadata (export date, source system)
 4. Write to Parquet format
 5. Create summary statistics
```

---

## Module Specifications

### 1. nets_loader.py
**Purpose**: Load and filter NETS establishment records

**Key Classes**:
- `NETSLoader`: Main loader with filter methods
- `NETSValidator`: Data quality checks

**Key Methods**:
```python
loader.load_raw() # Load CSV
loader.filter_by_state('MN') # State filter
loader.filter_by_naics_codes(['722513']) # Industry filter
loader.filter_by_zip_codes(['55401', ...]) # Geographic filter
loader.filter_active_only(year_threshold=2015) # Active establishments
loader.get_geopandas_gdf() # Convert to spatial format
loader.get_pipeline_ready(naics_codes, zip_codes) # Complete workflow
```

### 2. bayesian_employee_estimator.py
**Purpose**: Estimate employee counts with confidence intervals

**Key Classes**:
- `EmployeeEstimator`: Multi-signal ensemble estimator
- `EmployeeEstimate`: Result dataclass

**Key Methods**:
```python
estimator.estimate_from_linkedin(headcount)
estimator.estimate_from_review_velocity(count_3m, count_6_12m, naics)
estimator.estimate_from_building_area(area_sqm, naics)
estimator.estimate_from_job_postings(postings_6m, postings_peak, naics)
estimator.ensemble_estimate(estimates, weights)
estimator.estimate(record, linkedin_headcount, review_count_3m, ...)
estimator.process_batch(df, naics_code) # Batch processing
```

**Output Example**:
```python
EmployeeEstimate(
 duns_id='123456789',
 company_name='McDonald\'s (123 Main St)',
 point_estimate=18.5,
 ci_lower=15.2,
 ci_upper=22.1,
 confidence_level='high',
 estimation_method='xgboost',
 primary_signal='linkedin',
 signals_used=['linkedin', 'review_velocity', 'building_area']
)
```

### 3. survival_detector.py
**Purpose**: Detect business operational status and closure probability

**Key Classes**:
- `SurvivalDetector`: Multi-signal survival scorer
- `SurvivalEstimate`: Result dataclass

**Key Methods**:
```python
detector.calculate_review_decay_rate(count_3m, count_6_12m)
detector.evaluate_review_recency(last_review_date)
detector.evaluate_job_posting_activity(postings_6m, postings_peak)
detector.evaluate_street_view(facade_visible, signage_visible, lighting)
detector.score_survival(last_review_date, review_count_3m, ...)
detector.estimate(record, **signal_kwargs)
detector.process_batch(df)
```

**Output Example**:
```python
SurvivalEstimate(
 duns_id='123456789',
 company_name='McDonald\'s (123 Main St)',
 is_active_prob=0.87,
 confidence_level='high',
 last_review_date='2025-01-15',
 days_since_last_review=14,
 review_decay_rate=1.05,
 risk_factors=[''],
 protective_factors=['Recent review (14 days ago)', 'Active hiring'],
 primary_indicator='review_recency',
 signals_used=['review_recency', 'review_decay', 'job_postings']
)
```

### 4. pipeline.py
**Purpose**: Orchestrate complete data enhancement pipeline

**Key Class**: `NETSDataPipeline`

**Execution Workflow**:
```python
pipeline = NETSDataPipeline(
 nets_csv_path='data/raw/nets_minneapolis.csv',
 output_parquet_path='data/processed/nets_ai_minneapolis.parquet'
)

output_file = pipeline.run(
 linkedin_data='data/external/linkedin.csv',
 outscraper_data='data/external/outscraper_reviews.csv',
 job_postings_data='data/external/indeed_postings.csv'
)
```

---

## Output Specifications

### Parquet Database Schema

**File**: `data/processed/nets_ai_minneapolis.parquet`

**Format**: Apache Parquet with Snappy compression (default)

**Key Columns**:

#### Original NETS Fields (Preserved)
- `duns_id` (string, PRIMARY KEY)
- `company_name` (string)
- `street_address`, `city`, `state`, `zip_code` (string)
- `phone` (string)
- `website` (string)
- `latitude`, `longitude` (float, EPSG:4326)
- `naics_code` (string, 6-digit)

#### Geographic Enrichment
- `census_tract` (string): Census Tract FIPS code
- `census_block_group` (string): Block group identifier
- `coordinate_source` (string): 'original_nets', 'geocoded', 'clustered'
- `geocode_quality` (string): 'high', 'medium', 'low'

#### Employee Estimation
- `employees_optimized` (float): Point estimate
- `employees_ci_lower` (float): 2.5th percentile (95% CI)
- `employees_ci_upper` (float): 97.5th percentile (95% CI)
- `employees_estimation_method` (string): 'linkedin', 'xgboost', 'rule_based'
- `employees_confidence` (string): 'high', 'medium', 'low'
- `employee_data_sources` (string, JSON): Contributing source names

#### Business Survival
- `is_active_prob` (float): Probability of operational status (0-1)
- `is_active_confidence` (string): 'high', 'medium', 'low'
- `last_review_date` (string, ISO format): Latest customer review
- `days_since_last_review` (int): Recency in days
- `review_decay_rate` (float): Trend of review activity
- `hiring_activity_recent` (float): Recent job posting ratio
- `street_view_visible` (boolean): Operational visual indicators

#### Data Quality
- `data_quality_score` (int, 0-100): Composite quality metric
- `data_completeness` (float, 0-1): Field population ratio
- `signal_count` (int): Number of contributing data sources

#### Metadata
- `collection_date` (string, ISO format): Data collection date
- `data_sources_used` (string, JSON): List of sources integrated
- `data_export_date` (string, ISO format): Export timestamp
- `notes` (string, optional): Quality flags or warnings

**Example Row**:
```python
{
 'duns_id': '123456789',
 'company_name': 'McDonald\'s - Downtown',
 'street_address': '123 Main Street',
 'city': 'Minneapolis',
 'state': 'MN',
 'zip_code': '55401',
 'latitude': 44.9780,
 'longitude': -93.2650,
 'naics_code': '722513',
 'employees_optimized': 18.5,
 'employees_ci_lower': 15.2,
 'employees_ci_upper': 22.1,
 'employees_confidence': 'high',
 'is_active_prob': 0.87,
 'is_active_confidence': 'high',
 'last_review_date': '2025-01-15',
 'days_since_last_review': 14,
 'review_decay_rate': 1.05,
 'data_quality_score': 87,
 'data_sources_used': '["nets", "linkedin", "outscraper", "indeed"]',
 'data_export_date': '2025-01-29T15:30:00Z'
}
```

---

## Compliance and Quality Standards

### Data Privacy
- No storage of personal information
- Use of anonymized User-Agent for web scraping
- Compliance with Google TOS (non-commercial use)
- No linking to individual employee records

### API Usage
- Respect rate limits and quotas
- Implement exponential backoff for failed requests
- Log all API calls with timestamp and status code
- Track cumulative API costs

### Error Handling
- Try-except blocks for all external API calls
- Graceful fallback to secondary signals if primary unavailable
- Detailed error logging with context information
- Partial success (continue processing even if one signal fails)

### Data Quality
- Minimum thresholds for signal inclusion
- Validation of coordinate ranges (-90 to 90 latitude, -180 to 180 longitude)
- Check for impossible values (negative employee counts, etc.)
- Confidence level penalties for sparse data

### Performance
- Batch processing for >1000 records (use Dask)
- Caching of expensive API calls
- Vectorized operations where possible
- Progress reporting with tqdm

---

## Quick Start Guide

### Prerequisites
- Python 3.10+
- Conda or venv virtual environment
- API Keys: OpenAI (GPT analysis), Google Maps (optional)
- NETS CSV file in `data/raw/`

### Installation
```bash
# 1. Clone repository
git clone <repo_url>
cd NETS-AI

# 2. Create and activate environment
conda create -n nets-env python=3.10
conda activate nets-env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### Execution
```bash
# Method 1: Direct Python
python -c "
from src.data.pipeline import NETSDataPipeline
pipeline = NETSDataPipeline('data/raw/nets.csv')
pipeline.run()
"

# Method 2: Streamlit Dashboard
streamlit run dashboard/app.py
```

### Output Location
- **Parquet Database**: `data/processed/nets_ai_minneapolis.parquet`
- **Dashboard**: http://localhost:8501 (Streamlit default)
- **Logs**: `logs/` directory with timestamps

---

## Next Steps

1. **Integrate External Data Sources**
 - LinkedIn: Develop secure company profile scraper
 - Outscraper: Set up API account for unlimited reviews
 - Indeed: Job posting historical data pipeline
 - OSM: Download building footprints for Minneapolis

2. **Calibration & Validation**
 - Compare estimates vs. LinkedIn public data (if available)
 - Manual verification of 100 random establishments
 - Wayback Machine validation of establishment dates
 - Survival detection comparison vs. Google Maps "Permanently Closed" labels

3. **Production Deployment**
 - Cloud infrastructure (AWS S3 for data storage)
 - Scheduled daily/weekly updates
 - Error alerting and monitoring
 - Cost optimization (API budgets)

4. **Extended Capabilities**
 - Monthly time-series tracking (historical archive)
 - Network analysis (supply chain dependencies)
 - Real estate integration (lease expiration indicators)
 - Equity impact analysis (underserved neighborhood mapping)
