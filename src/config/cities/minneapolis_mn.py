"""
Minneapolis, MN city configuration.
Primary implementation city for NETS Enhancement System.
"""

MINNEAPOLIS_CONFIG = {
    # Geographic boundaries (EPSG:4326 WGS84)
    "CITY_NAME": "Minneapolis",
    "STATE_CODE": "MN",
    "STATE_FIPS": "27",
    "COUNTY_FIPS": "053",  # Hennepin County
    
    # Bounding box: (min_lon, min_lat, max_lon, max_lat)
    "GEOGRAPHIC_BOUNDS": (-93.3293, 44.8896, -93.1936, 45.0512),
    
    # Target ZIP codes for Minneapolis proper
    "TARGET_ZIP_CODES": [
        "55401", "55402", "55403", "55404", "55405",
        "55406", "55407", "55408", "55409", "55410",
        "55411", "55412", "55413", "55414", "55415"
    ],
    
    # Target NAICS codes
    "NAICS_TARGETS": ["722513", "446110"],
    
    # Industry-specific baselines
    "INDUSTRY_BASELINES": {
        "722513": {  # Limited-Service Restaurants (Fast Food)
            "avg_employees": 12,
            "employees_per_sqm": 0.025,
            "avg_reviews_per_month": 15.0,
            "typical_hours": "6:00 AM - 11:00 PM",
        },
        "446110": {  # Pharmacies
            "avg_employees": 8,
            "employees_per_sqm": 0.015,
            "avg_reviews_per_month": 5.0,
            "typical_hours": "8:00 AM - 9:00 PM",
        }
    },
    
    # Census tract prefix for Minneapolis
    "CENSUS_TRACT_PREFIX": "27053",
    
    # Data source paths (relative to data/)
    "NETS_INPUT_PATH": "raw/nets_minneapolis.csv",
    "OUTPUT_PATH": "processed/nets_enhanced_minneapolis.parquet",
}
