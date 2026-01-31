# Data Directory Structure

This directory contains all data files for the NETS Enhancement System.
**Place your real NETS data files in the appropriate subdirectories.**

## Directory Layout

```
data/
├── raw/                          # INPUT: Original NETS CSV exports
│   ├── .gitkeep
│   └── nets_minneapolis.csv      # <- Place your NETS export here
│
├── processed/                    # OUTPUT: Enhanced parquet files
│   ├── .gitkeep
│   └── nets_enhanced_minneapolis_YYYYMMDD.parquet  # Generated output
│
├── outputs/                      # OUTPUT: Analysis results and figures
│   ├── .gitkeep
│   └── validation_report.html    # Generated validation report
│
└── README.md                     # This file
```

## Required Input File

### `data/raw/nets_minneapolis.csv`

Your NETS CSV export must contain these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `duns_id` | str | Unique DUNS identifier | "123456789" |
| `company_name` | str | Business name | "McDonald's" |
| `naics_code` | str | 6-digit NAICS code | "722513" |
| `latitude` | float | GPS latitude | 44.9778 |
| `longitude` | float | GPS longitude | -93.2650 |
| `street_address` | str | Street address | "123 Main St" |
| `city` | str | City name | "Minneapolis" |
| `state` | str | 2-letter state code | "MN" |
| `zip_code` | str | 5-digit ZIP code | "55401" |
| `first_year` | int | Establishment year | 2015 |
| `last_year` | int | Last active year | 2024 |
| `emp_here` | int | Employee count (if available) | 12 |

### Optional Columns

| Column | Type | Description |
|--------|------|-------------|
| `phone` | str | Phone number |
| `website` | str | Website URL |
| `sic_code` | str | SIC code |
| `naics_title` | str | NAICS description |
| `sales_volume` | float | Annual sales |

## Output Files

### `data/processed/nets_enhanced_{city}_{task}_{timestamp}.parquet`

Enhanced dataset with additional columns:

| Column | Description |
|--------|-------------|
| `employees_optimized` | Estimated employee count |
| `employees_lower_ci` | 95% CI lower bound |
| `employees_upper_ci` | 95% CI upper bound |
| `is_active_prob` | Probability business is active |
| `confidence_level` | Data quality confidence (High/Medium/Low) |
| `data_quality_score` | Numeric quality score (0-1) |
| `census_tract_id` | Census tract identifier |

## NAICS Code Filter

The pipeline filters for these NAICS codes only:

- **722513**: Limited-Service Restaurants (Fast Food/QSR)
- **446110**: Pharmacies and Drug Stores

## Quick Start

1. Place your NETS CSV in `data/raw/nets_minneapolis.csv`
2. Run: `python scripts/run_pipeline.py --input data/raw/nets_minneapolis.csv`
3. Output: `data/processed/nets_enhanced_minneapolis_YYYYMMDD.parquet`

## Test Mode

For testing without real data, use test mode which generates minimal synthetic records:

```bash
python scripts/run_pipeline.py --test
```

This creates output in `data/processed/` without requiring actual NETS data.
