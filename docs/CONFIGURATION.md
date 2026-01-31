# 

## 1. CSV

CSV55

****:
- `name` - 
- `address` - 
- `google_rating` - Google
- `google_reviews_total` - Google
- `linkedin_employee_count` - LinkedIn
- `ai_employees_estimate` - AI
- `ai_status` - AI (Active/Inactive/Uncertain)
- `overall_confidence` - (High/Medium/Low)

## 2. Outscraper 

 (https://github.com/outscraper/outscraper-python)

**API Key**:
```python
from outscraper import ApiClient
client = ApiClient(api_key='SECRET_API_KEY')
```

**API Key**:
1. https://outscraper.com/
2. 
3. ProfileAPI key
4. `.env` :
 ```
 OUTSCRAPER_API_KEY=your_api_key_here
 ```

****: $1/1000 (Google Maps API97%)

****:
- Google Maps5
- Popular times
- 

## 3. LinkedIn Scraper v3.0+ 

Playwright

****:
```bash
pip install linkedin-scraper>=3.1.0 playwright
playwright install chromium
```

** .env**:
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

****:
- `.linkedin_session.json`
- 

****: LinkedInToS

## 4. 

1. ****:
 ```bash
 cp .env.example .env
 ```

2. ** .env API**:
 ```
 OPENAI_API_KEY=sk-your_key_here # 
 GOOGLE_MAPS_API_KEY=AIza_your_key_here # 
 OUTSCRAPER_API_KEY=your_key_here # 
 LINKEDIN_EMAIL=your_email@example.com # 
 LINKEDIN_PASSWORD=your_password # 
 ```

3. ****:
 ```bash
 python scripts/03_complete_pipeline.py --limit 10
 ```

## 5. 

| | | |
|------|------|------|
| Google Maps | OK | GOOGLE_MAPS_API_KEY () |
| GPT | OK | OPENAI_API_KEY () |
| Wayback | PARTIAL | API |
| Outscraper | NEEDS_CONFIG | OUTSCRAPER_API_KEY |
| LinkedIn | NEEDS_CONFIG | LINKEDIN_EMAIL + PASSWORD |

## 6. 

```bash
# 
python scripts/03_complete_pipeline.py

# 
python scripts/03_complete_pipeline.py --limit 10

# Wayback
python scripts/03_complete_pipeline.py --skip-wayback

# GPT
python scripts/03_complete_pipeline.py --skip-gpt

# 
python scripts/03_complete_pipeline.py --help
```
