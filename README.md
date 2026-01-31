# NETS Business Data Enhancement System

**Employee Estimation and Survival Detection for Minneapolis Quick Service Restaurants and Pharmacies**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Project Overview

This system enhances the National Establishment Time-Series (NETS) commercial database by integrating multi-source signals to:
1. **Estimate employee counts** with quantified uncertainty (95% confidence intervals)
2. **Detect operational status** ("zombie" establishments listed as open but inactive)
3. **Support health equity research** through food environment and pharmacy access analysis

**Geographic Scope**: Minneapolis, MN (Census Tract boundaries)  
**Industry Focus**: NAICS 722513 (Limited-Service Restaurants / Fast Food) and 446110 (Pharmacies)  
**Sample Scale**: 500-1000 establishments (MVP)  
**Current Phase**: Phase 4 - Model Development (see Implementation Status below)

> **CRITICAL**: This pipeline REQUIRES a NETS database snapshot as primary input. External sources (LinkedIn, Google Maps, reviews) supplement but do NOT replace NETS records.

---

## Implementation Status

**Phase 4 (Model Development) - In Progress**

- [x] Phase 0: Environment setup and NETS ingestion
- [x] Phase 1: Data collection infrastructure (agents)
- [x] Phase 2: Geographic boundary validation
- [x] Phase 3: Signal extraction pipeline
- [x] Phase 4: Employee estimation (XGBoost + PyMC hierarchical prior)
- [x] Phase 4: Survival detection (Random Forest on review decay)
- [ ] Phase 5: Signal fusion and Parquet export with full uncertainty quantification
- [ ] Phase 6: Health equity validation (food environment index, pharmacy deserts)

---

## Repository Structure

```text
NETS-AI/
├── README.md                      # Project overview and quickstart
├── requirements.txt               # Python 3.11 dependencies
├── .env                           # API keys (user-provided, gitignored)
├── .gitignore                     # Git exclusion rules
├── LICENSE                        # MIT License
├── run_pipeline.ps1               # PowerShell pipeline wrapper
├── AIAGENTNETS/                   # Virtual environment (Python 3.11)
├── .github/
│   └── copilot-instructions.md    # Automated constraint enforcement
├── notebooks/                     # Research and validation notebooks
│   ├── 01_crane_decker_replication.ipynb
│   ├── 02_minneapolis_pilot.ipynb
│   └── 03_statistical_validation.ipynb
├── src/                           # Core source code
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── agents/                    # External data collection agents
│   │   ├── google_maps_agent.py   # Place ID resolution (optional)
│   │   ├── outscraper_agent.py    # Review collection (optional)
│   │   ├── linkedin_scraper.py    # Employee signals (optional)
│   │   ├── wayback_agent.py       # Historical verification (optional)
│   │   └── gpt_analyzer.py        # Language model analysis (optional)
│   ├── data/                      # Data processing modules
│   │   ├── nets_loader.py         # NETS CSV ingestion (REQUIRED)
│   │   ├── pipeline.py            # Orchestration logic
│   │   ├── external_signals.py    # Multi-source signal fusion
│   │   └── validator.py           # Data quality validation
│   ├── models/                    # Statistical models (Phase 4)
│   │   ├── bayesian_employee_estimator.py  # PyMC hierarchical model
│   │   ├── survival_detector.py   # Random Forest closure detection
│   │   └── employee_estimator.py  # XGBoost baseline estimator
│   └── utils/
│       ├── logger.py              # Centralized logging
│       └── helpers.py             # Shared utilities
├── data/                          # Data storage (gitignored)
│   ├── raw/                       # NETS snapshots (user-provided)
│   ├── processed/                 # Parquet outputs with CI columns
│   └── outputs/                   # Figures and analysis results
├── scripts/                       # Command-line scripts
│   ├── 01_export_nets_snapshot.py
│   ├── 02_run_minneapolis_pilot.py
│   ├── 03_complete_pipeline.py
│   ├── generate_sample_data.py    # Data requirements documentation
│   ├── run_pipeline.py            # Main entry point (--test --skip)
│   └── validate_environment.py    # Dependency checker
├── tests/                         # Testing suite
│   ├── __init__.py
│   ├── fixtures/                  # Test data (5-20 records)
│   │   └── nets_test_data.csv
│   ├── test_agents.py
│   └── test_validator.py
├── dashboard/
│   └── app.py                     # Streamlit interactive visualization
└── docs/                          # Extended documentation
    ├── QUICKSTART.md              # Getting started guide
    ├── CONFIGURATION.md           # Configuration reference
    ├── IMPLEMENTATION_STATUS.md   # Phase tracking
    ├── api_costs_breakdown.md     # API usage estimation
    ├── Methodology.md             # Statistical methodology
    └── SYSTEM_REFERENCE.md        # API documentation
```

---

## Core Objectives

### 1. Employee Count Estimation
- **Model**: Bayesian Hierarchical (PyMC) with NAICS-specific priors
- **Inputs**: NETS baseline, LinkedIn employee counts (optional), review velocity (optional), building area (optional)
- **Output**: Point estimates with 95% confidence intervals (employees_optimized, employees_lower_ci, employees_upper_ci)
- **Implementation**: [src/models/bayesian_employee_estimator.py](src/models/bayesian_employee_estimator.py)

### 2. Survival Detection
- **Model**: Random Forest classifier on multi-signal features
- **Signals**: Review decay rate, job posting activity, Wayback Machine verification, Google Maps status
- **Output**: Operational probability (is_active_prob) with confidence levels
- **Purpose**: Identify "zombie" establishments (listed as open but operationally inactive)
- **Implementation**: [src/models/survival_detector.py](src/models/survival_detector.py)

### 3. Geographic and Industry Scope
- **Location**: Minneapolis, MN (Census Tract boundaries)
- **Industries**: 
  - NAICS 722513 (Limited-Service Restaurants / Fast Food)
  - NAICS 446110 (Pharmacies and Drug Stores)
  - **Note**: Coffee shops (722515) and gyms (713940) excluded from MVP
- **Sample Size**: 500-1000 establishments for MVP validation

### 4. Health Equity Validation (MVP Requirement)
- **Food Environment Index**: Tract-level fast food density and accessibility
- **Pharmacy Desert Analysis**: Census tracts with <1 pharmacy per 10,000 residents
- **Zombie Lag Reduction**: Improved closure detection accuracy for health metrics



## Quick Start

### Prerequisites

**Required**:
- Python 3.11 (PyMC3 incompatible with 3.12+)
- NETS database snapshot (CSV format)
- Windows PowerShell or Linux/macOS terminal

**Optional** (for external signal collection):
- Outscraper API key (review collection)
- Google Maps API key (place verification)
- OpenAI API key (entity resolution)

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/NETS-AI.git
cd NETS-AI

# Create virtual environment (Python 3.11)
python3.11 -m venv AIAGENTNETS

# Activate environment
# Windows PowerShell:
.\AIAGENTNETS\Scripts\Activate.ps1
# Linux/macOS:
source AIAGENTNETS/bin/activate

# Install dependencies
pip install -r requirements.txt

# Validate installation
python scripts/validate_environment.py
```

### 2. Configuration

```bash
# Create .env file for API keys (optional for external signals)
cp .env.example .env
# Edit .env and add keys: OUTSCRAPER_API_KEY, GOOGLE_MAPS_API_KEY, OPENAI_API_KEY
```

### 3. Data Preparation

**CRITICAL**: Place your NETS snapshot in `data/raw/`

```bash
# View required CSV schema
python scripts/generate_sample_data.py

# Required columns:
# - company_name, address, city, state, zipcode
# - latitude, longitude (EPSG:4326)
# - naics_code (must be 722513 or 446110)
# - employees_baseline (NETS reported value)
```

### 4. Run Pipeline

```bash
# Test mode (uses fixtures/nets_test_data.csv, 5-20 records)
python scripts/run_pipeline.py --test

# Production mode (requires NETS snapshot)
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv

# Skip expensive operations during development
python scripts/run_pipeline.py --test --skip linkedin wayback gpt

# Output: data/processed/nets_enhanced_minneapolis.parquet
```

### 5. Visualization

```bash
# Launch interactive dashboard
streamlit run dashboard/app.py

# Open browser to http://localhost:8501
# Explore employee estimates, survival probabilities, and geographic distributions
```

## Key Modules

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

## Technical Requirements

### Software Stack

**Core**:
- Python 3.11 (PyMC3 requires <=3.11, incompatible with 3.12+)
- pandas, numpy (data manipulation)
- geopandas, shapely (geospatial operations)
- pymc (Bayesian inference with NUTS sampler)
- scikit-learn, xgboost (machine learning models)

**Data Sources**:
- NETS database (PRIMARY - required)
- LinkedIn API (optional - employee signals)
- Outscraper API (optional - review collection)
- Google Maps API (optional - place verification)
- Wayback Machine (optional - historical validation)

**Visualization**:
- streamlit (interactive dashboard)
- folium (geographic heatmaps)
- altair (statistical charts)

### Output Format

**Primary**: Apache Parquet (3-5x smaller than CSV, preserves geospatial types)

**Required Columns**:
```
company_name, naics_code, latitude, longitude, census_tract_id,
employees_optimized, employees_lower_ci, employees_upper_ci, employees_confidence,
is_active_prob, is_active_confidence,
data_quality_score, last_updated
```

**CSV Fallback**: Available via dashboard export for legacy systems

---

## Documentation

Comprehensive guides in [docs/](docs/) directory:

- **[QUICKSTART.md](docs/QUICKSTART.md)**: Step-by-step setup and first run
- **[CONFIGURATION.md](docs/CONFIGURATION.md)**: Environment variables and settings
- **[IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md)**: Phase 4 progress tracking
- **[Methodology.md](docs/Methodology.md)**: Statistical methodology and model specifications
- **[api_costs_breakdown.md](docs/api_costs_breakdown.md)**: API usage cost estimation
- **[SYSTEM_REFERENCE.md](docs/SYSTEM_REFERENCE.md)**: Module API documentation

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

If you use this system in research, please cite:

```bibtex
@software{nets_enhancement_2026,
  title={NETS Business Data Enhancement System},
  author={[Your Name/Institution]},
  year={2026},
  url={https://github.com/yourusername/NETS-AI}
}
```

---

## Maintenance

**Project Status**: Phase 4 (Model Development) - Active Development  
**Last Updated**: January 30, 2026  
**Maintained By**: [Your Name/Lab]  
**Issues**: [GitHub Issues](https://github.com/yourusername/NETS-AI/issues)
