# Multi-City Deployment Guide

This document describes how to deploy the NETS Enhancement System to additional cities.

## Architecture Overview

The system uses a modular city configuration approach:

```
src/config/cities/
    __init__.py           # Config registry
    city_context.py       # Runtime context manager
    minneapolis_mn.py     # Minneapolis configuration
    denver_co.py          # Denver configuration (template)
```

## Adding a New City

### Step 1: Create City Configuration File

Create `src/config/cities/{city}_{state}.py`:

```python
"""
Configuration for {City Name}, {State}
"""

from typing import Dict, Any

{CITY}_CONFIG: Dict[str, Any] = {
    "city_name": "{City Name}",
    "state": "{ST}",
    "timezone": "America/{Timezone}",
    
    # Geographic bounds (EPSG:4326)
    "bounds": {
        "min_lon": -XX.XXXX,
        "max_lon": -XX.XXXX,
        "min_lat": XX.XXXX,
        "max_lat": XX.XXXX,
    },
    
    # Valid ZIP codes for the city
    "zip_codes": [
        "XXXXX", "XXXXX", ...
    ],
    
    # Target NAICS codes
    "naics_codes": {
        "722513": "Limited-Service Restaurants",
        "446110": "Pharmacies",
    },
    
    # Industry baselines for employee estimation
    "employee_baselines": {
        "722513": {
            "median": 12,
            "mean": 15.0,
            "std": 8.0,
            "min_typical": 3,
            "max_typical": 50,
        },
        "446110": {
            "median": 8,
            "mean": 10.0,
            "std": 6.0,
            "min_typical": 2,
            "max_typical": 35,
        },
    },
    
    # Data sources configuration
    "data_sources": {
        "sos_url": "https://...",  # Secretary of State business lookup
        "sos_enabled": True,
    },
}
```

### Step 2: Register the Configuration

Edit `src/config/cities/__init__.py`:

```python
from .{city}_{state} import {CITY}_CONFIG

CITY_CONFIGS = {
    "minneapolis_mn": MINNEAPOLIS_CONFIG,
    "denver_co": DENVER_CONFIG,
    "{city}_{state}": {CITY}_CONFIG,  # Add new city
}
```

### Step 3: Prepare NETS Data

1. Export NETS snapshot for the target city:
   - Filter by city name and state
   - Filter by target ZIP codes
   - Filter by target NAICS codes

2. Place data file in `data/raw/{city}_{state}_nets.csv`

### Step 4: Configure API Keys

Ensure `.env` has appropriate API keys for the region.

### Step 5: Run Pipeline

```bash
python main.py --input data/raw/{city}_{state}_nets.csv --city {city}_{state}
```

## Geographic Bounds Determination

To determine city bounds:

1. **Census Bureau**: Use TIGER/Line shapefiles for official city boundaries
2. **OpenStreetMap**: Query for city relation boundaries
3. **Conservative buffer**: Add 0.01 degrees (~1km) buffer around official bounds

## ZIP Code Collection

Sources for city ZIP codes:
- US Census Bureau ZIP Code Tabulation Areas (ZCTAs)
- USPS Address Information System
- City planning department resources

## Industry Baseline Calibration

Employee baselines should be calibrated using:

1. **Bureau of Labor Statistics** (BLS) QCEW data
2. **Census Bureau** County Business Patterns
3. **NETS historical data** for the specific city

### Baseline Validation

Run validation to ensure baselines are appropriate:

```bash
python main.py --input data/raw/{city}_nets.csv --city {city}_{state} --validate
```

## Deployment Checklist

- [ ] City configuration file created
- [ ] Configuration registered in __init__.py
- [ ] Geographic bounds verified
- [ ] ZIP codes validated
- [ ] Industry baselines calibrated
- [ ] NETS data exported and placed
- [ ] API keys configured for region
- [ ] Test run completed successfully
- [ ] Output validated against known establishments

## Current Deployments

| City | State | Status | NAICS Codes |
|------|-------|--------|-------------|
| Minneapolis | MN | Production | 722513, 446110 |
| Denver | CO | Template | 722513, 446110 |

## Troubleshooting

### Common Issues

**Coordinates outside bounds**
- Verify NETS data coordinates are in EPSG:4326
- Check bounds calculation (min/max may be swapped)

**Missing ZIP codes**
- Add ZIP codes to city configuration
- Verify ZIP code format (5-digit string)

**Low match rates**
- Review geographic matching threshold (default: 50m)
- Check name fuzzy matching configuration
