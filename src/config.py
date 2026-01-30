"""
AI-BDD Configuration Module
Centralized configuration for all data collection tasks
"""

# ==========================================
# MINNEAPOLIS ZIP CODES
# ==========================================
TARGET_ZIP_CODES = [
    "55401", "55402", "55403", "55404", "55405", 
    "55406", "55407", "55408", "55409", "55410", 
    "55411", "55412", "55413", "55414", "55415",
    "55454", "55455"
]

# ==========================================
# BUSINESS CATEGORIES CONFIGURATION
# ==========================================
CATEGORY_CONFIG = {
    "library": {
        "search_term": "Public Library",
        "target_naics": "519120",
        "sic_code": "8231",
        "definition": "Facility that lends books and provides quiet study areas. Key signs: 'Librarian', 'Checkout', 'Computers'. Non-commercial."
    },
    "park": {
        "search_term": "Park",
        "target_naics": "712190", 
        "sic_code": "7999",
        "definition": "Designated outdoor area for nature and recreation. Key signs: 'Trail', 'Playground', 'Grass'. Distinct from 'Mobile Home Park' (Residential)."
    },
    "coffee": {
        "search_term": "Coffee Shop",
        "target_naics": "722515",
        "sic_code": "5812",
        "definition": "Focuses on coffee/tea and light food. Key signs: Opens early (6-8 AM), serves breakfast. If it opens early, it is a Coffee Shop even if it has beer."
    },
    "gym": {
        "search_term": "Gym",
        "target_naics": "713940",
        "sic_code": "7991",
        "definition": "Facility for physical exercise. Key signs: 'Weights', 'Treadmills', 'Membership', 'Classes'. Distinct from 'Playground equipment store'."
    },
    "grocery": {
        "search_term": "Grocery Store",
        "target_naics": "445110",
        "sic_code": "5411",
        "definition": "Retail store primarily selling fresh food, produce, and meats. Distinct from 'Convenience Store' (Gas stations) or 'Liquor Store'."
    },
    "civic": {
        "search_term": "Community Center",
        "target_naics": "813410",
        "sic_code": "8641",
        "definition": "Non-profit facility for social interaction and community support. Key signs: 'Volunteers', 'Community Events', 'Hall Rental'."
    },
    "religion": {
        "search_term": "Place of Worship",
        "target_naics": "813110",
        "sic_code": "8661",
        "definition": "Facility for religious services. Key signs: 'Service', 'Prayer', 'Worship', 'Church/Mosque/Synagogue'."
    }
}

# ==========================================
# OUTPUT COLUMNS
# ==========================================
FINAL_COLUMNS = [
    "Company", "Calculated_NAICS", "Target_NAICS", "Is_Target_Match", "Confidence", 
    "Match_Reasoning", "Business_Status", "Review_Count", "Has_Reviews",
    "Latitude", "Longitude", "Street_Address", "City", "State", "Zip_Code",
    "Operating_Hours", "Hard_Attributes", "Price_Level", "Business_Website", 
    "Employees_Estimated", "Year_Established", "Last_Review_Date"
]

# ==========================================
# APPLICATION DEFAULTS
# ==========================================
TARGET_CITY_NAME = "Minneapolis"
DEFAULT_STATE = "MN"
DEFAULT_TASK = "coffee"
DEFAULT_OUTPUT_DIR = "../data"

# Optional external data sources
SOS_REGISTRY_PATH = "data/external/mn_sos_registry.csv"
EXTERNAL_SIGNALS_PATH = "data/external/external_signals.csv"

# Grid search defaults for Google Maps (meters)
GRID_SEARCH_RADIUS_M = 800
GRID_SEARCH_SPACING_M = 800

# Employee estimation coefficients (employees per square meter)
EMPLOYEE_AREA_COEFFICIENTS = {
    "coffee": 1 / 18.0,
    "gym": 1 / 35.0,
    "library": 1 / 45.0,
    "park": 1 / 500.0,
    "grocery": 1 / 25.0,
    "civic": 1 / 40.0,
    "religion": 1 / 60.0
}

# Service categories for review/popular-times based staffing
SERVICE_CATEGORIES = {
    "coffee", "gym", "grocery", "civic", "religion", "library", "park"
}

# Baseline review velocity (avg reviews/month by category)
REVIEW_VELOCITY_BASELINES = {
    "coffee": 20.0,
    "gym": 8.0,
    "grocery": 12.0,
    "civic": 3.0,
    "religion": 2.0,
    "library": 4.0,
    "park": 2.0
}

# Max customers/hour when popular_times_peak is an index (0-100)
POPULAR_TIMES_MAX_CUSTOMERS_PER_HOUR = {
    "coffee": 120.0,
    "gym": 80.0,
    "grocery": 200.0,
    "civic": 60.0,
    "religion": 150.0,
    "library": 70.0,
    "park": 100.0
}

# Staffing rule: 50 customers/hour requires 4 staff
POPULAR_TIMES_CUSTOMERS_PER_EMPLOYEE = 12.5

# Model settings
AI_MODEL = "gpt-4o-mini"
AI_TEMPERATURE = 0.0
