## Testing Guide for NETS-AI Pipeline

This document explains how to run tests and validate the NETS-AI system without production data.

### Overview

The system supports two modes:
- **Production mode**: Process real NETS data files
- **Test mode**: Use minimal test fixtures for validation and development

### Quick Start - Running Tests

#### Step 1: Generate Test Fixtures

Test fixtures are minimal datasets for unit testing. Generate them with:

```bash
# Activate virtual environment
.\AIAGENTNETS\Scripts\Activate.ps1

# Generate test fixtures (creates 8 small records)
python scripts/generate_sample_data.py
```

Output: `tests/fixtures/nets_test_fixture_small.csv` (8 records: 5 QSR + 3 Pharmacy)

#### Step 2: Run Pipeline in Test Mode

```bash
# Run pipeline with test fixtures (automatic)
python scripts/run_pipeline.py --mode test

# Run with validation enabled
python scripts/run_pipeline.py --mode test --validate

# Run with verbose logging
python scripts/run_pipeline.py --mode test --verbose
```

Output: `data/processed/nets_test_output.parquet`

#### Step 3: View Test Results

```bash
# Verify output was created
Get-ChildItem data/processed/nets_test_output.parquet

# Load and inspect results
python -c "
import pandas as pd
df = pd.read_parquet('data/processed/nets_test_output.parquet')
print(f'Records: {len(df)}')
print(f'Columns: {df.columns.tolist()}')
print(df[['company_name', 'naics_code', 'employees_optimized']].head())
"
```

### Complete Test Workflow

```bash
# 1. Verify environment
python verify_setup.py

# 2. Generate test fixtures
python scripts/generate_sample_data.py

# 3. Run pipeline in test mode with all checks
python scripts/run_pipeline.py --mode test --validate --verbose

# 4. Verify output file
ls -la data/processed/nets_test_output.parquet

# 5. Inspect results
python -c "import pandas as pd; df = pd.read_parquet('data/processed/nets_test_output.parquet'); print(f'Success: {len(df)} records processed')"
```

### Test Fixtures Details

#### Test Fixture Composition

File: `tests/fixtures/nets_test_fixture_small.csv`

Total Records: 8
- Quick Service Restaurants (NAICS 722513): 5 records
- Pharmacies (NAICS 446110): 3 records

Geographic: All within Minneapolis ZIP codes 55401-55415

#### Test Fixture Columns

Required columns:
```
duns_id, company_name, naics_code, naics_title, 
latitude, longitude, zip_code, city, state,
street_address, phone, year_established, year_closed,
employee_count_raw
```

Optional enrichment columns:
```
linkedin_employee_count, review_count_3m, review_count_6_12m,
last_review_date, job_postings_6m, job_postings_peak,
estimated_area_sqm, street_view_active, signage_visible
```

### Running Individual Components in Test Mode

#### Test Employee Estimator

```python
from src.models.bayesian_employee_estimator import EmployeeEstimator
from src.config import EMPLOYEE_ESTIMATION_BASELINES

estimator = EmployeeEstimator(EMPLOYEE_ESTIMATION_BASELINES)

estimate = estimator.estimate(
 record={'employee_count_raw': 12, 'naics_code': '722513'},
 naics_code='722513',
 linkedin_headcount=13,
 review_count_3m=8,
 review_count_6_12m=15,
 estimated_area_sqm=500,
 job_postings_6m=2
)

print(f"Estimate: {estimate.employees_optimized}")
print(f"Confidence: {estimate.employees_confidence}")
```

#### Test Survival Detector

```python
from src.models.survival_detector import SurvivalDetector

detector = SurvivalDetector()

result = detector.score_survival(
 duns_id='123456',
 company_name='Test Restaurant',
 last_review_date='2026-01-15',
 review_count_3m=10,
 review_count_6_12m=25,
 job_postings_6m=2,
 job_postings_peak=3,
 street_view_facade=True,
 street_view_signage=True
)

print(f"Survival Probability: {result.is_active_prob}")
print(f"Confidence: {result.is_active_confidence}")
```

#### Test Data Loader

```python
from src.data.nets_loader import NETSLoader

loader = NETSLoader('tests/fixtures/nets_test_fixture_small.csv')

# Load raw data
df = loader.load_raw()
print(f"Loaded {len(df)} records")

# Filter by NAICS
df_qsr = loader.filter_by_naics_codes(['722513'])
print(f"QSR records: {len(df_qsr)}")

# Filter by ZIP code
from src.config import TARGET_ZIP_CODES
df_minneapolis = loader.filter_by_zip_codes(TARGET_ZIP_CODES)
print(f"Minneapolis records: {len(df_minneapolis)}")
```

### Running Tests via Python

```bash
# Activate environment
.\AIAGENTNETS\Scripts\Activate.ps1

# Run Python test script
python -c "
from pathlib import Path
from src.data.pipeline import NETSDataPipeline

# Use test fixture
pipeline = NETSDataPipeline(
 nets_csv_path='tests/fixtures/nets_test_fixture_small.csv',
 output_parquet_path='data/processed/nets_test_output.parquet'
)

# Run pipeline
df = pipeline.load_and_filter()
print(f'Loaded: {len(df)} records')

pipeline.create_geodataframe()
df_emp = pipeline.estimate_employees()
print(f'Estimated employees for: {len(df_emp)} records')

df_surv = pipeline.detect_survival_status()
print(f'Detected survival status: {len(df_surv)} records')

df_quality = pipeline.calculate_composite_quality_score()
print(f'Calculated quality: {len(df_quality)} records')

df_output = pipeline.prepare_parquet_output()
pipeline.export_parquet(df_output)
print('Export complete')
"
```

### Expected Test Results

After running test mode pipeline:

Output file should contain:
```
File: data/processed/nets_test_output.parquet
Size: ~5-10 KB
Records: 8
Columns: 42
```

Sample records should show:
```
company_name | naics_code | employees_optimized | is_active_prob | data_quality_score
Subway | 722513 | 5-15 | 0.3-0.9 | 40-70
CVS | 446110 | 4-12 | 0.3-0.9 | 40-70
```

### Validation Checks

Test mode pipeline runs:
- Column presence validation
- Data type validation
- Geographic boundary validation
- Quality score calculation
- Schema compliance

### Troubleshooting Tests

#### Test Fixture Not Found

```
Error: Test fixture not found at tests/fixtures/nets_test_fixture_small.csv
```

Solution:
```bash
python scripts/generate_sample_data.py
```

#### Import Errors in Test

Ensure you are in the correct directory:
```bash
cd d:\NETS-AI
.\AIAGENTNETS\Scripts\Activate.ps1
python scripts/run_pipeline.py --mode test
```

#### Test Mode with Custom Output

```bash
python scripts/run_pipeline.py --mode test --output data/processed/my_test_output.parquet
```

### Automated Test Execution

Create a batch file for repeated testing (`run_tests.bat`):

```batch
@echo off
echo Running NETS-AI Test Suite...
echo.

echo Step 1: Generate test fixtures
python scripts/generate_sample_data.py

echo.
echo Step 2: Run pipeline in test mode
python scripts/run_pipeline.py --mode test --validate --verbose

echo.
echo Test execution complete. Check results in:
echo - data/processed/nets_test_output.parquet
echo.
pause
```

Run with:
```bash
run_tests.bat
```

### Next Steps: Using Production Data

Once tests pass, switch to production:

```bash
# Prepare your NETS CSV file
# Place in: data/raw/your_nets_data.csv

# Run production mode
python scripts/run_pipeline.py --mode production --input data/raw/your_nets_data.csv --validate

# Or shorter:
python scripts/run_pipeline.py --input data/raw/your_nets_data.csv --validate
```

### Support

For issues with tests:
1. Verify test fixtures exist: `tests/fixtures/nets_test_fixture_small.csv`
2. Check environment: `python verify_setup.py`
3. View logs in: `logs/` directory
4. Run with verbose flag: `--verbose`
