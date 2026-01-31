# Feature Engineering Documentation

This document describes the feature engineering process for the NETS Enhancement System.

## Overview

The system extracts and engineers features from multiple data sources to estimate business employment levels and survival probability.

## Feature Categories

### 1. NETS Primary Features

These features come directly from the NETS database (PRIMARY source):

| Feature | Type | Description |
|---------|------|-------------|
| `emp_here` | int | Employee count at this location |
| `year_established` | int | Business establishment year |
| `naics_code` | str | 6-digit NAICS industry code |
| `zip_code` | str | 5-digit ZIP code |
| `latitude/longitude` | float | Geographic coordinates (EPSG:4326) |

### 2. Review Signal Features

Derived from Google/Yelp review data:

| Feature | Type | Description |
|---------|------|-------------|
| `review_count` | int | Total review count |
| `avg_rating` | float | Average rating (1-5 scale) |
| `review_velocity` | float | Reviews per month |
| `review_decay_rate` | float | Rate of review decline |
| `months_since_last_review` | int | Activity recency signal |

### 3. Employment Signals

External signals for employee estimation:

| Feature | Source | Reliability |
|---------|--------|-------------|
| `linkedin_employee_count` | LinkedIn API | High |
| `job_posting_count` | Indeed/LinkedIn | Medium |
| `hiring_activity_score` | Aggregated | Medium |

### 4. Survival Indicators

Features for predicting business survival:

| Feature | Type | Signal |
|---------|------|--------|
| `website_status` | bool | Active domain |
| `last_wayback_date` | date | Archival activity |
| `license_status` | str | Active/expired |
| `review_decay_rate` | float | Key predictor |

## Feature Engineering Pipeline

### Step 1: NETS Data Loading

```python
# Primary data source - never replaced
nets_df = NETSLoader.load(path)
```

### Step 2: External Signal Collection

```python
# Supplements NETS data (does NOT replace)
signals = ExternalSignalCollector.collect(duns_id)
```

### Step 3: Feature Transformation

- Log transformation for skewed counts
- One-hot encoding for categorical features
- Temporal features (business age, seasonality)
- Geospatial features (distance to urban core)

### Step 4: Missing Value Handling

| Strategy | Features |
|----------|----------|
| Median imputation | Numeric counts |
| Mode imputation | Categorical |
| Industry baseline | Missing employee counts |

## Uncertainty Quantification

All estimates include 95% confidence intervals:

```python
@dataclass
class EmployeeEstimate:
    point_estimate: float
    ci_lower: float      # 2.5th percentile
    ci_upper: float      # 97.5th percentile
    confidence_level: str  # high/medium/low
```

## Industry-Specific Baselines

### NAICS 722513 (Limited-Service Restaurants)

| Metric | Value |
|--------|-------|
| Median employees | 12 |
| Mean employees | 15.3 |
| Std dev | 8.7 |
| Min typical | 3 |
| Max typical | 50 |

### NAICS 446110 (Pharmacies)

| Metric | Value |
|--------|-------|
| Median employees | 8 |
| Mean employees | 10.2 |
| Std dev | 6.5 |
| Min typical | 2 |
| Max typical | 35 |

## Data Quality Scoring

Each record receives a composite data quality score (0-100):

| Component | Weight | Criteria |
|-----------|--------|----------|
| Coordinate validity | 20% | Within city bounds |
| NETS completeness | 30% | Required fields present |
| Signal freshness | 25% | Recent external data |
| Consistency | 25% | Cross-source agreement |
