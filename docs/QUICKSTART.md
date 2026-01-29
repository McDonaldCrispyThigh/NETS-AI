# AI-BDD Quick Start Guide

## Prerequisites

### 1. Install Python Dependencies
```powershell
cd d:\NETS-AI
.\AIAGENTNETS\Scripts\Activate.ps1  # Activate virtual environment
pip install -r requirements.txt
```

### 2. Configure API Keys
Create `.env` file in project root directory:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

## Execution Workflow

### List Available Business Categories
```powershell
python scripts/03_complete_pipeline.py --list
```

Expected output:
```
Available Business Categories:
------------------------------------------------------------
  coffee       -> coffee shops              NAICS: 722515
  gym          -> gyms                      NAICS: 713940
  library      -> libraries                 NAICS: 519120
  park         -> parks                     NAICS: 712190
  grocery      -> grocery stores            NAICS: 445110
  civic        -> civic organizations       NAICS: 813410
  religion     -> religious organizations   NAICS: 813110
```

### Execute Complete Analysis
```powershell
# Analyze Minneapolis coffee shops (default configuration)
python scripts/03_complete_pipeline.py

# Specify target category
python scripts/03_complete_pipeline.py --task gym

# Limit sample size for testing
python scripts/03_complete_pipeline.py --task coffee --limit 10
```

### Rapid Execution Mode (Skip Optional Components)
```powershell
# Skip Wayback Machine validation (faster execution)
python scripts/03_complete_pipeline.py --skip-wayback

# Skip GPT analysis (reduce API costs)
python scripts/03_complete_pipeline.py --skip-gpt

# Skip both (Google Maps data only)
python scripts/03_complete_pipeline.py --skip-wayback --skip-gpt
```

## Output Data Structure

### File Location
```
data/processed/ai_bdd_Minneapolis_coffee_20250102_143022.csv
```

### Output Fields

#### Google Maps Core Data
- `name`, `address`, `phone`, `website`, `google_url`
- `latitude`, `longitude`
- `google_rating`, `user_ratings_total`, `review_count`
- `last_review_date`, `oldest_review_date`
- `operating_hours`, `is_open_now`
- `attributes`, `google_types`

#### Wayback Machine Historical Validation
- `wayback_first_snapshot`: Date of earliest web archive (YYYY-MM-DD)
- `wayback_first_year`: Year of first snapshot
- `wayback_last_snapshot`: Date of most recent snapshot
- `wayback_last_year`: Year of last snapshot
- `wayback_snapshot_count`: Total number of archived snapshots
- **Application**: Validate establishment year, detect closure timing

#### GPT-4o-mini AI Analysis
- `ai_status`: Active / Inactive / Uncertain
- `ai_status_confidence`: Confidence score (0.0-1.0)
- `ai_status_reasoning`: Textual explanation
- `ai_risk_factors`: List of identified risk factors

- `ai_employees_min`: Minimum employee count estimate
- `ai_employees_max`: Maximum employee count estimate
- `ai_employees_estimate`: Best estimate

- `ai_naics_match`: Boolean (True/False)
- `ai_naics_suggested`: Recommended NAICS code
- `ai_naics_confidence`: Classification confidence
- `ai_naics_reasoning`: Matching rationale
- **Application**: Intelligent classification, overcome manual annotation costs

#### Metadata
- `source_zip`: Source ZIP code
- `target_naics`: Target NAICS code
- `category`: Business category
- `overall_confidence`: High / Medium / Low
- `collection_date`: Data collection date

## API Cost Estimation

### Per 1,000 Locations
```
Google Maps API:
  - Places Search:  $32.00 (0.032 per search)
  - Place Details:  $17.00 (0.017 per request)
  
OpenAI GPT-4o-mini:
  - 3 calls/location: $3.00 (0.150 per 1M tokens)
  
Wayback Machine:    $0.00 (free public service)

Total: approximately $52 per 1,000 locations
```

### Comparison with NETS Database
- **NETS**: $50,000+ annual subscription
- **AI-BDD**: <$5,000 annually (100,000 locations)
- **Cost Reduction**: >90%

## Pipeline Workflow

### Step 1: Google Maps Search
```
Iterate through 9 Minneapolis ZIP codes × search term
→ Grid-based nearby search (optional) → Deduplicate results → Generate unique place_id list
```

Note: Google Places API returns a limited review sample. The pipeline preserves total review counts from Google (`google_reviews_total`) and enriches review signals with Yelp Fusion API when available.

### Step 2: Data Collection and Analysis
For each location:
1. **Google Maps Details**: Retrieve comprehensive information (address, phone, rating, hours)
2. **Website Verification**: Check HTTP status code and accessibility
3. **Wayback Validation**: Retrieve first/last snapshots, total archive count
4. **GPT Analysis**: 
   - Classify business status (Active/Inactive)
   - Estimate employee count
   - Verify NAICS code

### Step 3: Export and Reporting
- Generate CSV file
- Statistical summary (active count, confidence distribution)
- Logging in `logs/` directory

## Data Validation Methodology

### Multi-Source Signal Alignment

| Signal Source | Detection Metric | Application |
|--------------|-----------------|-------------|
| Google Maps | Last review date | Detect closures (>180 days without reviews = suspicious) |
| Wayback Machine | Last snapshot date | Verify website activity |
| Website Status | HTTP 200 response | Confirm online presence |
| GPT-4o-mini | Aggregate judgment | Integrate multiple weak signals |

### Confidence Scoring Rules
```python
indicators = {
    'has_recent_reviews': Reviews within last 180 days,
    'review_count': More than 10 reviews,
    'website_accessible': HTTP 200 status,
    'has_hours': Operating hours available,
    'wayback_verified': Snapshot count > 0
}

- 5 indicators met → High confidence
- 3-4 indicators met → Medium confidence  
- <3 indicators met → Low confidence
```

## Troubleshooting

### 1. API Key Error
```
EnvironmentError: Missing: OPENAI_API_KEY
```
**Solution**: Verify `.env` file exists in project root directory

### 2. Google Maps API Quota
```
OVER_QUERY_LIMIT
```
**Solution**: 
- Use `--limit 10` for testing
- Wait for quota reset (daily limit)
- Upgrade Google Cloud billing

### 3. Wayback Timeout
```
WaybackMachineCDXServerAPI timeout
```
**Solution**: 
- Use `--skip-wayback` to bypass
- Wayback API occasionally unstable, retry recommended

### 4. GPT Cost Concerns
```
Estimated API cost: $156.00
```
**Solution**: 
- Test first with `--limit 10`
- Use `--skip-gpt` to collect raw data only
- Run GPT analysis in batch later

## Advanced Usage

### Batch Processing All Categories
```powershell
foreach ($task in @("coffee", "gym", "library", "grocery")) {
    python scripts/03_complete_pipeline.py --task $task
    Write-Host "Completed: $task"
}
```

### Data Analysis (Jupyter Notebook)
```python
import pandas as pd

df = pd.read_csv("data/processed/ai_bdd_Minneapolis_coffee_*.csv")

# Active rate
active_rate = (df['ai_status'] == 'Active').mean()

# Confidence distribution
df['overall_confidence'].value_counts()

# Wayback verification rate
wayback_verified = (df['wayback_snapshot_count'] > 0).mean()
```

## Related Documentation

- [Complete Methodology](Methodology.md) - Academic background and theoretical foundation
- [API Cost Analysis](api_costs_breakdown.md) - Detailed cost comparison
- [PROMPT Design Guide](PROMPT_GUIDE.md) - GPT prompt engineering

## Best Practices

1. **Small-scale testing first**: Use `--limit 10` to validate workflow
2. **Incremental feature activation**: Start with baseline data, then add Wayback and GPT
3. **Monitor API costs**: Review Google Cloud and OpenAI dashboards
4. **Preserve raw data**: Do not delete CSV files, facilitate reanalysis
5. **Regular backups**: `data/processed/` directory contains all results

---

**Support**: Refer to project README or submit an issue
