"""
NETS Business Data Enhancement - Quick Reference Guide
Essential commands and workflow for data processing pipeline
"""

# NETS Business Data Enhancement - Quick Reference Guide

## Project Overview
- **Target**: Quick Service Restaurants (NAICS 722513) + Pharmacies (NAICS 446110)
- **Location**: Minneapolis, Minnesota
- **Output**: Parquet database + Streamlit dashboard
- **Key Metrics**: employee count (with CI) + survival probability

## Directory Structure
```
NETS-AI/
[|][-][-] src/
 [|][-][-] config.py # Configuration + baselines
 [|][-][-] data/
 [|][-][-] nets_loader.py # Load + filter NETS data
 [_][-][-] pipeline.py # Main orchestration
 [|][-][-] models/
 [|][-][-] bayesian_employee_estimator.py # Employee modeling
 [_][-][-] survival_detector.py # Survival prediction
 [_][-][-] utils/
 [_][-][-] logger.py # Logging utilities
[|][-][-] data/
 [|][-][-] raw/ # Input NETS CSV
 [|][-][-] external/ # LinkedIn, Outscraper, Indeed, OSM
 [_][-][-] processed/ # Output Parquet files
[|][-][-] dashboard/
 [_][-][-] app.py # Streamlit dashboard
[|][-][-] docs/
 [|][-][-] ARCHITECTURE.md # Complete system design
 [_][-][-] QUICKSTART.md # Getting started guide
[_][-][-] requirements.txt # Python dependencies
```

## Installation (First Time)

```powershell
# 1. Activate environment
.\AIAGENTNETS\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt --upgrade

# 3. Verify installation
python scripts/validate_environment.py
```

## Data Preparation

### Step 1: Prepare Input Files
Place the following files in `data/raw/` or `data/external/`:

```
data/raw/
[|][-][-] nets_minneapolis.csv # NETS establishment data (required)
 # Expected columns: duns_id, company_name, 
 # latitude, longitude, naics_code, zip_code

data/external/
[|][-][-] linkedin_headcount.csv # LinkedIn employee counts (optional)
 Columns: duns_id, linkedin_headcount, linkedin_url
[|][-][-] outscraper_reviews.csv # Google reviews timeseries (optional)
 Columns: duns_id, review_count_3m, review_count_6_12m, last_review_date
[|][-][-] indeed_postings.csv # Job posting activity (optional)
 Columns: duns_id, job_postings_6m, job_postings_peak
[_][-][-] osm_building_footprints.csv # Building areas (optional)
 Columns: latitude, longitude, building_area_sqm
```

### Step 2: Validate NETS Input
```python
from src.data.nets_loader import NETSLoader, NETSValidator

loader = NETSLoader('data/raw/nets_minneapolis.csv')
df = loader.load_raw()
print(f"Loaded {len(df)} records")

# Check data quality
validator = NETSValidator()
print(validator.check_required_columns(df))
print(validator.check_coordinates(df))
```

## Running the Pipeline

### Method 1: Complete Automated Run
```python
from src.data.pipeline import NETSDataPipeline

pipeline = NETSDataPipeline(
 nets_csv_path='data/raw/nets_minneapolis.csv',
 output_parquet_path='data/processed/nets_ai_minneapolis.parquet'
)

# Run with all optional data sources
output_file = pipeline.run(
 linkedin_data='data/external/linkedin_headcount.csv',
 outscraper_data='data/external/outscraper_reviews.csv',
 job_postings_data='data/external/indeed_postings.csv',
 validate=True
)

print(f"Output file: {output_file}")
```

### Method 2: Step-by-Step Control
```python
pipeline = NETSDataPipeline('data/raw/nets_minneapolis.csv')

# Load and filter
pipeline.load_and_filter(filter_by_zip=True, filter_active_only=True)
print(f"After filtering: {len(pipeline.df)} records")

# Deduplicate
pipeline.deduplicate()

# Validate
results = pipeline.validate_data_quality()
print(results)

# Create spatial representation
gdf = pipeline.create_geodataframe()

# Enrich with external data
pipeline.enrich_with_external_sources(
 linkedin_data_path='data/external/linkedin_headcount.csv'
)

# Run models
pipeline.estimate_employees()
pipeline.detect_survival_status()

# Quality scoring
pipeline.calculate_composite_quality_score()

# Export
output_df = pipeline.prepare_parquet_output()
output_path = pipeline.export_parquet(output_df)
```

### Method 3: Streamlit Dashboard (No Pipeline Needed)
```bash
# Requires existing Parquet file
streamlit run dashboard/app.py
```

## Configuration

### Modify Target NAICS Codes
Edit `src/config.py`:
```python
INDUSTRY_CONFIG = {
 "quick_service_restaurant": {
 "naics_code": "722513",
 ...
 },
 "pharmacy": {
 "naics_code": "446110",
 ...
 }
}
```

### Adjust Employee Estimation Baselines
Edit `src/config.py`:
```python
EMPLOYEE_ESTIMATION_BASELINES = {
 "722513": { # Quick Service Restaurants
 "employees_per_sqm": 0.025,
 "avg_employees": 12,
 "avg_store_size_sqm": 500,
 "min_employees": 4,
 "max_employees": 50
 },
 ...
}
```

### Modify Feature Engineering Parameters
Edit `src/config.py`:
```python
REVIEW_DECAY_WINDOW = {
 "recent": 3, # Recent period (months)
 "historical": 12, # Historical baseline (months)
 "min_review_count": 3 # Minimum for decay calculation
}

GEOGRAPHIC_MATCH = {
 "haversine_threshold_m": 50, # Match distance threshold
 "coordinate_cluster_radius_m": 20 # Clustering radius
}
```

## Output Files

### Primary Output: Parquet Database
**File**: `data/processed/nets_ai_minneapolis.parquet`

**How to Read**:
```python
import pandas as pd

df = pd.read_parquet('data/processed/nets_ai_minneapolis.parquet')
print(f"Shape: {df.shape}")
print(df.columns)

# Filter to high-confidence estimates
high_conf = df[df['employees_confidence'] == 'high']
print(f"High confidence: {len(high_conf)} records")

# Filter to likely active businesses
active = df[df['is_active_prob'] > 0.7]
print(f"Likely active: {len(active)} records")

# Export subset to CSV
active.to_csv('data/processed/active_establishments.csv', index=False)
```

### Streamlit Dashboard
**Start**: `streamlit run dashboard/app.py`

**Features**:
- Interactive maps (Folium heatmaps)
- Employee distribution charts (Altair)
- Survival probability analysis
- Data quality visualization
- Filterable data table with CSV export

### Logs
**Location**: `logs/` directory

**Contents**:
- Pipeline execution log (timestamp-labeled)
- Error messages with context
- API call summary
- Performance metrics

**Example Log**:
```
2025-01-29 15:30:00 - INFO - Loading NETS data...
2025-01-29 15:30:15 - INFO - Initial records: 5234
2025-01-29 15:30:45 - INFO - After filtering: 842 records
2025-01-29 15:31:00 - INFO - Estimating employee counts...
2025-01-29 15:32:15 - INFO - Employee estimation complete
2025-01-29 15:32:30 - INFO - Detecting business survival status...
2025-01-29 15:33:45 - INFO - Survival detection complete: 598 likely active
2025-01-29 15:34:00 - INFO - Exporting to Parquet: data/processed/nets_ai_minneapolis.parquet
2025-01-29 15:34:05 - INFO - Parquet export complete: 2.5 MB
```

## Performance Optimization

### For Large Datasets (>1000 records)
```python
# Enable Dask for distributed processing
import dask.dataframe as dd

df_dask = dd.read_parquet('data/processed/nets_ai_minneapolis.parquet')

# Compute in batches
result = df_dask.groupby('naics_code')['employees_optimized'].mean().compute()
```

### Memory Usage
```python
# Check DataFrame memory footprint
df = pd.read_parquet('data/processed/nets_ai_minneapolis.parquet')
print(df.memory_usage(deep=True).sum() / (1024**3), "GB")

# Optimize data types
df['employees_optimized'] = df['employees_optimized'].astype('float32')
df['is_active_prob'] = df['is_active_prob'].astype('float32')
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pymc'"
**Solution**: Install missing dependencies
```bash
pip install pymc arviz
```

### Issue: "PARQUET file not found for dashboard"
**Solution**: Run pipeline first to generate Parquet
```bash
python -c "from src.data.pipeline import NETSDataPipeline; NETSDataPipeline('data/raw/nets_minneapolis.csv').run()"
```

### Issue: API Rate Limits Exceeded
**Solution**: Implement delays and batching
```python
import time
for i in range(1000):
 if i % 100 == 0:
 time.sleep(30) # 30-second delay every 100 records
 # Process record
```

### Issue: Memory Error with Large Datasets
**Solution**: Process in batches
```python
BATCH_SIZE = 100
for i in range(0, len(df), BATCH_SIZE):
 batch = df.iloc[i:i+BATCH_SIZE]
 # Process batch
```

## Key Metrics to Track

After running pipeline, calculate these metrics:

```python
import pandas as pd

df = pd.read_parquet('data/processed/nets_ai_minneapolis.parquet')

# Data completeness
print(f"Data completeness: {df['employees_optimized'].notna().sum() / len(df) * 100:.1f}%")

# Confidence distribution
print(df['employees_confidence'].value_counts())
print(df['is_active_confidence'].value_counts())

# Business status summary
print(f"Likely active (>0.7): {(df['is_active_prob'] > 0.7).sum()}")
print(f"Uncertain (0.3-0.7): {((df['is_active_prob'] >= 0.3) & (df['is_active_prob'] <= 0.7)).sum()}")
print(f"Likely inactive (<0.3): {(df['is_active_prob'] < 0.3).sum()}")

# Employee estimation summary
print(f"Mean employees: {df['employees_optimized'].mean():.1f}")
print(f"Median CI width: {(df['employees_ci_upper'] - df['employees_ci_lower']).median():.1f}")

# Data quality score
print(f"Mean quality: {df['data_quality_score'].mean():.0f}/100")
```

## Next Steps

1. **Collect External Data Sources**
 - Request LinkedIn company data export
 - Set up Outscraper API account
 - Download Indeed historical job postings
 - Get OSM building footprints for Minneapolis

2. **Validate Results**
 - Compare estimates vs. LinkedIn (where available)
 - Manual verification of 100 random businesses
 - Calculate error metrics (MAE, RMSE)

3. **Production Deployment**
 - Set up cloud storage (S3/GCS)
 - Schedule daily/weekly updates
 - Configure monitoring and alerts
 - Document data lineage and versioning

4. **Extend Capabilities**
 - Add time-series tracking
 - Implement forecasting models
 - Create neighborhood-level aggregations
 - Develop equity impact analysis
