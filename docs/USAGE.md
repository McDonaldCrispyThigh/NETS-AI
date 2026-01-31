# NETS Minneapolis Business Data Enhancement - Usage Guide

Complete guide for using the NETS-AI system to process and analyze Minneapolis business data.

## [LIST] Quick Start

### 1. Generate Sample Data (Testing)

```bash
# Activate virtual environment
.\AIAGENTNETS\Scripts\Activate.ps1

# Generate realistic sample data (150 QSR + 80 Pharmacies)
python scripts/generate_sample_data.py
```

Output: `data/raw/nets_minneapolis_sample.csv` (230 records with enrichment features)

### 2. Run the Pipeline

```bash
# Basic usage with sample data
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_sample.csv

# With validation enabled
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_sample.csv --validate

# With custom output path
python scripts/run_pipeline.py \
 --input data/raw/nets_minneapolis_sample.csv \
 --output data/processed/my_output.parquet

# Limited to N records (useful for testing)
python scripts/run_pipeline.py \
 --input data/raw/nets_minneapolis_sample.csv \
 --sample-size 50
```

Output: `data/processed/nets_ai_minneapolis.parquet` (Parquet columnar format)

### 3. View Results with Dashboard

```bash
# Launch interactive Streamlit dashboard
streamlit run dashboard/app.py

# Open browser to http://localhost:8501
```

## [STATS] Full Pipeline Usage

### Complete Workflow

```bash
# 1. Generate sample data
python scripts/generate_sample_data.py

# 2. Run enhancement pipeline with all features
python scripts/run_pipeline.py \
 --input data/raw/nets_minneapolis_sample.csv \
 --validate \
 --verbose

# 3. Launch dashboard for exploration
streamlit run dashboard/app.py
```

### Command-Line Options

```bash
python scripts/run_pipeline.py --help
```

Key options:

- `--input, -i` **(required)**: Path to input NETS CSV file
- `--output, -o`: Output Parquet path (default: `data/processed/nets_ai_minneapolis.parquet`)
- `--naics`: Target NAICS codes (default: `722513 446110`)
- `--validate`: Run data quality validation
- `--verbose, -v`: Enable verbose logging
- `--sample-size`: Limit to N records for testing
- `--dashboard`: Auto-launch Streamlit dashboard after pipeline completes

## [FILES] Data Format

### Input CSV Requirements

Minimum required columns for input NETS data:

```
duns_id (string) - Unique D-U-N-S identifier
company_name (string) - Business name
naics_code (string) - 6-digit NAICS code
latitude (float) - WGS84 latitude
longitude (float) - WGS84 longitude
zip_code (string) - ZIP code
state (string) - State abbreviation
```

Optional enrichment columns (improves estimates):

```
employee_count_raw (int) - Raw employee count from NETS
linkedin_employee_count (int) - LinkedIn company profile headcount
review_count_3m (int) - Reviews in past 3 months
review_count_6_12m (int) - Reviews 6-12 months ago
last_review_date (string) - ISO date (YYYY-MM-DD)
job_postings_6m (int) - Job postings in past 6 months
job_postings_peak (int) - Peak monthly job postings
estimated_area_sqm (float) - Building area in square meters
```

### Output Parquet Schema

Exported Parquet file contains 42+ columns:

**Original NETS fields:**
- `duns_id`, `company_name`, `street_address`, `city`, `state`, `zip_code`
- `latitude`, `longitude`, `naics_code`, `naics_title`

**Employee Estimation (ML Output):**
- `employees_optimized` - Best estimate (integer)
- `employees_ci_lower` - 95% CI lower bound
- `employees_ci_upper` - 95% CI upper bound
- `employees_confidence` - Confidence level (high/medium/low)
- `employees_method_primary` - Primary estimation method

**Survival Detection (ML Output):**
- `is_active_prob` - Probability business is active (0-1)
- `is_active_confidence` - Confidence level
- `days_since_last_review` - Review recency indicator
- `review_decay_rate` - Review velocity trend
- `job_posting_activity` - Hiring intensity signal

**Data Quality:**
- `data_quality_score` - 0-100 composite quality metric
- `data_completeness_score` - Coverage of optional fields
- `signal_diversity_score` - Variety of data sources used

**Metadata:**
- `pipeline_version` - System version that processed record
- `processing_timestamp` - When record was enhanced
- `enrichment_source_priority` - Data source ranking

## Dashboard Features

### Interactive Visualizations

**Maps Tab:**
- Geographic distribution of establishments
- Employee count heatmap (geographic clustering)
- Business survival probability heatmap

**Employee Distribution Tab:**
- Histogram of employee counts by industry
- Confidence interval examples
- Distribution statistics

**Survival Status Tab:**
- Business status probability distribution
- Breakdown of likely active vs inactive vs uncertain
- Risk and protective factors

**Data Quality Tab:**
- Quality score histogram
- Employee estimate confidence distribution
- Data completeness metrics

**Details Tab:**
- Filterable table of all records
- Download filtered data as CSV
- Detailed record inspection

### Filtering Options

In the left sidebar:

- **NAICS Code**: Filter by industry (722513, 446110)
- **Business Status**: All, Likely Active (>0.7), Uncertain, Likely Inactive
- **Employee Count**: Range slider
- **Confidence Level**: Filter by estimate confidence (high/medium/low)

## [GOAL] Target Industries

### NAICS 722513 - Limited-Service Restaurants (Quick Service)

**Baseline Parameters:**
- Average employees: 12
- Employees per sqm: 0.025 (1 per 40 sqm)
- Typical store size: 500 sqm
- Examples: McDonald's, Subway, Chipotle, Taco Bell, Panera

**Minneapolis Data:**
- Target: ~150 establishments
- Focus: Minneapolis ZIP codes 55401-55415
- Activity signals: review velocity, job postings

### NAICS 446110 - Pharmacies

**Baseline Parameters:**
- Average employees: 10
- Employees per sqm: 0.020 (1 per 50 sqm)
- Typical store size: 600 sqm
- Examples: CVS, Walgreens, Target Pharmacy, Costco Pharmacy

**Minneapolis Data:**
- Target: ~80 establishments
- Focus: Minneapolis ZIP codes 55401-55415
- Activity signals: operating hours, script processing

## Estimation Methods

### Employee Estimation (Multi-Signal Ensemble)

Four-signal weighted combination:

1. **LinkedIn Signal (50% weight)**
 - Source: LinkedIn company profiles
 - Method: Direct headcount extraction
 - Confidence: Highest (when available)

2. **Review Velocity Signal (30% weight)**
 - Source: Google/Yelp/etc review counts
 - Method: Review intensity ratio (3m vs 6-12m)
 - Interpretation: More reviews = likely larger operation

3. **Building Area Signal (15% weight)**
 - Source: OpenStreetMap or provided estimates
 - Method: Area industry-specific employees-per-sqm
 - Example: 500 sqm 0.025 emp/sqm = 12.5 employees

4. **Job Postings Signal (5% weight)**
 - Source: Indeed, LinkedIn jobs
 - Method: Recent job posting activity
 - Interpretation: Active hiring = growing business

**Fallback:**
- When signals unavailable: Industry baseline (12 for QSR, 10 for pharmacy)
- Bayesian hierarchical model with priors (when PyMC available)
- XGBoost ensemble when training data available

### Survival Detection (4-Signal Scoring)

Weighted probability of business being operational:

1. **Review Recency (35% weight)**
 - <30 days: Strong positive
 - 30-90 days: Neutral
 - 90-180 days: Caution
 - 180+ days: Strong negative

2. **Review Decay Rate (30% weight)**
 - Ratio of 3-month to 6-12-month reviews
 - >1.0: Growing activity
 - 0.3-1.0: Stable
 - <0.3: Declining (closure risk)

3. **Job Posting Activity (20% weight)**
 - Recent posting activity indicates growth
 - Peak hiring periods signal expansion
 - No postings suggests stability or decline

4. **Street View Indicators (15% weight)**
 - Facade condition and signage visibility
 - Lighting and entrance condition
 - Visual confirmation of operations

**Output:** `is_active_prob` (0-1 probability) + confidence level

## [GROWTH] Data Quality Scoring

Composite 0-100 metric combining:

- **Completeness (20%)**: Optional fields provided
- **Diversity (20%)**: Multiple data sources used
- **Estimate Confidence (30%)**: ML model confidence
- **CI Certainty (30%)**: Narrow confidence intervals

Interpretation:
- 80-100: Excellent data, high confidence estimates
- 60-80: Good data, moderate confidence
- 40-60: Fair data, provisional estimates
- <40: Limited data, use with caution

## [CONFIG] Configuration

Edit `src/config.py` to customize:

### Geographic Settings

```python
TARGET_ZIP_CODES = [
 "55401", "55402", ... "55415" # Minneapolis only
]

# Or use census tracts instead:
MINNEAPOLIS_CENSUS_TRACTS = [...]
```

### Industry Baselines

```python
EMPLOYEE_ESTIMATION_BASELINES = {
 "722513": { # QSR
 "avg_employees": 12,
 "employees_per_sqm": 0.025,
 "min_employees": 4,
 "max_employees": 50
 },
 "446110": { # Pharmacy
 "avg_employees": 10,
 "employees_per_sqm": 0.020,
 "min_employees": 3,
 "max_employees": 35
 }
}
```

### Output Schema

```python
PARQUET_OUTPUT_SCHEMA = {
 # Customize which columns to include
 # Adjust column order and types
}
```

## [TOOLS] Troubleshooting

### Pipeline fails with "Input file not found"

```bash
# Verify file exists
ls data/raw/nets_minneapolis_sample.csv

# Use absolute path if needed
python scripts/run_pipeline.py --input "D:\NETS-AI\data\raw\nets_minneapolis_sample.csv"
```

### Dashboard shows "Unable to load data"

```bash
# Verify Parquet file was created
ls data/processed/nets_ai_minneapolis.parquet

# Check if pipeline completed successfully
python scripts/run_pipeline.py --input data/raw/nets_minneapolis_sample.csv
```

### Missing values in estimates

Expected behavior:
- When enrichment data unavailable: Uses industry baseline
- Confidence level: Set to "medium" or "low"
- CI bounds: Wider when uncertain

To improve:
- Provide `employee_count_raw` field in input CSV
- Include `review_count_3m` and `review_count_6_12m`
- Add `job_postings_6m` for hiring signals

### Slow pipeline execution

Solutions:
- Use `--sample-size` flag for testing
- Reduce ZIP code filter in config.py
- Disable validation with `--validate` flag

## [LAUNCH] Performance Tips

### For Large Datasets

```bash
# Test with sample first
python scripts/run_pipeline.py \
 --input data/raw/nets_full.csv \
 --sample-size 1000 \
 --verbose

# Then run full pipeline
python scripts/run_pipeline.py \
 --input data/raw/nets_full.csv \
 --validate
```

### For Real-Time Dashboard

```bash
# Pre-compute Parquet file
python scripts/run_pipeline.py --input data/raw/nets.csv

# Then launch dashboard (Parquet loading is fast)
streamlit run dashboard/app.py
```

## API Documentation

See [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) for complete API reference:

- `NETSLoader` - Data loading and filtering
- `EmployeeEstimator` - Multi-signal estimation
- `SurvivalDetector` - Closure risk detection
- `NETSDataPipeline` - End-to-end orchestration

## [LEARN] Examples

### Example 1: Process Real NETS Data

```bash
# Assuming you have nets_minneapolis.csv from NETS provider
python scripts/run_pipeline.py \
 --input data/raw/nets_minneapolis.csv \
 --validate \
 --verbose

streamlit run dashboard/app.py
```

### Example 2: Focus on Specific NAICS Codes

```bash
# Pharmacies only
python scripts/run_pipeline.py \
 --input data/raw/nets.csv \
 --naics 446110

# Multiple codes
python scripts/run_pipeline.py \
 --input data/raw/nets.csv \
 --naics 722513 446110 722515
```

### Example 3: Custom Processing Pipeline

```python
from src.data.pipeline import NETSDataPipeline

# Initialize with your data
pipeline = NETSDataPipeline(
 nets_csv_path='data/raw/nets.csv',
 output_parquet_path='data/processed/custom_output.parquet',
 target_naics_codes=['722513', '446110']
)

# Load and filter
df = pipeline.load_and_filter(filter_by_zip=True)

# Process
pipeline.create_geodataframe()
pipeline.estimate_employees()
pipeline.detect_survival_status()
pipeline.calculate_composite_quality_score()

# Export
df_output = pipeline.prepare_parquet_output()
pipeline.export_parquet(df_output)
```

## [SUPPORT] Support

For issues or questions:

1. Check [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) for common problems
2. Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
3. Check logs in `logs/` directory for error details
4. Verify requirements with `python verify_setup.py`

## [DOCS] Version History

- **v1.0** (Jan 2026): Initial release with QSR and Pharmacy focus, Minneapolis geographic scope, multi-signal estimation
