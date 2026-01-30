"""
NETS Business Data Enhancement System - Documentation Index
Complete reference guide to all project documentation
"""

# NETS Business Data Enhancement - Documentation Index

## Quick Navigation

### For Getting Started
1. **README.md** - Project overview and quick start
2. **docs/QUICK_REFERENCE.md** - Command reference and workflow
3. **PROJECT_REALIGNMENT_SUMMARY.md** - What changed in this release

### For System Design
1. **docs/ARCHITECTURE.md** - Complete system architecture
2. **src/config.py** - Configuration parameters and baselines

### For Development
1. **src/data/nets_loader.py** - NETS data loading
2. **src/models/bayesian_employee_estimator.py** - Employee estimation
3. **src/models/survival_detector.py** - Survival detection
4. **src/data/pipeline.py** - Pipeline orchestration

### For Dashboard
1. **dashboard/app.py** - Streamlit dashboard source code

---

## Document Descriptions

### README.md
**Purpose**: Project overview and quick reference  
**Audience**: All users  
**Contains**:
- Project vision and objectives
- Pipeline architecture overview
- Technology stack requirements
- Quick start installation
- Repository structure
- Core innovation summary

**Read this if**: You're new to the project and want a 5-minute overview

---

### PROJECT_REALIGNMENT_SUMMARY.md
**Purpose**: Changelog and high-level overview of modifications  
**Audience**: Project stakeholders, developers  
**Contains**:
- What changed from previous version
- New features summary
- Data flow changes
- File manifest (created/modified)
- Configuration customization guide
- Next steps recommendations

**Read this if**: You want to understand what was changed and why

---

### docs/ARCHITECTURE.md (CORE DOCUMENTATION)
**Purpose**: Complete system architecture and design specifications  
**Audience**: Developers, technical stakeholders  
**Contains**:
- System overview and scope definition
- Complete pipeline architecture with diagrams
- Data flow walkthrough (6 phases)
- Module specifications:
  - nets_loader.py
  - bayesian_employee_estimator.py
  - survival_detector.py
  - pipeline.py
- Output schema (Parquet columns + example records)
- Compliance and quality standards
- Quick start guide

**Read this if**: You need to understand how the system works or integrate it

---

### docs/QUICK_REFERENCE.md (DAILY WORKFLOW)
**Purpose**: Essential commands and daily operations guide  
**Audience**: Data engineers, analysts  
**Contains**:
- Directory structure
- Installation instructions
- Data preparation checklist
- Running the pipeline (3 methods)
- Configuration customization
- Output file reading examples
- Dashboard startup
- Troubleshooting guide
- Performance optimization
- Key metrics to track

**Read this if**: You need to run or operate the system

---

### src/config.py (CONFIGURATION)
**Purpose**: Centralized configuration and baselines  
**Audience**: Developers, analysts  
**Contains**:
- Geographic boundaries (Minneapolis ZIP codes)
- Industry configuration (NAICS 722513, 446110)
- Employee estimation baselines by NAICS
- Feature engineering parameters
- Parquet output schema
- Application defaults
- Data source priorities

**Customize this for**:
- Changing target industries (modify INDUSTRY_CONFIG)
- Adjusting employee estimation models (modify EMPLOYEE_ESTIMATION_BASELINES)
- Changing feature thresholds (modify REVIEW_DECAY_WINDOW, GEOGRAPHIC_MATCH)
- Expanding geographic coverage (modify TARGET_ZIP_CODES)

---

### src/data/nets_loader.py (DATA LOADING)
**Purpose**: Load, filter, and validate NETS establishment data  
**Key Classes**:
- `NETSLoader`: Main data loading and filtering
- `NETSValidator`: Data quality verification

**Key Methods**:
```python
loader.load_raw()                    # Load CSV
loader.filter_by_state('MN')         # Filter by state
loader.filter_by_naics_codes(['722513'])  # Filter by industry
loader.filter_by_zip_codes([...])    # Filter by geography
loader.filter_active_only(2015)      # Filter to likely active
loader.get_geopandas_gdf()           # Convert to spatial format
loader.get_pipeline_ready(...)       # Complete workflow
```

**Usage Example**:
```python
from src.data.nets_loader import NETSLoader

loader = NETSLoader('data/raw/nets_minneapolis.csv')
df = loader.get_pipeline_ready(
    naics_codes=['722513', '446110'],
    zip_codes=['55401', '55402', ...],
    filter_active=True
)
print(f"Ready for pipeline: {len(df)} records")
```

---

### src/models/bayesian_employee_estimator.py (EMPLOYEE ESTIMATION)
**Purpose**: Estimate employee counts with confidence intervals  
**Key Class**:
- `EmployeeEstimator`: Multi-signal ensemble estimator
- `EmployeeEstimate`: Result dataclass

**Estimation Methods**:
1. **LinkedIn** (weight 50%): Direct from company profiles, highest credibility
2. **Review Velocity** (weight 30%): Recent reviews / historical baseline
3. **Building Area** (weight 15%): Store size correlates with staffing
4. **Job Postings** (weight 5%): Hiring activity indicator

**Usage Example**:
```python
from src.models.bayesian_employee_estimator import EmployeeEstimator
from src.config import EMPLOYEE_ESTIMATION_BASELINES

estimator = EmployeeEstimator(EMPLOYEE_ESTIMATION_BASELINES)

estimate = estimator.estimate(
    record={'duns_id': '123', 'company_name': 'McDonald\'s'},
    naics_code='722513',
    linkedin_headcount=18,
    review_count_3m=45,
    review_count_6_12m=80,
    building_area_sqm=500
)

print(f"Estimated employees: {estimate.point_estimate} ({estimate.ci_lower}-{estimate.ci_upper})")
print(f"Confidence: {estimate.confidence_level}")
```

---

### src/models/survival_detector.py (SURVIVAL DETECTION)
**Purpose**: Detect business operational status and closure probability  
**Key Class**:
- `SurvivalDetector`: Multi-signal survival scorer
- `SurvivalEstimate`: Result dataclass

**Signal Weights**:
1. **Review Recency** (35%): Days since last customer review
2. **Review Decay** (30%): Trend of review activity
3. **Job Postings** (20%): Recent hiring activity
4. **Street View** (15%): Visual operational indicators

**Usage Example**:
```python
from src.models.survival_detector import SurvivalDetector

detector = SurvivalDetector()

estimate = detector.estimate(
    record={'duns_id': '123', 'company_name': 'McDonald\'s'},
    last_review_date='2025-01-15',
    review_count_3m=45,
    review_count_6_12m=80,
    job_postings_6m=3,
    job_postings_peak=5
)

print(f"Survival probability: {estimate.is_active_prob:.2f}")
print(f"Confidence: {estimate.confidence_level}")
print(f"Risk factors: {estimate.risk_factors}")
```

---

### src/data/pipeline.py (ORCHESTRATION)
**Purpose**: End-to-end pipeline orchestration  
**Key Class**:
- `NETSDataPipeline`: Main pipeline controller

**Workflow**:
1. Load and filter NETS data
2. Create spatial representation
3. Enrich with external sources
4. Estimate employees
5. Detect survival status
6. Calculate quality scores
7. Export to Parquet

**Usage Example**:
```python
from src.data.pipeline import NETSDataPipeline

pipeline = NETSDataPipeline(
    nets_csv_path='data/raw/nets_minneapolis.csv',
    output_parquet_path='data/processed/nets_ai_minneapolis.parquet'
)

output_file = pipeline.run(
    linkedin_data='data/external/linkedin_headcount.csv',
    outscraper_data='data/external/outscraper_reviews.csv',
    job_postings_data='data/external/indeed_postings.csv'
)

print(f"Output: {output_file}")
```

---

### dashboard/app.py (VISUALIZATION)
**Purpose**: Interactive Streamlit dashboard  
**Features**:
- 5 tabs: Maps, Employees, Survival, Quality, Details
- Folium heatmaps (employees and survival probability)
- Altair charts (distributions and trends)
- Interactive filters (NAICS, status, employee range, confidence)
- Filterable data table with CSV export
- Summary statistics metrics

**Usage**:
```bash
streamlit run dashboard/app.py
# Opens at http://localhost:8501
```

---

## Typical Workflows

### Workflow 1: First-Time Setup
1. Read **README.md** (5 min)
2. Read **docs/QUICK_REFERENCE.md** - Installation section (10 min)
3. Install dependencies: `pip install -r requirements.txt` (5 min)
4. Prepare NETS CSV in `data/raw/` (varies)

### Workflow 2: Run Pipeline
1. Refer to **docs/QUICK_REFERENCE.md** - Running the Pipeline section
2. Choose Method 1 (automated) or Method 2 (step-by-step)
3. Check logs in `logs/` directory
4. Verify output in `data/processed/nets_ai_minneapolis.parquet`

### Workflow 3: Explore Results
1. Refer to **docs/QUICK_REFERENCE.md** - Output Files section
2. Read Parquet with pandas: `pd.read_parquet('data/processed/...')`
3. Start dashboard: `streamlit run dashboard/app.py`
4. Use interactive filters and maps

### Workflow 4: Customize System
1. Review **PROJECT_REALIGNMENT_SUMMARY.md** - Configuration Customization
2. Edit **src/config.py** parameters
3. Re-run pipeline to apply changes
4. Check results in dashboard

### Workflow 5: Troubleshoot Issues
1. Check **docs/QUICK_REFERENCE.md** - Troubleshooting section
2. Review logs in `logs/` directory
3. Verify data files in `data/raw/` and `data/external/`
4. Check Python and package versions

---

## API Reference Quick Links

### NETS Loader
- `NETSLoader.load_raw()` - Load CSV
- `NETSLoader.filter_by_naics_codes()` - Industry filter
- `NETSLoader.filter_by_zip_codes()` - Geographic filter
- `NETSValidator.check_coordinates()` - Validate locations

### Employee Estimator
- `EmployeeEstimator.estimate_from_linkedin()` - LinkedIn signal
- `EmployeeEstimator.estimate_from_review_velocity()` - Review signal
- `EmployeeEstimator.estimate_from_building_area()` - Area signal
- `EmployeeEstimator.ensemble_estimate()` - Combine signals
- `EmployeeEstimator.process_batch()` - Batch processing

### Survival Detector
- `SurvivalDetector.calculate_review_decay_rate()` - Trend analysis
- `SurvivalDetector.evaluate_review_recency()` - Recency scoring
- `SurvivalDetector.evaluate_job_posting_activity()` - Hiring signal
- `SurvivalDetector.score_survival()` - Multi-signal scoring
- `SurvivalDetector.process_batch()` - Batch processing

### Pipeline
- `NETSDataPipeline.load_and_filter()` - Load data
- `NETSDataPipeline.enrich_with_external_sources()` - Add signals
- `NETSDataPipeline.estimate_employees()` - Run employee model
- `NETSDataPipeline.detect_survival_status()` - Run survival model
- `NETSDataPipeline.export_parquet()` - Write output
- `NETSDataPipeline.run()` - Execute complete pipeline

---

## Configuration Parameters

All customizable in **src/config.py**:

- `INDUSTRY_CONFIG` - NAICS definitions and descriptions
- `EMPLOYEE_ESTIMATION_BASELINES` - Industry-specific employment models
- `PARQUET_OUTPUT_SCHEMA` - Output column specifications
- `TARGET_ZIP_CODES` - Geographic coverage
- `REVIEW_DECAY_WINDOW` - Feature engineering thresholds
- `GEOGRAPHIC_MATCH` - Coordinate matching parameters
- `JOB_POSTING_WINDOW` - Job posting analysis windows
- `DATA_SOURCE_PRIORITY` - Integration priority order

---

## Support and Issues

**For questions about**:
- System design: See **docs/ARCHITECTURE.md**
- Running the pipeline: See **docs/QUICK_REFERENCE.md**
- Configuration: See **src/config.py** docstrings
- Data loading: See **src/data/nets_loader.py** docstrings
- Employee estimation: See **src/models/bayesian_employee_estimator.py** docstrings
- Survival detection: See **src/models/survival_detector.py** docstrings
- Dashboard: See **dashboard/app.py** docstrings

All code includes comprehensive docstrings, type hints, and inline comments.

---

## Document Version

**Created**: January 29, 2025  
**Project**: NETS Business Data Enhancement System  
**Version**: 1.0  
**Status**: Production Ready
