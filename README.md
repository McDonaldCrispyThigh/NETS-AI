# NETS Business Data Enhancement System

**Statistical Employee Estimation and Operational Status Detection for Quick Service Restaurants and Pharmacies**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Phase: 4](https://img.shields.io/badge/phase-4%20Model%20Development-orange.svg)](docs/IMPLEMENTATION_STATUS.md)

## Project Overview

This system enhances the National Establishment Time-Series (NETS) commercial database through **dynamic multi-city architecture** with statistical model integration. The pipeline integrates multi-source external signals to:

1. **Employee Count Estimation**: Bayesian hierarchical modeling with NAICS-specific priors and 95% credible intervals
2. **Operational Status Detection**: Random Forest classification for zombie establishment identification
3. **Health Equity Research Support**: Census tract-level food environment and pharmacy accessibility metrics

### Key Features

- **Dynamic Geographic Boundaries**: Fetched automatically from OpenStreetMap Nominatim and US Census APIs
- **No Hardcoded Constants**: All city boundaries and ZIP codes retrieved at runtime
- **Multi-City Support**: Any US city supported via `--city {city}_{state}` parameter
- **Cached Boundaries**: Downloaded data cached locally in `data/boundaries/`

### Scope

**Geographic Coverage**: Any US city (boundaries fetched dynamically)
- Run with: `python main.py --input data.csv --city seattle_wa`

**Industry Focus**: 
- NAICS 722513 (Limited-Service Restaurants / Fast Food)
- NAICS 446110 (Pharmacies and Drug Stores)

**Current Phase**: Phase 4 - Statistical Model Development

> **CRITICAL**: NETS database is the PRIMARY authoritative data source. External signals (LinkedIn, Google Maps, reviews) are supplementary only.

---

## Quick Start

### 1. Environment Setup

```bash
# Create Python 3.11 environment (required for PyMC)
conda create -n nets python=3.11
conda activate nets

# Install dependencies
pip install -r requirements.txt

# Install PyMC separately
pip install pymc arviz
```

### 2. Configure API Keys

Create `.env` file in project root:

```env
GOOGLE_MAPS_API_KEY=your_key_here
YELP_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OUTSCRAPER_API_KEY=your_key_here
```

### 3. Run Pipeline

```bash
# Test mode (uses fixtures, no API calls)
python main.py --test --verbose

# Production mode
python main.py --input data/raw/nets_data.csv --city minneapolis_mn

# Skip expensive APIs
python main.py --input data.csv --skip linkedin wayback gpt
```

---

## Repository Structure

```text
NETS-Enhancement/
+-- main.py                       # CLI entry point
+-- requirements.txt              # Python dependencies
+-- .env                          # API keys (gitignored)
+-- src/
|   +-- config/
|   |   +-- cities/               # Dynamic city configuration
|   |       +-- dynamic_config.py # CityConfig with API fetching
|   |       +-- city_context.py   # Runtime context manager
|   +-- geospatial/               # Geographic operations
|   |   +-- boundary_fetcher.py   # OpenStreetMap/Census API client
|   |   +-- boundary_validator.py # Coordinate validation
|   |   +-- distance_calculator.py# Haversine distance
|   +-- agents/                   # External data collectors
|   |   +-- yelp_api.py           # Yelp Fusion API
|   |   +-- wayback_agent.py      # Internet Archive
|   |   +-- google_maps_agent.py  # Places API
|   +-- data/                     # Data processing
|   |   +-- nets_loader.py        # NETS CSV ingestion
|   |   +-- pipeline.py           # Orchestration engine
|   +-- models/                   # Statistical models
|       +-- bayesian_employee_estimator.py
|       +-- survival_detector.py
+-- data/
|   +-- boundaries/               # Cached city boundaries (auto-generated)
|   +-- raw/                      # Input NETS data
|   +-- processed/                # Output Parquet files
+-- tests/
|   +-- fixtures/
|       +-- nets_test_data.csv    # Test data (5 records)
+-- docs/
    +-- FEATURES.md               # Feature engineering
    +-- MULTI_CITY_DEPLOYMENT.md  # City deployment guide
```

---

## Dynamic Boundary System

All geographic data is fetched automatically from external APIs:

| Data Type | Source | Cached |
|-----------|--------|--------|
| City bounds | OpenStreetMap Nominatim | Yes |
| ZIP codes | US Census ZCTA | Yes |
| Polygon geometry | Census TIGERweb | Yes |

### Usage

```python
from src.config.cities import get_city_config

# Boundaries fetched automatically on first access
config = get_city_config(\"portland_or\")
bounds = config.get_bounds()  # (min_lon, min_lat, max_lon, max_lat)
```

---

## Output Schema

All outputs include uncertainty quantification:

| Column | Type | Description |
|--------|------|-------------|
| `employees_optimized` | float | Point estimate |
| `employees_ci_lower` | float | 2.5th percentile (95% CI) |
| `employees_ci_upper` | float | 97.5th percentile |
| `is_active_prob` | float | Survival probability (0-1) |
| `confidence_level` | str | high/medium/low |
| `data_quality_score` | int | 0-100 composite score |

---

## Implementation Status

- [x] Phase 0: Environment Configuration
- [x] Phase 1: Data Collection Infrastructure  
- [x] Phase 2: Multi-City Architecture (Dynamic)
- [x] Phase 3: Signal Processing Pipeline
- [x] Phase 4: Statistical Model Development (CURRENT)
- [ ] Phase 5: Production Integration
- [ ] Phase 6: Health Equity Validation

---

## License

MIT License - See [LICENSE](LICENSE) for details.
