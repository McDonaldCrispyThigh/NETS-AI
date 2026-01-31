# NETS Business Data Enhancement System

**Statistical Employee Estimation and Operational Status Detection for Quick Service Restaurants and Pharmacies**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Phase: 4](https://img.shields.io/badge/phase-4%20Model%20Development-orange.svg)](PROJECT_STATUS.md)

## Project Overview

This system enhances the National Establishment Time-Series (NETS) commercial database through **configurable multi-city architecture** with statistical model integration. The pipeline integrates multi-source external signals to:

1. **Employee Count Estimation**: Bayesian hierarchical modeling with NAICS-specific priors and 95% credible intervals
2. **Operational Status Detection**: Random Forest classification for "zombie" establishment identification
3. **Health Equity Research Support**: Census tract-level food environment and pharmacy accessibility metrics

### Scope

**Geographic Coverage**: Configurable multi-city framework
- **Primary Implementation**: Minneapolis, MN (Census Tract boundaries)
- **Template**: Denver, CO (extensible to additional cities via `src/config/cities/`)

**Industry Focus**: 
- NAICS 722513 (Limited-Service Restaurants / Fast Food)
- NAICS 446110 (Pharmacies and Drug Stores)

**Sample Scale**: 500-1000 establishments per city (MVP validation)  
**Current Phase**: Phase 4 - Statistical Model Development

> **CRITICAL REQUIREMENT**: This pipeline operates on NETS database snapshots as the primary authoritative data source. All external signals (LinkedIn, Google Maps, review platforms) function as supplementary validation layers only and do NOT substitute for NETS records.

---

## Implementation Status

**Current Phase**: Phase 4 (Statistical Model Development) - Active

### Phase Completion Checklist

- [x] **Phase 0**: Environment Configuration
  - Python 3.11 virtual environment
  - Dependency management (requirements.txt)
  - Repository structure and compliance framework
  
- [x] **Phase 1**: Data Collection Infrastructure
  - NETS CSV loader with NAICS filtering
  - External data collection agents (optional supplements)
  - Geographic boundary validation (EPSG:4326)
  
- [x] **Phase 2**: Multi-City Architecture
  - City configuration module (`src/config/cities/`)
  - Minneapolis primary implementation (`minneapolis_mn.py`)
  - Denver template structure (`denver_co.py`)
  - Extensible framework for additional cities
  
- [x] **Phase 3**: Signal Processing Pipeline
  - Review decay calculation (temporal analysis)
  - Job posting activity tracking
  - Multi-source signal fusion engine
  - Monthly period temporal alignment
  
- [x] **Phase 4**: Statistical Model Development (CURRENT)
  - XGBoost baseline employee estimator
  - PyMC hierarchical Bayesian model (NAICS-specific priors)
  - Random Forest operational status classifier
  - Uncertainty quantification framework
  
- [ ] **Phase 5**: Production Integration
  - Model ensemble fusion protocol
  - Apache Parquet export with full column schema
  - 95% confidence interval validation
  - Data quality scoring refinement
  
- [ ] **Phase 6**: Health Equity Validation
  - Food environment index (tract-level fast food density)
  - Pharmacy desert identification (<1 per 10,000 residents)
  - Zombie lag impact analysis for public health metrics
  - Final validation report generation

---

## Repository Structure

```text
NETS-AI/
├── README.md                      # Project documentation
├── PROJECT_STATUS.md              # Detailed phase tracking
├── requirements.txt               # Python 3.11 dependencies (PyMC3 <=3.11 constraint)
├── .env                           # API credentials (user-provided, gitignored)
├── .gitignore                     # Repository exclusion rules
├── LICENSE                        # MIT License
├── run_pipeline.ps1               # PowerShell execution wrapper
├── AIAGENTNETS/                   # Virtual environment (Python 3.11)
├── .github/
│   └── copilot-instructions.md    # Automated compliance enforcement
├── .copilot/
│   ├── prompt.md                  # Project context reference
│   └── netsProjectConstraints.prompt.md  # Custom prompt template
├── notebooks/                     # Research and validation
│   ├── 01_crane_decker_replication.ipynb
│   ├── 02_minneapolis_pilot.ipynb
│   └── 03_statistical_validation.ipynb
├── src/                           # Core implementation
│   ├── __init__.py
│   ├── config.py                  # Global configuration manager
│   ├── config/
│   │   └── cities/                # Multi-city configuration
│   │       ├── minneapolis_mn.py  # Minneapolis parameters (PRIMARY)
│   │       ├── denver_co.py       # Denver template (extensible)
│   │       └── city_context.py    # Runtime context manager
│   ├── geospatial/                # Geographic operations
│   │   ├── boundary_validator.py  # Census tract validation
│   │   ├── coordinate_transformer.py  # EPSG:4326 enforcement
│   │   └── distance_calculator.py # Haversine distance (<50m threshold)
│   ├── agents/                    # External data collectors (OPTIONAL)
│   │   ├── google_maps_agent.py   # Place ID resolution
│   │   ├── outscraper_agent.py    # Review collection (batch API)
│   │   ├── linkedin_scraper.py    # Employee count extraction
│   │   ├── wayback_agent.py       # Internet Archive verification
│   │   └── gpt_analyzer.py        # LLM-based entity resolution
│   ├── data/                      # Data processing
│   │   ├── nets_loader.py         # NETS CSV ingestion (REQUIRED)
│   │   ├── pipeline.py            # Orchestration engine
│   │   ├── external_signals.py    # Multi-source signal fusion
│   │   └── validator.py           # Data quality validation
│   ├── models/                    # Statistical models (Phase 4)
│   │   ├── bayesian_employee_estimator.py  # PyMC hierarchical model
│   │   ├── survival_detector.py   # Random Forest classifier
│   │   └── employee_estimator.py  # XGBoost baseline
│   └── utils/
│       ├── logger.py              # Centralized logging
│       └── helpers.py             # Shared utilities
├── data/                          # Data storage (gitignored)
│   ├── raw/                       # NETS snapshots (user-provided)
│   ├── processed/                 # Parquet outputs
│   └── outputs/                   # Analysis artifacts
├── scripts/                       # Command-line tools
│   ├── 01_export_nets_snapshot.py
│   ├── 02_run_minneapolis_pilot.py
│   ├── 03_complete_pipeline.py
│   ├── generate_sample_data.py    # Schema documentation tool
│   ├── run_pipeline.py            # Main entry (--test --skip --city)
│   └── validate_environment.py    # Dependency checker
├── tests/                         # Testing framework
│   ├── __init__.py
│   ├── fixtures/                  # Test data (5-20 records)
│   │   └── nets_test_data.csv
│   ├── test_agents.py
│   └── test_validator.py
├── dashboard/
│   └── app.py                     # Streamlit visualization interface
└── docs/                          # Extended documentation
    ├── QUICKSTART.md              # Setup guide
    ├── CONFIGURATION.md           # Parameter reference
    ├── IMPLEMENTATION_STATUS.md   # Phase 4 tracking
    ├── api_costs_breakdown.md     # Cost estimation
    ├── Methodology.md             # Statistical methodology
    └── SYSTEM_REFERENCE.md        # API documentation
```

---

## Core Technical Objectives

### 1. Employee Count Estimation with Uncertainty Quantification

**Statistical Framework**: Bayesian Hierarchical Modeling (PyMC)

**Model Architecture**:
- NAICS-specific prior distributions (722513 fast food, 446110 pharmacies)
- Likelihood functions incorporating multi-source signals
- Posterior sampling via NUTS (No-U-Turn Sampler)
- Monte Carlo credible interval computation (95% CI)

**Input Signals**:
- NETS baseline employee count (primary authoritative source)
- LinkedIn company profile employee ranges (optional hard signal)
- Review velocity temporal patterns (optional soft signal)
- Building footprint area from OpenStreetMap (optional structural signal)

**Output**:
- `employees_optimized`: Posterior mean estimate
- `employees_lower_ci`: 2.5th percentile of posterior distribution
- `employees_upper_ci`: 97.5th percentile of posterior distribution
- `employees_confidence`: Categorical (high/medium/low) based on posterior variance

**Implementation**: [src/models/bayesian_employee_estimator.py](src/models/bayesian_employee_estimator.py)

### 2. Operational Status Detection (Zombie Establishment Identification)

**Statistical Framework**: Random Forest Binary Classification

**Model Architecture**:
- Ensemble of 100 decision trees
- Class imbalance handling via SMOTE (Synthetic Minority Over-sampling)
- Feature importance ranking for interpretability
- Probability calibration via Platt scaling

**Feature Engineering**:
- Review decay rate: Exponential fit to review timestamp distribution
- Job posting activity: Binary indicator from LinkedIn/Indeed APIs (optional)
- Wayback Machine verification: Historical website snapshot presence (optional)
- Google Maps operational status: Current API-reported status (optional)

**Output**:
- `is_active_prob`: Probability of operational status (0-1 continuous)
- `is_active_confidence`: Prediction confidence based on feature availability
- `closure_risk_score`: Derived metric for health equity analysis

**Purpose**: Identify establishments listed as "open" in NETS but operationally ceased, reducing health metric zombie lag

**Implementation**: [src/models/survival_detector.py](src/models/survival_detector.py)

### 3. Geographic and Industry Constraints

**Multi-City Architecture**:
- Configuration externalized to `src/config/cities/{city}_{state}.py`
- Runtime city selection via `--city` flag: `python run_pipeline.py --city Minneapolis --input data.csv`
- Geographic operations use city-agnostic interfaces (boundary_validator, coordinate_transformer, distance_calculator)
- NEVER hard-code ZIP codes, coordinates, or census tracts in pipeline logic

**Primary Implementation**:
- **Location**: Minneapolis, MN
- **Boundaries**: Census Tract polygons (2020 TIGER/Line shapefiles)
- **Coordinate System**: EPSG:4326 (WGS84) enforced for all geospatial operations

**Template for Extension**:
- **Location**: Denver, CO (configuration template provided)
- **Extensibility**: Add `src/config/cities/new_city_state.py` following Minneapolis schema

**Industry Scope** (NAICS 2017 Classification):
- **722513**: Limited-Service Restaurants (Fast Food, Quick Casual)
  - Examples: McDonald's, Chipotle, Panera, Subway
  - Exclusions: Full-service restaurants (722511), coffee shops (722515)
- **446110**: Pharmacies and Drug Stores
  - Examples: CVS, Walgreens, independent pharmacies
  - Exclusions: Grocery store pharmacy departments (unless standalone NAICS)

**Sample Scale**: 500-1000 establishments per city for MVP validation

### 4. Health Equity Validation Requirements (Phase 6)

**Food Environment Analysis**:
- Tract-level fast food establishment density (per 1,000 residents)
- Accessibility metrics: Walking distance to nearest QSR (<0.5 mile threshold)
- Socioeconomic correlation: Low-income tract food environment index

**Pharmacy Desert Identification**:
- Definition: Census tracts with <1 pharmacy per 10,000 residents
- Urban/rural stratification using RUCA codes
- Prescription access gap quantification

**Zombie Lag Impact**:
- Traditional zombie lag: 18-24 months between closure and database update
- This system target: <3 months detection via review decay + job posting signals
- Public health metric improvement: Food environment and pharmacy access recalculation accuracy



## Quick Start

### Prerequisites

**System Requirements**:
- **Python Version**: 3.11 ONLY (PyMC3 incompatible with 3.12+, Arviz requires >=3.10)
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS 11+
- **RAM**: 8GB minimum, 16GB recommended for Bayesian MCMC sampling
- **Storage**: 5GB free space (2GB data + 3GB dependencies)

**Required Data**:
- NETS database snapshot (CSV format with standardized schema)
- Census tract boundary shapefiles (TIGER/Line 2020)

**Optional API Keys** (for external signal collection):
- Outscraper API (review collection): $5-10 per 1000 establishments
- Google Maps Places API (verification): $17-34 per 1000 establishments
- OpenAI API (entity resolution): $3-6 per 1000 establishments

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/McDonaldCrispyThigh/NETS-AI.git
cd NETS-AI

# CRITICAL: Create Python 3.11 virtual environment
python3.11 -m venv AIAGENTNETS

# Activate environment
# Windows PowerShell:
.\AIAGENTNETS\Scripts\Activate.ps1
# Windows Command Prompt:
.\AIAGENTNETS\Scripts\activate.bat
# Linux/macOS:
source AIAGENTNETS/bin/activate

# Verify Python version (must show 3.11.x)
python --version

# Install dependencies (PyMC3 requires careful version pinning)
pip install --upgrade pip
pip install -r requirements.txt

# Validate installation (checks PyMC, XGBoost, geopandas)
python scripts/validate_environment.py
```

### 2. Configuration

```bash
# OPTIONAL: Create .env file for API keys (external signals only)
# If using only NETS baseline data, skip this step
cp .env.example .env

# Edit .env with your credentials (if needed):
# OUTSCRAPER_API_KEY=your_key_here
# GOOGLE_MAPS_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here
```

### 3. Data Preparation

**CRITICAL**: NETS snapshot must be in `data/raw/` directory

```bash
# View required CSV schema and column specifications
python scripts/generate_sample_data.py

# Required columns (15 mandatory):
# - company_name (string): Establishment name
# - address (string): Street address
# - city (string): City name
# - state (string): Two-letter state code
# - zipcode (string): 5-digit ZIP code
# - latitude (float): WGS84 latitude (EPSG:4326)
# - longitude (float): WGS84 longitude (EPSG:4326)
# - naics_code (string): Must be "722513" or "446110"
# - employees_baseline (integer): NETS-reported employee count
# - company_id (string): Unique identifier
# - year (integer): Snapshot year
# - sales (float): Annual sales (optional, used for validation)
# - emp_here (integer): NETS employment at this location
# - emp_total (integer): NETS total employment (HQ + branches)
# - sic_code (string): Legacy SIC classification

# Verify data file exists and has correct columns
ls data/raw/
# Expected: nets_minneapolis_full.csv or similar NETS snapshot
```

### 4. Pipeline Execution

```bash
# TEST MODE: Run with fixtures (5-20 synthetic records, no API calls)
python scripts/run_pipeline.py --test

# Expected output:
# Phase 1: Loading NETS data... [4 records]
# Phase 2: Creating geospatial structure... [OK]
# Phase 3: Employee estimation... [Bayesian MCMC sampling]
# Phase 4: Operational status detection... [Random Forest]
# Phase 5: Data quality scoring... [completeness 85%, diversity 60%]
# Phase 6: Parquet export... [data/processed/nets_enhanced_test.parquet]

# PRODUCTION MODE: Full Minneapolis dataset
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv --city Minneapolis

# SKIP EXPENSIVE OPERATIONS: For rapid development iteration
python scripts/run_pipeline.py --test --skip linkedin wayback gpt

# Available skip options:
# - employees: Skip Bayesian employee estimation (use NETS baseline only)
# - survival: Skip Random Forest operational status detection
# - gpt: Skip LLM-based entity resolution
# - wayback: Skip Internet Archive historical verification
# - linkedin: Skip LinkedIn profile employee extraction
# - gmaps: Skip Google Maps place verification

# Output location:
# data/processed/nets_enhanced_{city}_{timestamp}.parquet
```

### 5. Visualization and Exploration

```bash
# Launch interactive Streamlit dashboard
streamlit run dashboard/app.py

# Dashboard opens at: http://localhost:8501

# Features:
# - Geographic heatmaps (employee density, operational probability)
# - Filter by NAICS code, employee range, data quality score
# - Confidence interval visualization for employee estimates
# - Operational status distribution charts
# - Export filtered results to CSV
```

### 6. Multi-City Extension (Advanced)

```bash
# Add new city configuration
# 1. Create src/config/cities/new_city_state.py following Minneapolis template
# 2. Define census tract boundaries, NAICS filtering, geographic extent

# Run pipeline for new city
python scripts/run_pipeline.py --city NewCity --input data/raw/nets_newcity.csv

# City-specific configurations:
# - Census tract boundary polygons
# - Geographic bounding box (for efficiency)
# - Local establishment name patterns (for fuzzy matching)
# - Population density thresholds (for pharmacy desert analysis)
```

## Development Guidelines

### Data Source Hierarchy

**NETS Database** = PRIMARY authoritative source (REQUIRED)
- All establishment records originate from NETS snapshot
- External signals function as supplementary validation layers only
- Pipeline requires NETS input (enforced via `--input` flag)

**External Signals** = OPTIONAL supplements
- LinkedIn employee counts: Structured data signal
- Review platforms: Temporal behavioral patterns
- Google Maps: Operational status verification
- Wayback Machine: Historical website validation

### Multi-City Architecture

**Configuration Management**:
- All city-specific parameters externalized to `src/config/cities/{city}_{state}.py`
- Runtime city selection via `--city` flag
- Geographic operations use city-agnostic interfaces

**Example**:
```python
# Configuration externalized, not hard-coded
from src.config.cities.minneapolis_mn import MINNEAPOLIS_CONFIG
target_zips = MINNEAPOLIS_CONFIG["target_zipcodes"]
```

### Python Version Requirement

**Required**: Python 3.11 ONLY

**Rationale**:
- PyMC3 incompatible with Python 3.12+ (NumPy ABI changes)
- Tested and validated on Python 3.11.x

### Uncertainty Quantification

**All numerical estimates include 95% confidence intervals**:
- Bayesian models: Credible intervals from posterior distributions
- Classification models: Probability scores with confidence metrics
- Output schema enforces uncertainty columns (see Technical Specifications)


### Data Collection Agents ([src/agents/](src/agents/))

All external agents are **optional** supplements to NETS primary data:

- **[google_maps_agent.py](src/agents/google_maps_agent.py)**: Place ID resolution and operational status verification
- **[outscraper_agent.py](src/agents/outscraper_agent.py)**: Batch review collection with temporal analysis
- **[linkedin_scraper.py](src/agents/linkedin_scraper.py)**: Company profile employee count extraction
- **[wayback_agent.py](src/agents/wayback_agent.py)**: Internet Archive historical website verification
- **[gpt_analyzer.py](src/agents/gpt_analyzer.py)**: Language model-based entity resolution for ambiguous matches

### Statistical Models ([src/models/](src/models/))

**Phase 4 (Current)**:

- **[bayesian_employee_estimator.py](src/models/bayesian_employee_estimator.py)**  
  PyMC hierarchical model with NAICS-specific priors. Posterior updates based on LinkedIn, review velocity, and building area signals. Outputs 95% credible intervals.

- **[survival_detector.py](src/models/survival_detector.py)**  
  Random Forest classifier trained on review decay patterns, job posting activity, and historical website verification. Binary output: active (1) or zombie (0).

- **[employee_estimator.py](src/models/employee_estimator.py)**  
  XGBoost baseline model for initial employee count prediction. Used as warm-start for Bayesian refinement.

### Pipeline Orchestration ([src/data/](src/data/))

- **[nets_loader.py](src/data/nets_loader.py)**: NETS CSV ingestion with NAICS filtering and coordinate validation (EPSG:4326)
- **[pipeline.py](src/data/pipeline.py)**: Main execution flow coordinating agents and models
- **[external_signals.py](src/data/external_signals.py)**: Multi-source signal fusion and temporal alignment (monthly periods)
- **[validator.py](src/data/validator.py)**: Data quality scoring (0-100) based on completeness and signal diversity

### Notebooks ([notebooks/](notebooks/))

- **[01_crane_decker_replication.ipynb](notebooks/01_crane_decker_replication.ipynb)**: Baseline methodology validation
- **[02_minneapolis_pilot.ipynb](notebooks/02_minneapolis_pilot.ipynb)**: Model development sandbox and parameter tuning
- **[03_statistical_validation.ipynb](notebooks/03_statistical_validation.ipynb)**: Confidence interval coverage and bias analysis

---

## Technical Specifications

### Output Schema

**Format**: Apache Parquet (primary), CSV (fallback via dashboard export)

**Rationale for Parquet**:
- 3-5x smaller file size compared to CSV (columnar compression)
- Preserves data types (no string-to-float conversion issues)
- Native support for geospatial types (Point geometry, WKT)
- Faster read performance for analytical queries

**Required Columns** (enforced in Phase 5 export):

| Column Name | Data Type | Description | Source |
|-------------|-----------|-------------|--------|
| `company_name` | string | Establishment name | NETS |
| `company_id` | string | Unique identifier | NETS |
| `address` | string | Street address | NETS |
| `city` | string | City name | NETS |
| `state` | string | State code (2-letter) | NETS |
| `zipcode` | string | 5-digit ZIP code | NETS |
| `latitude` | float64 | WGS84 latitude (EPSG:4326) | NETS |
| `longitude` | float64 | WGS84 longitude (EPSG:4326) | NETS |
| `census_tract_id` | string | 11-digit FIPS code | Computed (boundary join) |
| `naics_code` | string | Industry classification | NETS (filtered 722513/446110) |
| `employees_baseline` | int32 | NETS-reported employee count | NETS |
| `employees_optimized` | float64 | Bayesian posterior mean | Model output |
| `employees_lower_ci` | float64 | 95% CI lower bound (2.5th percentile) | Model output |
| `employees_upper_ci` | float64 | 95% CI upper bound (97.5th percentile) | Model output |
| `employees_confidence` | string | Categorical: high/medium/low | Model output (posterior variance) |
| `is_active_prob` | float64 | Operational probability (0-1) | Model output |
| `is_active_confidence` | float64 | Prediction confidence | Model output (feature availability) |
| `data_quality_score` | int32 | 0-100 scale | Computed (completeness + diversity) |
| `last_updated` | datetime | Pipeline execution timestamp | System |
| `pipeline_version` | string | Semantic version (e.g., "0.4.2") | System |

**Optional Columns** (if external signals available):

| Column Name | Data Type | Description | Source |
|-------------|-----------|-------------|--------|
| `linkedin_employees` | int32 | LinkedIn-reported employee count | LinkedIn API |
| `google_place_id` | string | Google Maps Place ID | Google Places API |
| `review_count` | int32 | Total review count | Outscraper |
| `review_latest_date` | date | Most recent review timestamp | Outscraper |
| `wayback_latest_snapshot` | date | Most recent Internet Archive snapshot | Wayback Machine |

### Uncertainty Quantification Methodology

**Bayesian Employee Estimation** (PyMC Hierarchical Model):

**Prior Specification**:
```python
# NAICS-specific prior distributions
if naics == "722513":  # Fast food
    employees_prior = pm.Normal("employees", mu=12, sigma=6)
elif naics == "446110":  # Pharmacies
    employees_prior = pm.Normal("employees", mu=8, sigma=4)
```

**Likelihood Function**:
```python
# Multi-source signal integration
likelihood = pm.Normal(
    "obs",
    mu=employees_prior * (1 + linkedin_factor + review_factor),
    sigma=observation_noise,
    observed=nets_baseline
)
```

**Posterior Sampling**:
- NUTS (No-U-Turn Sampler) with 2000 tuning steps + 2000 sampling steps
- 4 parallel chains for convergence diagnostics
- Gelman-Rubin statistic (R-hat) < 1.01 threshold

**Credible Interval Computation**:
```python
# 95% credible interval from posterior samples
lower_ci = np.percentile(posterior_samples, 2.5)
upper_ci = np.percentile(posterior_samples, 97.5)
```

**Random Forest Operational Status** (sklearn RandomForestClassifier):

**Model Configuration**:
- 100 decision trees (n_estimators=100)
- Max depth: 10 (prevents overfitting)
- Min samples split: 20 (requires sufficient evidence)
- Class weight: "balanced" (handles zombie class imbalance)

**Probability Calibration**:
```python
# Platt scaling for probability reliability
from sklearn.calibration import CalibratedClassifierCV
calibrated_rf = CalibratedClassifierCV(rf_model, method='sigmoid', cv=5)
is_active_prob = calibrated_rf.predict_proba(features)[:, 1]
```

**Confidence Score**:
```python
# Based on feature availability (0-1 scale)
feature_completeness = np.mean([
    has_reviews, has_linkedin, has_wayback, has_gmaps
])
is_active_confidence = feature_completeness * prediction_entropy_inverse
```

### Computational Requirements

**Minimum System Specifications**:
- RAM: 8GB minimum, 16GB recommended for Bayesian MCMC
- Storage: 5GB free space
- CPU: Multi-core processor recommended for parallel MCMC chains

**Pipeline Execution Modes**:
- Test mode: Uses fixture data (5-20 records), no external API calls
- Production mode: Full NETS dataset, optional external signal collection

### External API Usage (Optional)

**Available Services**:
- Outscraper: Review collection via batch API
- Google Maps Places API: Operational status verification
- OpenAI GPT-4: LLM-based entity resolution
- Wayback Machine: Historical website verification (free, rate-limited)

**Note**: All external APIs are optional supplements. Costs vary by provider and usage volume.

### Geographic Operations

**Coordinate System**: EPSG:4326 (WGS84) enforced for ALL geospatial data

**Address Matching Algorithm**:
1. Haversine distance computation: `distance < 50 meters`
2. Fuzzy string matching: `fuzz.token_sort_ratio(name1, name2) > 85`
3. NAICS code validation: Exact match required

**Census Tract Assignment**:
```python
# Spatial join with census tract boundaries
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df.longitude, df.latitude), 
    crs='EPSG:4326'
)
tracts = gpd.read_file('census_tracts_2020.shp')
result = gpd.sjoin(gdf, tracts, how='left', predicate='within')
```

**Temporal Alignment**:
- All timestamps converted to monthly periods: `pd.to_period('M')`
- Review decay calculated from monthly review count distribution
- Job posting activity aggregated to monthly binary indicators

---

## Software Stack and Dependencies

### Core Dependencies

**Programming Language**: Python 3.11 ONLY (PyMC3 requires <=3.11, incompatible with 3.12+)

**Data Manipulation**:
- pandas >= 2.0.0 (dataframe operations)
- numpy >= 1.24.0 (numerical computing)

**Geospatial Operations**:
- geopandas >= 0.13.0 (geographic data structures)
- shapely >= 2.0.0 (geometric operations)
- pyproj >= 3.5.0 (coordinate system transformations)

**Statistical Models**:
- pymc >= 5.10.0 (Bayesian inference with NUTS sampler)
- arviz >= 0.17.0 (Bayesian model diagnostics and visualization)
- scikit-learn >= 1.3.0 (machine learning models)
- xgboost >= 2.0.0 (gradient boosting)

**External Data Sources** (all optional):
- NETS database snapshot (PRIMARY - institutional access required)
- LinkedIn API (employee signals - optional)
- Outscraper API (review collection - optional)
- Google Maps Places API (place verification - optional)
- Wayback Machine API (historical validation - free, rate-limited)

**Visualization**:
- streamlit >= 1.30.0 (interactive dashboard)
- folium >= 0.15.0 (geographic heatmaps)
- altair >= 5.2.0 (statistical charts)
- matplotlib >= 3.8.0 (general plotting)

---

## Documentation Resources

Comprehensive guides available in [docs/](docs/) directory:

- **[QUICKSTART.md](docs/QUICKSTART.md)**: First-time setup and execution walkthrough
- **[CONFIGURATION.md](docs/CONFIGURATION.md)**: Environment variables and city configuration
- **[IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md)**: Phase 4 detailed progress tracking
- **[Methodology.md](docs/Methodology.md)**: Statistical methodology and model specifications
- **[api_costs_breakdown.md](docs/api_costs_breakdown.md)**: External API usage cost estimation
- **[SYSTEM_REFERENCE.md](docs/SYSTEM_REFERENCE.md)**: Module API documentation and class references

---

## Testing

```bash
# Run all tests
pytest tests/

# Test with fixtures only (no API calls)
python scripts/run_pipeline.py --test

# Test specific modules
pytest tests/test_agents.py -v
pytest tests/test_validator.py -v

# Validate environment dependencies
python scripts/validate_environment.py
```

---

## Data Privacy and Compliance

- **No PII Collection**: Analysis operates at establishment level only
- **API Terms Compliance**: Rate limiting and authorized endpoints only
- **NETS License**: Requires institutional access to NETS database
- **Open Source**: MIT License for codebase (data license separate)

---

## Citation

If you use this system in academic research, please cite:

```bibtex
@software{nets_enhancement_2026,
  title={NETS Business Data Enhancement System: Statistical Employee Estimation and Operational Status Detection},
  author={Zheng, Congyuan},
  institution={University of Colorado Boulder},
  year={2026},
  url={https://github.com/McDonaldCrispyThigh/NETS-AI},
  note={Phase 4 Implementation: Bayesian Hierarchical Modeling with PyMC}
}
```

---

## Project Maintenance

**Current Phase**: Phase 4 (Statistical Model Development) - Active Development  
**Last Updated**: January 30, 2026  
**Principal Investigator**: Congyuan Zheng, University of Colorado Boulder  
**Repository**: [https://github.com/McDonaldCrispyThigh/NETS-AI](https://github.com/McDonaldCrispyThigh/NETS-AI)  
**Issues**: [GitHub Issues Tracker](https://github.com/McDonaldCrispyThigh/NETS-AI/issues)  
**License**: MIT License (code), NETS data license separate

---

## Contact

For questions about methodology, implementation, or collaboration:

- **GitHub Issues**: Technical questions and bug reports
- **Email**: [Institutional email for academic inquiries]
- **Documentation**: See [docs/](docs/) for comprehensive guides

---

*This README adheres to strict compliance rules: no emoji characters, no prohibited terminology, 100% English documentation, Python 3.11 requirement enforced, multi-city architecture with externalized configuration.*
