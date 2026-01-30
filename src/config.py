"""
NETS Business Data Enhancement System - Configuration Module
Focus: Quick Service Restaurants (NAICS 722513) and Pharmacies (NAICS 446110)
Geographic Area: Minneapolis, MN (Census Tract boundaries)
"""

# ==========================================
# MINNEAPOLIS GEOGRAPHIC BOUNDARIES
# ==========================================
# Census Tract filtering for Minneapolis proper
MINNEAPOLIS_CENSUS_TRACTS = [
    # Core downtown/north Minneapolis
    "27053" + tract for tract in [
        "010100", "010201", "010202", "010300", "010400",
        "020000", "020100", "020200", "020300", "020400",
        "030000", "030100", "030200", "030300", "030400",
        "040000", "040100", "040200", "040300", "040400"
    ]
]

# Alternative: Direct ZIP codes with Minneapolis/St. Paul coverage
TARGET_ZIP_CODES = [
    "55401", "55402", "55403", "55404", "55405",
    "55406", "55407", "55408", "55409", "55410",
    "55411", "55412", "55413", "55414", "55415"
]

# ==========================================
# TARGET INDUSTRIES (NAICS CODES)
# ==========================================
INDUSTRY_CONFIG = {
    "quick_service_restaurant": {
        "naics_code": "722513",
        "naics_title": "Limited-Service Restaurants",
        "search_term": "Quick Service Restaurant",
        "description": "Establishments primarily engaged in preparing and serving food and beverages for immediate consumption without table service. Includes fast food, quick casual, counter service.",
        "examples": "McDonald's, Subway, Chipotle, Taco Bell, Panda Express, Panera, Starbucks (food service)",
        "typical_hours": "6:00 AM - 11:00 PM",
        "peak_hours": "11:30 AM - 1:30 PM (lunch), 5:00 PM - 7:00 PM (dinner)"
    },
    "pharmacy": {
        "naics_code": "446110",
        "naics_title": "Pharmacies",
        "search_term": "Pharmacy",
        "description": "Establishments primarily engaged in retailing prescription drugs and proprietary medicines. Usually includes front store merchandise.",
        "examples": "CVS Pharmacy, Walgreens, Target Pharmacy, Costco Pharmacy, Independent pharmacies",
        "typical_hours": "8:00 AM - 9:00 PM",
        "peak_hours": "9:00 AM - 12:00 PM, 1:00 PM - 3:00 PM"
    }
}

# ==========================================
# EMPLOYEE ESTIMATION COEFFICIENTS
# ==========================================
# Industry-specific baselines (employees per unit metric)
EMPLOYEE_ESTIMATION_BASELINES = {
    "722513": {  # Quick Service Restaurants
        "employees_per_sqm": 0.025,      # 1 employee per 40 sqm (~430 sqft)
        "avg_reviews_per_month": 15.0,
        "avg_employees": 12,
        "avg_store_size_sqm": 500,
        "hiring_intensity_high": 0.8,    # 80% of businesses in growth phase
        "min_employees": 4,
        "max_employees": 50
    },
    "446110": {  # Pharmacies
        "employees_per_sqm": 0.020,      # 1 employee per 50 sqm (~540 sqft)
        "avg_reviews_per_month": 8.0,
        "avg_employees": 10,
        "avg_store_size_sqm": 600,
        "hiring_intensity_high": 0.5,    # 50% of pharmacies in growth phase
        "min_employees": 3,
        "max_employees": 35
    }
}

# ==========================================
# FEATURE ENGINEERING PARAMETERS
# ==========================================
# Review decay analysis (months)
REVIEW_DECAY_WINDOW = {
    "recent": 3,          # Recent reviews (0-3 months)
    "historical": 12,     # Historical baseline (6-12 months)
    "min_review_count": 3  # Require minimum reviews for decay calculation
}

# Geographic matching thresholds
GEOGRAPHIC_MATCH = {
    "haversine_threshold_m": 50,        # Maximum distance for name+address match
    "coordinate_cluster_radius_m": 20   # Cluster nearby coordinates
}

# Job posting activity (for survival detection)
JOB_POSTING_WINDOW = {
    "recent_months": 6,
    "historical_months": 24,
    "posting_activity_threshold": 2     # Min postings to indicate hiring
}

# Street view features
STREET_VIEW = {
    "facade_analysis_enabled": True,
    "edge_detection_threshold": 50,     # OpenCV Canny threshold
    "min_facade_width_m": 3,
    "max_facade_width_m": 15
}

# ==========================================
# OUTPUT SPECIFICATION (PARQUET)
# ==========================================
PARQUET_OUTPUT_SCHEMA = [
    # Original NETS columns (preserved)
    "duns_id",
    "company_name",
    "street_address",
    "city",
    "state",
    "zip_code",
    "phone",
    "website",
    "latitude",
    "longitude",
    "naics_code",
    
    # Geographic enrichment
    "census_tract",
    "census_block_group",
    "coordinate_source",  # 'original_nets', 'geocoded', 'clustered'
    "geocode_quality",    # 'high', 'medium', 'low'
    
    # Employee estimation
    "employees_optimized",
    "employees_ci_lower",
    "employees_ci_upper",
    "employees_estimation_method",  # 'linkedin', 'review_intensity', 'building_area'
    "employees_confidence",         # 'high', 'medium', 'low'
    "employee_data_sources",        # JSON list of contributing sources
    
    # Business survival indicators
    "is_active_prob",               # 0.0-1.0 probability
    "is_active_confidence",         # 'high', 'medium', 'low'
    "last_review_date",
    "days_since_last_review",
    "review_decay_rate",
    "hiring_activity_recent",
    "street_view_visible",
    
    # Data quality metrics
    "data_quality_score",           # 0-100 composite
    "data_completeness",            # Percentage of fields populated
    "signal_count",                 # Number of data sources used
    
    # Metadata
    "collection_date",
    "data_sources_used",            # JSON: ['outscraper', 'linkedin', 'osm', etc.]
    "notes"
]

# ==========================================
# APPLICATION CONFIGURATION
# ==========================================
TARGET_CITY = "Minneapolis"
TARGET_STATE = "Minnesota"
DEFAULT_STATE_CODE = "MN"
DEFAULT_OUTPUT_DIR = "data/processed"
DEFAULT_PARQUET_OUTPUT = "data/processed/nets_ai_minneapolis.parquet"

# Data source priorities
DATA_SOURCE_PRIORITY = [
    "nets_database",
    "outscraper_reviews",
    "linkedin_headcount",
    "indeed_postings",
    "openstreetmap",
    "google_street_view"
]

# Error handling and logging
LOG_LEVEL = "INFO"
VALIDATION_ON_EXPORT = True
BACKUP_PARQUET = True

# Performance settings
BATCH_SIZE_DASK = 100  # Use Dask for >1000 records
GEOCODING_TIMEOUT_SEC = 10
API_RATE_LIMIT_DELAY_SEC = 1
