# AI-BDD System Architecture and Function Reference

## Table of Contents
1. [Project Overview](#project-overview)
2. [File Structure and Purpose](#file-structure)
3. [Module Documentation](#module-documentation)
4. [Execution Workflow](#execution-workflow)
5. [Next Steps](#next-steps)

---

## Project Overview

**AI-Business Dynamics Database (AI-BDD)** is a data collection and analysis system that combines Google Maps API, Wayback Machine archival data, and GPT-4o-mini natural language processing to validate business operational status, establishment dates, and employment estimates.

**Core Problem**: NETS database contains 67% imputed data with 24-month closure detection lag (Crane & Decker, 2019).

**Solution**: Multi-source signal alignment using public APIs and AI classification.

---

## File Structure and Purpose

### Core Agent Modules (`src/agents/`)

#### 1. `google_maps_agent.py`
**Purpose**: Interface with Google Maps Places API

**Class**: `GoogleMapsAgent`

**Functions**:

```python
def __init__(self):
 """
 Initialize Google Maps client
 
 Input: None (reads GOOGLE_MAPS_API_KEY from environment)
 Output: GoogleMapsAgent instance
 
 Raises: Warning if API key missing
 """

def search_places(self, query: str) -> list:
 """
 Search for places with automatic pagination
 
 Input:
 query (str): Search query (e.g., "coffee shops in Minneapolis 55401")
 
 Output:
 list: Array of place objects, each containing:
 - place_id (str): Unique identifier
 - name (str): Business name
 - formatted_address (str): Full address
 - geometry (dict): {location: {lat: float, lng: float}}
 
 Implementation:
 - Handles up to 5 pages (60 results per query)
 - Automatic retry with exponential backoff for pagination tokens
 - 2-5 second delays between page requests
 """

def get_place_details(self, place_id: str) -> dict:
 """
 Retrieve comprehensive place details
 
 Input:
 place_id (str): Google Maps place identifier
 
 Output:
 dict: Detailed place information including:
 - name, formatted_address, formatted_phone_number
 - website, url (Google Maps link)
 - rating (float), user_ratings_total (int)
 - reviews (list): Array of review objects with:
 * author_name, rating, text, time (UNIX timestamp)
 - opening_hours (dict): weekday_text, open_now
 - geometry.location: {lat, lng}
 - types (list): Place type classifications
 - serves_* (bool): Service attributes
 
 Fields Parameter: Requests extensive field list to maximize data retrieval
 """
```

**Cost**: $0.032 per search, $0.017 per details request

---

#### 2. `wayback_agent.py`
**Purpose**: Query Internet Archive Wayback Machine for historical website snapshots

**Class**: `WaybackAgent`

**Functions**:

```python
def __init__(self, user_agent: str = "AI-BDD-Research/1.0"):
 """
 Initialize Wayback Machine API client
 
 Input:
 user_agent (str): Custom user agent for API requests
 
 Output: WaybackAgent instance
 
 Configuration: Sets 15-second timeout, 1-second delay between requests
 """

def get_first_snapshot(self, url: str) -> dict:
 """
 Retrieve earliest archived snapshot of a website
 
 Input:
 url (str): Website URL to query
 
 Output:
 dict or None:
 - date (datetime): Snapshot date
 - url (str): Archive.org snapshot URL
 - timestamp (str): CDX timestamp format (YYYYMMDDHHmmss)
 - year (int): Extracted year
 
 Returns None if: No snapshots exist or API error
 
 Application: Validate claimed establishment year
 """

def get_last_snapshot(self, url: str) -> dict:
 """
 Retrieve most recent archived snapshot
 
 Input:
 url (str): Website URL
 
 Output:
 dict or None: Same structure as get_first_snapshot()
 
 Application: Detect website abandonment, estimate closure timing
 """

def validate_establishment_year(self, url: str, claimed_year: int) -> dict:
 """
 Cross-validate claimed founding year with web archive
 
 Input:
 url (str): Business website
 claimed_year (int): Year business claims to have been established
 
 Output:
 dict:
 - is_validated (bool): True if first snapshot claimed_year
 - first_snapshot_year (int or None): Actual year of first archive
 - year_difference (int): claimed_year - first_snapshot_year
 - confidence (str): "High", "Medium", "Low", or "No Data"
 
 Confidence Rules:
 - High: |difference| 1 year
 - Medium: 1 < |difference| 3 years
 - Low: |difference| > 3 years
 """

def check_business_active(self, url: str, cutoff_date: datetime) -> dict:
 """
 Determine if business was active after specified date
 
 Input:
 url (str): Business website
 cutoff_date (datetime): Reference date for activity check
 
 Output:
 dict:
 - is_active (bool): True if last snapshot after cutoff
 - last_snapshot_date (datetime or None)
 - days_since_cutoff (int): Days between cutoff and last snapshot
 - confidence (str): Based on recency
 
 Application: Closure detection (e.g., active after 2020-01-01?)
 """

def get_snapshot_count(self, url: str) -> int:
 """
 Count total archived snapshots for URL
 
 Input:
 url (str): Website URL
 
 Output:
 int: Number of snapshots (0 if none or error)
 
 Application: Website activity indicator (high count = established presence)
 """
```

**Cost**: Free (Internet Archive public service)

---

#### 3. `gpt_analyzer.py`
**Purpose**: GPT-4o-mini powered business analysis

**Class**: `GPTAnalyzer`

**Functions**:

```python
def __init__(self, model: str = "gpt-4o-mini"):
 """
 Initialize OpenAI client
 
 Input:
 model (str): Model identifier (default: gpt-4o-mini)
 
 Output: GPTAnalyzer instance
 
 Raises: Warning if OPENAI_API_KEY missing
 
 Model Specs:
 - Input: $0.150 per 1M tokens
 - Output: $0.600 per 1M tokens
 - Context: 128k tokens
 """

def classify_business_status(self, business_data: dict) -> dict:
 """
 Classify business operational status
 
 Input:
 business_data (dict): Aggregated business information
 Required fields:
 - name, address
 - google_rating, user_ratings_total, review_count
 - last_review_date, oldest_review_date
 - operating_hours, is_open_now
 - website, website_accessible
 - wayback_last_snapshot, wayback_snapshot_count
 
 Output:
 dict:
 - status (str): "Active", "Inactive", or "Uncertain"
 - confidence (float): 0.0 to 1.0
 - reasoning (str): Explanation of classification
 - risk_factors (list): Identified warning signs
 
 Prompt Strategy:
 - Structured JSON output
 - Evidence-based reasoning
 - Considers review recency, website status, Wayback activity
 
 Classification Criteria:
 - Active: Recent reviews (<6 months), accessible website, high rating
 - Inactive: No recent reviews (>12 months), dead website, low Wayback activity
 - Uncertain: Mixed signals, insufficient data
 """

def estimate_employment(self, business_data: dict) -> dict:
 """
 Estimate employee count from observable signals
 
 Input:
 business_data (dict): Business information including:
 - name, category (e.g., "coffee shop")
 - google_rating, review_count
 - attributes (e.g., "Takeout, Delivery, Dine-in")
 - operating_hours
 
 Output:
 dict:
 - min_employees (int): Lower bound estimate
 - max_employees (int): Upper bound estimate
 - best_estimate (int): Most likely value
 - confidence (float): 0.0 to 1.0
 - reasoning (str): Basis for estimate
 
 Estimation Factors:
 - Business category typical staffing (coffee shop: 3-8, gym: 5-20)
 - Service offerings (dine-in requires more staff than takeout)
 - Operating hours (7-day operation suggests larger staff)
 - Review volume (high traffic implies more employees)
 """

def verify_naics_classification(self, business_data: dict, 
 target_naics: str, definition: str) -> dict:
 """
 Verify NAICS code appropriateness
 
 Input:
 business_data (dict): Business information
 - name, google_types (e.g., ["cafe", "restaurant"])
 - attributes, review_snippets
 target_naics (str): Expected NAICS code (e.g., "722515")
 definition (str): NAICS definition text
 
 Output:
 dict:
 - is_match (bool): True if business matches target NAICS
 - actual_naics_suggestion (str): Recommended NAICS if mismatch
 - confidence (float): 0.0 to 1.0
 - reasoning (str): Explanation
 
 Example:
 Input: Business labeled "cafe", target NAICS 722515 (snack/coffee shops)
 Output: {is_match: True, confidence: 0.95, reasoning: "..."}
 
 Input: Business labeled "full-service restaurant", target NAICS 722515
 Output: {is_match: False, actual_naics_suggestion: "722511", ...}
 """

def analyze_business_comprehensive(self, business_data: dict, 
 target_naics: str, definition: str) -> dict:
 """
 Execute all three analyses in single call
 
 Input: Combined parameters from above functions
 
 Output:
 dict: Merged results from:
 - classify_business_status()
 - estimate_employment()
 - verify_naics_classification()
 
 Note: More cost-effective than three separate API calls when all analyses needed
 """
```

**Cost**: ~$0.0005 per business (3 API calls)

---

### Utility Modules (`src/utils/`)

#### 4. `logger.py`
**Purpose**: Centralized logging configuration

**Function**:

```python
def setup_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
 """
 Create configured logger instance
 
 Input:
 name (str): Logger identifier
 log_level (int): Logging level (default: INFO)
 
 Output:
 logging.Logger: Configured logger with:
 - File handler: logs/{name}_{timestamp}.log
 - Console handler: stdout
 - Format: [YYYY-MM-DD HH:MM:SS] LEVEL: message
 
 File Location: Automatically creates logs/ directory
 
 Usage:
 logger = setup_logger("AI-BDD-Pipeline")
 logger.info("Processing started")
 """
```

---

#### 5. `helpers.py`
**Purpose**: Common utility functions

**Functions**:

```python
def check_website_status(url: str, timeout: int = 10) -> dict:
 """
 Verify website accessibility
 
 Input:
 url (str): Website URL
 timeout (int): Request timeout in seconds
 
 Output:
 dict:
 - status_code (int or None): HTTP status (200, 404, etc.)
 - accessible (bool): True if status_code == 200
 - error (str or None): Error message if request failed
 
 Implementation: Uses requests library with SSL verification
 """

def parse_review_date(date_str: str) -> datetime:
 """
 Convert Google review timestamp to datetime
 
 Input:
 date_str (str): Date string (various formats)
 
 Output:
 datetime or None: Parsed date
 
 Supports: ISO format, UNIX timestamps, common date formats
 """

def is_recent_activity(last_date: str, days_threshold: int = 180) -> bool:
 """
 Determine if activity is recent
 
 Input:
 last_date (str): Date string (YYYY-MM-DD)
 days_threshold (int): Recency cutoff (default: 180 days)
 
 Output:
 bool: True if activity within threshold
 
 Application: Identify businesses with recent customer engagement
 """

def calculate_confidence_score(indicators: dict) -> str:
 """
 Compute overall data confidence level
 
 Input:
 indicators (dict): Binary indicators
 - has_recent_reviews (bool)
 - review_count (int) 
 - website_accessible (bool)
 - has_hours (bool)
 - wayback_verified (bool)
 
 Output:
 str: "High", "Medium", or "Low"
 
 Scoring:
 High: All 5 indicators TRUE, OR review_count > 10 AND 4 indicators TRUE
 Medium: 3-4 indicators TRUE
 Low: <3 indicators TRUE
 """

def calculate_api_cost(num_places: int, gpt_calls_per_place: int = 3) -> dict:
 """
 Estimate total API costs
 
 Input:
 num_places (int): Number of businesses to process
 gpt_calls_per_place (int): GPT API calls per business
 
 Output:
 dict:
 - google_search_cost (float)
 - google_details_cost (float)
 - gpt_cost (float)
 - total_cost (float)
 - formatted_total (str): e.g., "$52.00"
 
 Assumptions:
 - Google Search: $0.032 per query
 - Google Details: $0.017 per request
 - GPT: $0.0005 per business (800 tokens avg)
 """

def normalize_url(url: str) -> str:
 """
 Standardize URL format
 
 Input:
 url (str): Raw URL
 
 Output:
 str: Normalized URL (lowercase, strip trailing slash)
 
 Application: Consistent Wayback Machine queries
 """
```

---

### Configuration Module

#### 6. `src/config.py`
**Purpose**: Centralized configuration constants

**Key Variables**:

```python
TARGET_CITY_NAME = "Minneapolis"
TARGET_STATE = "MN"

TARGET_ZIP_CODES = [
 "55401", "55402", "55403", "55404", "55405", 
 "55406", "55407", "55408", "55417"
]

CATEGORY_CONFIG = {
 "coffee": {
 "search_term": "coffee shops",
 "target_naics": "722515",
 "definition": "Establishments primarily engaged in preparing and serving specialty snacks and nonalcoholic beverages...",
 "examples": "coffee shops, espresso bars, cafes"
 },
 "gym": {...},
 "library": {...},
 # ... 7 categories total
}

DEFAULT_TASK = "coffee"

FINAL_COLUMNS = [
 "name", "place_id", "address", "phone", "website",
 "latitude", "longitude", 
 "google_rating", "user_ratings_total", "review_count",
 "wayback_first_snapshot", "wayback_snapshot_count",
 "ai_status", "ai_status_confidence", "ai_employees_estimate",
 # ... 40+ columns total
]
```

**Usage**: Import in all scripts for consistent configuration

---

### Execution Scripts (`scripts/`)

#### 7. `03_complete_pipeline.py`
**Purpose**: Main data collection and analysis pipeline

**Workflow**:

```python
def main():
 """
 Complete execution pipeline
 
 Command-line Arguments:
 --task <category>: Business category (default: coffee)
 --city <name>: Target city (default: Minneapolis)
 --list: Display available categories
 --limit <n>: Process only first n businesses
 --skip-wayback: Bypass Wayback validation
 --skip-gpt: Bypass GPT analysis
 
 Execution Steps:
 1. Parse arguments and validate configuration
 2. Initialize agents (GoogleMaps, Wayback, GPT)
 3. Search Google Maps across all ZIP codes
 4. Deduplicate results by place_id
 5. For each business:
 a. collect_business_data() - Google Maps details
 b. enhance_with_wayback() - Historical validation
 c. enhance_with_gpt() - AI analysis
 d. calculate_overall_confidence() - Data quality score
 6. Export to CSV with timestamp
 7. Generate statistical summary
 
 Output:
 CSV file: data/processed/ai_bdd_{city}_{category}_{timestamp}.csv
 Log file: logs/ai-bdd-pipeline_{timestamp}.log
 
 Exit Codes:
 0: Success
 1: Configuration error or no data collected
 """

def collect_business_data(place_id: str, maps_agent: GoogleMapsAgent) -> dict:
 """
 Extract comprehensive Google Maps data
 
 Input:
 place_id (str): Google Maps identifier
 maps_agent (GoogleMapsAgent): Initialized agent
 
 Output:
 dict: 25+ fields including location, rating, reviews, hours, attributes
 
 Processing:
 - Parse review timestamps to extract date range
 - Concatenate review snippets (first 100 chars each, max 5 reviews)
 - Extract service attributes (breakfast, delivery, etc.)
 - Format hours as semicolon-separated list
 """

def enhance_with_wayback(business_data: dict, wayback_agent: WaybackAgent) -> dict:
 """
 Augment data with Wayback Machine fields
 
 Input:
 business_data (dict): Existing business data
 wayback_agent (WaybackAgent): Initialized agent
 
 Output:
 dict: business_data updated with:
 - wayback_first_snapshot, wayback_first_year
 - wayback_last_snapshot, wayback_last_year
 - wayback_snapshot_count
 
 Skips: Businesses without website field
 """

def enhance_with_gpt(business_data: dict, gpt_analyzer: GPTAnalyzer, 
 config: dict) -> dict:
 """
 Add GPT analysis fields
 
 Input:
 business_data (dict): Existing data
 gpt_analyzer (GPTAnalyzer): Initialized analyzer
 config (dict): Category configuration from CATEGORY_CONFIG
 
 Output:
 dict: business_data updated with 10+ AI-generated fields
 
 Processing:
 - Calls classify_business_status()
 - Calls estimate_employment()
 - Calls verify_naics_classification()
 - Merges results into business_data dict
 """
```

**Execution Time**: ~2 hours for 690 businesses (all 7 categories)

---

#### 8. `validate_environment.py`
**Purpose**: Pre-flight environment verification

**Functions**:

```python
def check_imports() -> bool:
 """
 Verify all required packages installed
 
 Output:
 bool: True if all packages available
 
 Tests: pandas, numpy, openai, googlemaps, waybackpy, requests, 
 beautifulsoup4, lxml, python-dotenv, pydantic, httpx, tqdm, openpyxl
 """

def check_env() -> bool:
 """
 Verify API keys configured
 
 Output:
 bool: True if OPENAI_API_KEY and GOOGLE_MAPS_API_KEY present
 
 Display: Masked key values (first 8 + last 4 characters)
 """

def check_project_structure() -> bool:
 """
 Verify directory structure and critical files
 
 Output:
 bool: True if all required directories and files exist
 
 Checks:
 Directories: src/agents, src/data, scripts, data/processed, logs, notebooks, tests, docs
 Files: src/config.py, all agent files, scripts/03_complete_pipeline.py, requirements.txt
 """

def test_agents() -> bool:
 """
 Test agent instantiation
 
 Output:
 bool: True if all agents can be imported and initialized
 
 Tests: GoogleMapsAgent, WaybackAgent, GPTAnalyzer, Logger, Helpers
 """

def test_wayback_sample() -> bool:
 """
 Test Wayback Machine API connectivity
 
 Output:
 bool: True if can retrieve snapshots for python.org
 
 Purpose: Verify Internet Archive API accessible
 """

def main() -> int:
 """
 Execute all validation checks
 
 Output:
 int: Exit code (0 = all passed, 1 = failures detected)
 
 Display: Color-coded test results with summary statistics
 """
```

**Usage**: Run before first pipeline execution

```powershell
python scripts/validate_environment.py
```

---

#### 9. `run_pipeline.ps1`
**Purpose**: Interactive PowerShell launcher

**Features**:
- Automatic virtual environment activation
- Dependency verification
- .env file validation
- Menu-driven execution options

**Menu Options**:
1. List available categories
2. Test run (10 places)
3-6. Full analysis for specific categories
7. Custom parameters

**Usage**:
```powershell
.\run_pipeline.ps1
```

---

## Execution Workflow

### Standard Analysis Workflow

```
1. Environment Setup
 [|][-] Activate virtual environment
 [|][-] Verify dependencies (validate_environment.py)
 [_][-] Check API keys in .env

2. Data Collection (03_complete_pipeline.py)
 [|][-] Step 1: Google Maps Search
 [|][-] Query: "{category} in {city} {zip_code}"
 [|][-] Iterate: 9 ZIP codes
 [|][-] Paginate: Up to 60 results per ZIP
 [_][-] Deduplicate: Unique place_id set
 
 [|][-] Step 2: For Each Business
 [|][-] Google Maps Details (0.017 USD)
 [|][-] Website Status Check (free)
 [|][-] Wayback Validation (free)
 [|][-] First snapshot Establishment validation
 [|][-] Last snapshot Closure detection
 [_][-] Snapshot count Activity indicator
 [_][-] GPT Analysis (0.0005 USD)
 [|][-] Status classification
 [|][-] Employment estimation
 [_][-] NAICS verification
 
 [_][-] Step 3: Export
 [|][-] CSV: data/processed/ai_bdd_*.csv
 [|][-] Log: logs/ai-bdd-pipeline_*.log
 [_][-] Summary statistics to console

3. Data Validation
 [|][-] Confidence scoring (helpers.calculate_confidence_score)
 [|][-] Field completeness checks
 [_][-] Outlier detection (optional)

4. Analysis (Jupyter Notebooks)
 [|][-] Load CSV with pandas
 [|][-] Descriptive statistics
 [|][-] Visualizations (folium maps, matplotlib charts)
 [_][-] Export figures for publication
```

---

## Next Steps

### Immediate Actions

#### 1. Environment Configuration (Required)
**Location**: Project root directory 
**Action**: Create `.env` file

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx
GOOGLE_MAPS_API_KEY=AIzaSyxxxxxxxxxx
```

**How to Obtain**:
- OpenAI: https://platform.openai.com/api-keys
- Google Maps: https://console.cloud.google.com/google/maps-apis/

**Verification**:
```powershell
python scripts/validate_environment.py
```

---

#### 2. Dependency Installation (Required)
**Location**: Project root directory 
**Action**:

```powershell
.\AIAGENTNETS\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Critical Packages**:
- `waybackpy==3.0.6`: Wayback Machine API wrapper
- `openai==2.15.0`: GPT-4o-mini client
- `googlemaps==4.10.0`: Google Maps API client
- `pandas==3.0.0`: Data manipulation

**Verification**: All checks pass in validate_environment.py

---

#### 3. Test Execution (Recommended)
**Location**: Project root directory 
**Action**:

```powershell
# Test with 10 businesses (~$0.20 cost)
python scripts/03_complete_pipeline.py --task coffee --limit 10
```

**Expected Output**:
```
Step 1: Searching Google Maps...
 Zip 55401: 15 places
 ...
Found 10 unique places

Estimated API cost: $0.20

Step 2: Collecting detailed data...
[1/10] Starbucks
 Checking Wayback for: https://www.starbucks.com
 Running GPT analysis...
 Complete (Confidence: High)
...

COMPLETE!
 Total businesses: 10
 Active (AI): 9
 High confidence: 8
 
Output: data/processed/ai_bdd_Minneapolis_coffee_20260129_*.csv
```

---

### Short-Term Development Tasks

#### 4. Data Validation Module (Optional)
**Location**: `src/data/validator.py` 
**Purpose**: CSV output quality assurance

**Implementation**:
```python
class DataValidator:
 def validate_csv_output(self, df: pd.DataFrame) -> dict:
 """
 Input: pandas DataFrame from pipeline output
 Output: dict with validation results
 - missing_critical_fields (list)
 - outlier_count (int)
 - duplicate_count (int)
 - confidence_distribution (dict)
 """
 
 def compare_with_nets(self, ai_df: pd.DataFrame, 
 nets_df: pd.DataFrame) -> dict:
 """
 Input: AI-BDD DataFrame, NETS DataFrame
 Output: dict with comparison metrics
 - overlap_rate (float)
 - closure_detection_lead_time (int days)
 - employment_mae (float)
 - false_positive_rate (float)
 """
```

**Usage**:
```python
from src.data.validator import DataValidator

validator = DataValidator()
df = pd.read_csv("data/processed/ai_bdd_Minneapolis_coffee_*.csv")
validation_report = validator.validate_csv_output(df)
```

---

#### 5. Secretary of State Integration (Optional)
**Location**: `src/data/sos_loader.py` 
**Purpose**: Cross-reference with state business registrations

**Implementation**:
```python
class SOSLoader:
 def query_business_entity(self, business_name: str, 
 state: str = "MN") -> dict:
 """
 Input:
 business_name (str): Business legal name
 state (str): State abbreviation
 
 Output:
 dict:
 - entity_id (str)
 - registration_date (str)
 - status (str): "Active", "Dissolved", etc.
 - registered_agent (str)
 
 Source: State Secretary of State website (web scraping or API if available)
 """
```

**Data Source**: Minnesota SOS Business Search
https://mblsportal.sos.state.mn.us/Business/Search

---

#### 6. Jupyter Notebook Templates (Recommended)
**Location**: `notebooks/` 
**Purpose**: Interactive data exploration and visualization

**Templates to Create**:

**a. `01_data_quality_assessment.ipynb`**
```python
# Load data
df = pd.read_csv("data/processed/ai_bdd_Minneapolis_coffee_*.csv")

# Descriptive statistics
df.describe()
df['ai_status'].value_counts()
df['overall_confidence'].value_counts()

# Missing data analysis
missing_percent = df.isnull().sum() / len(df) * 100

# Correlation analysis
corr = df[['google_rating', 'review_count', 'wayback_snapshot_count']].corr()
```

**b. `02_spatial_visualization.ipynb`**
```python
import folium

# Create interactive map
m = folium.Map(location=[44.9778, -93.2650], zoom_start=12)

# Add markers
for idx, row in df.iterrows():
 color = 'green' if row['ai_status'] == 'Active' else 'red'
 folium.Marker(
 location=[row['latitude'], row['longitude']],
 popup=row['name'],
 icon=folium.Icon(color=color)
 ).add_to(m)

m.save('output/business_map.html')
```

**c. `03_comparative_analysis.ipynb`**
```python
# Compare AI-BDD with NETS (if available)
import matplotlib.pyplot as plt

# Active rate by ZIP code
active_by_zip = df.groupby('source_zip')['ai_status'].apply(
 lambda x: (x == 'Active').sum() / len(x)
)

# Visualization
active_by_zip.plot(kind='bar', title='Active Rate by ZIP Code')
```

---

#### 7. Unit Testing (Optional)
**Location**: `tests/` 
**Purpose**: Ensure code reliability

**Test Files to Create**:

**a. `tests/test_agents.py`**
```python
import pytest
from src.agents.wayback_agent import WaybackAgent
from src.agents.gpt_analyzer import GPTAnalyzer

def test_wayback_first_snapshot():
 agent = WaybackAgent()
 result = agent.get_first_snapshot("https://www.python.org")
 
 assert result is not None
 assert 'year' in result
 assert result['year'] < 2026
 assert result['year'] > 1990

def test_gpt_status_classification():
 analyzer = GPTAnalyzer()
 test_data = {
 'name': 'Test Coffee Shop',
 'google_rating': 4.5,
 'review_count': 120,
 'last_review_date': '2026-01-15',
 'is_open_now': True
 }
 
 result = analyzer.classify_business_status(test_data)
 
 assert 'status' in result
 assert result['status'] in ['Active', 'Inactive', 'Uncertain']
 assert 0 <= result['confidence'] <= 1
```

**Run Tests**:
```powershell
pytest tests/ -v
```

---

### Medium-Term Research Tasks

#### 8. Yelp API Integration (Optional)
**Location**: `src/agents/yelp_agent.py` 
**Purpose**: Add third data source for triangulation

**Implementation**:
```python
class YelpAgent:
 def __init__(self, api_key: str):
 """
 Input: Yelp Fusion API key
 Output: YelpAgent instance
 
 API: https://www.yelp.com/developers
 Cost: Free tier (5000 requests/day)
 """
 
 def search_businesses(self, term: str, location: str) -> list:
 """
 Input:
 term (str): Search term (e.g., "coffee")
 location (str): Location (e.g., "Minneapolis, MN")
 
 Output:
 list: Business objects with:
 - id, name, rating, review_count
 - coordinates (lat, lng)
 - categories, price
 
 Pagination: Handle up to 1000 results (20 per page)
 """
 
 def get_business_details(self, business_id: str) -> dict:
 """
 Input: Yelp business ID
 Output: Detailed business information
 
 Additional Fields:
 - hours, transactions (delivery, pickup)
 - photos
 - reviews (3 most recent)
 """
```

**Integration**:
- Add `yelp_rating`, `yelp_review_count` to FINAL_COLUMNS
- Cross-validate with Google Maps data
- Detect discrepancies (e.g., active on Google but missing on Yelp)

---

#### 9. Automated Scheduling (Recommended)
**Location**: `.github/workflows/` or Windows Task Scheduler 
**Purpose**: Periodic data collection for longitudinal analysis

**GitHub Actions Workflow** (`.github/workflows/monthly_collection.yml`):
```yaml
name: Monthly Data Collection

on:
 schedule:
 - cron: '0 0 1 * *' # First day of each month

jobs:
 collect:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v3
 - name: Set up Python
 uses: actions/setup-python@v4
 with:
 python-version: '3.10'
 - name: Install dependencies
 run: pip install -r requirements.txt
 - name: Run pipeline
 env:
 OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
 GOOGLE_MAPS_API_KEY: ${{ secrets.GOOGLE_MAPS_API_KEY }}
 run: python scripts/03_complete_pipeline.py --task coffee
 - name: Upload results
 uses: actions/upload-artifact@v3
 with:
 name: monthly-data
 path: data/processed/
```

**Windows Task Scheduler**:
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute 'python' `
 -Argument 'scripts/03_complete_pipeline.py --task coffee' `
 -WorkingDirectory 'D:\NETS-AI'

$trigger = New-ScheduledTaskTrigger -Monthly -At 2am -DaysOfMonth 1

Register-ScheduledTask -TaskName "AI-BDD-Monthly" `
 -Action $action -Trigger $trigger
```

---

#### 10. Statistical Modeling (Advanced)
**Location**: `src/models/pgbdm.py` 
**Purpose**: Probabilistic Generative Business Dynamics Model

**Objectives**:
- Model entry/exit rates by category
- Estimate employment dynamics
- Predict closure risk

**Implementation Sketch**:
```python
class PGBDM:
 """
 Probabilistic Generative Business Dynamics Model
 
 Input:
 historical_data (pd.DataFrame): Time series of business observations
 
 Methods:
 fit(): Estimate model parameters using MLE or MCMC
 predict_closure_risk(): P(closure | observed_signals)
 simulate_dynamics(): Generate synthetic business population
 
 Model Structure:
 - Entry: Poisson process with ZIP-code specific rates
 - Exit: Survival analysis (Cox proportional hazards)
 - Employment: Zero-inflated negative binomial
 
 References:
 - Crane & Decker (2019) for NETS critique
 - Haltiwanger et al. (2013) for establishment dynamics
 """
 
 def fit(self, df: pd.DataFrame, method: str = 'mle'):
 """
 Input:
 df (pd.DataFrame): Panel data with columns:
 - business_id, year, status, employees
 method (str): 'mle' or 'mcmc'
 
 Output:
 self: Fitted model with .params attribute
 """
 
 def predict_closure_risk(self, business_data: dict) -> float:
 """
 Input: Single business observation
 Output: float (0 to 1) probability of closure in next 6 months
 
 Features:
 - Review velocity decline
 - Rating deterioration
 - Website inactivity
 - Wayback snapshot gap
 """
```

**Usage**:
```python
from src.models.pgbdm import PGBDM

# Load historical data
df_2020 = pd.read_csv("data/processed/ai_bdd_Minneapolis_coffee_202001.csv")
df_2026 = pd.read_csv("data/processed/ai_bdd_Minneapolis_coffee_202601.csv")

# Merge and label
panel = merge_panel_data(df_2020, df_2026)

# Fit model
model = PGBDM()
model.fit(panel)

# Predict
current_business = {...}
risk = model.predict_closure_risk(current_business)
print(f"Closure probability: {risk:.2%}")
```

---

### Long-Term Publication Tasks

#### 11. Paper Preparation
**Location**: `docs/paper/` 
**Target**: *Environment and Planning B: Urban Analytics and City Science*

**Required Sections**:
1. **Introduction**: NETS imputation problem, research gap
2. **Literature Review**: Business dynamics measurement, data quality issues
3. **Methodology**: Multi-source signal alignment, AI classification
4. **Data**: Minneapolis pilot study, 7 business categories
5. **Results**: Validation against ground truth, cost analysis
6. **Discussion**: Policy implications, limitations, future work
7. **Conclusion**: Summary of contributions

**Supplementary Materials**:
- Code repository (GitHub)
- Replication data (anonymized CSV)
- API cost calculator (Excel)

---

#### 12. Reproducibility Package
**Location**: Root directory 
**Files to Include**:

- `REPLICATION_GUIDE.md`: Step-by-step instructions
- `data/sample/`: 100-business sample dataset
- `results/tables/`: LaTeX formatted tables
- `results/figures/`: Publication-quality figures
- `LICENSE`: MIT or GPL license
- `CITATION.cff`: Citation file format

---

## Summary

### System Components

| Module | Purpose | Input | Output | Cost |
|--------|---------|-------|--------|------|
| `google_maps_agent.py` | POI search and details | Query string | Place data dict | $0.049/place |
| `wayback_agent.py` | Historical validation | URL | Snapshot metadata | Free |
| `gpt_analyzer.py` | AI classification | Business data dict | Analysis dict (status, employment, NAICS) | $0.0005/place |
| `logger.py` | Event logging | Log level | Logger instance | N/A |
| `helpers.py` | Utility functions | Various | Various | N/A |
| `config.py` | Configuration | N/A | Constants | N/A |
| `03_complete_pipeline.py` | Orchestration | CLI args | CSV file | $2/100 places |
| `validate_environment.py` | Pre-flight checks | N/A | Boolean status | N/A |

### Critical Path

```
1. Setup (30 min)
 Obtain API keys
 Install dependencies
 Validate environment

2. Test Run (10 min, $0.20)
 Execute with --limit 10
 Verify CSV output
 Review logs

3. Full Analysis (2 hours, $15)
 Run all 7 categories
 Export 690 businesses
 Generate summary stats

4. Data Analysis (ongoing)
 Create Jupyter notebooks
 Visualize results
 Statistical testing

5. Publication (3-6 months)
 Draft manuscript
 Peer review
 Revisions
```

### Key Deliverables

**Code**: Fully documented Python pipeline 
**Data**: CSV files with 40+ fields per business 
**Documentation**: Technical reference (this file) 
**Paper**: Academic manuscript for EPB journal 
**Replication Package**: GitHub repository with sample data

---

**Current Status**: Core implementation complete, ready for test execution 
**Next Action**: Configure `.env` file and run `validate_environment.py`
