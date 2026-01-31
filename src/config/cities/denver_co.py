"""
Denver, CO city configuration.
Template for multi-city expansion.
"""

DENVER_CONFIG = {
    # Geographic boundaries (EPSG:4326 WGS84)
    "CITY_NAME": "Denver",
    "STATE_CODE": "CO",
    "STATE_FIPS": "08",
    "COUNTY_FIPS": "031",  # Denver County
    
    # Bounding box: (min_lon, min_lat, max_lon, max_lat)
    "GEOGRAPHIC_BOUNDS": (-105.1098, 39.6143, -104.5996, 39.9142),
    
    # Target ZIP codes for Denver proper
    "TARGET_ZIP_CODES": [
        "80202", "80203", "80204", "80205", "80206",
        "80207", "80209", "80210", "80211", "80212",
        "80214", "80216", "80218", "80219", "80220",
        "80222", "80223", "80224", "80230", "80231",
        "80237", "80238", "80239", "80246", "80247",
        "80249", "80264", "80290", "80293", "80294"
    ],
    
    # Target NAICS codes (same as Minneapolis)
    "NAICS_TARGETS": ["722513", "446110"],
    
    # Industry-specific baselines (adjust for Denver market)
    "INDUSTRY_BASELINES": {
        "722513": {  # Limited-Service Restaurants (Fast Food)
            "avg_employees": 11,
            "employees_per_sqm": 0.024,
            "avg_reviews_per_month": 14.0,
            "typical_hours": "6:00 AM - 11:00 PM",
        },
        "446110": {  # Pharmacies
            "avg_employees": 7,
            "employees_per_sqm": 0.014,
            "avg_reviews_per_month": 4.5,
            "typical_hours": "8:00 AM - 9:00 PM",
        }
    },
    
    # Census tract prefix for Denver
    "CENSUS_TRACT_PREFIX": "08031",
    
    # Data source paths (relative to data/)
    "NETS_INPUT_PATH": "raw/nets_denver.csv",
    "OUTPUT_PATH": "processed/nets_enhanced_denver.parquet",
}
