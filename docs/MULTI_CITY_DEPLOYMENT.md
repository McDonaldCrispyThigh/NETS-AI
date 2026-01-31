# Multi-City Deployment Guide

This document describes how to deploy the NETS Enhancement System to additional cities.

## Architecture Overview

The system uses **dynamic boundary fetching** - all geographic data is retrieved from external APIs at runtime:

```
src/config/cities/
    __init__.py           # Config exports
    dynamic_config.py     # CityConfig class with dynamic fetching
    city_context.py       # Runtime context manager

src/geospatial/
    boundary_fetcher.py   # OpenStreetMap/Census API integration
    boundary_validator.py # Coordinate validation
    distance_calculator.py# Haversine distance

data/boundaries/          # Local cache for downloaded boundaries
    minneapolis_mn.json
    denver_co.json
```

## Key Principle: No Hardcoded Geography

All geographic data is fetched dynamically:

| Data Type | Source | Cached |
|-----------|--------|--------|
| City boundaries | OpenStreetMap Nominatim | Yes |
| ZIP codes | US Census ZCTA | Yes |
| Polygon geometry | Census TIGERweb | Yes |

## Adding a New City

### Step 1: Simply Use the City Key

No configuration file needed. Just run with the city key:

```bash
python main.py --input data/raw/portland_or_nets.csv --city portland_or
```

The system will automatically:
1. Parse "portland_or" into city="Portland", state="OR"
2. Fetch boundaries from OpenStreetMap Nominatim API
3. Fetch ZIP codes from Census ZCTA API
4. Cache results in `data/boundaries/portland_or.json`

### Step 2: (Optional) Custom Configuration

For custom NAICS codes or baselines, create a config programmatically:

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
