"""
NETS Data Path Reference - NO SAMPLE DATA GENERATION
This file documents where to place your real NETS CSV files for pipeline processing
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# REAL DATA FILE PATHS - Place Your NETS CSV Files Here
# =============================================================================

# Production NETS data path
NETS_PRODUCTION_PATH = Path("data/raw/nets_minneapolis_full.csv")

# Test data path (smaller subset for testing)
NETS_TEST_PATH = Path("tests/fixtures/nets_test_data.csv")


# =============================================================================
# REQUIRED CSV SCHEMA FOR NETS DATA
# =============================================================================

REQUIRED_COLUMNS = {
    # Core identifiers
    'duns_id': 'str - Unique DUNS business identifier',
    'company_name': 'str - Business name',
    
    # Industry classification
    'naics_code': 'str - 6-digit NAICS code (e.g., "722513" for QSR)',
    'naics_title': 'str - NAICS description',
    'sic_code': 'str - SIC code (optional)',
    
    # Location information
    'latitude': 'float - GPS latitude (e.g., 44.9778)',
    'longitude': 'float - GPS longitude (e.g., -93.2650)',
    'street_address': 'str - Street address',
    'city': 'str - City name',
    'state': 'str - 2-letter state code (e.g., "MN")',
    'zip_code': 'str - 5-digit ZIP code',
    
    # Contact information
    'phone': 'str - Phone number (optional)',
    'website': 'str - Website URL (optional)',
    
    # Temporal data
    'year_established': 'int - Year business established (optional)',
    'year_closed': 'int - Year business closed, null if active (optional)',
    
    # Employee data
    'employee_count_raw': 'int - Raw employee count from NETS (optional)',
}

OPTIONAL_ENRICHMENT_COLUMNS = {
    # External enrichment data (if available)
    'linkedin_employee_count': 'int - Employee count from LinkedIn',
    'review_count_3m': 'int - Recent review count (last 3 months)',
    'review_count_6_12m': 'int - Historical review count (6-12 months ago)',
    'last_review_date': 'str - Date of last review (YYYY-MM-DD)',
    'job_postings_6m': 'int - Job postings in last 6 months',
    'job_postings_peak': 'int - Peak job posting count',
    'estimated_area_sqm': 'float - Building area in square meters',
    'street_view_active': 'bool - Street view indicators available',
    'signage_visible': 'bool - Business signage visible in imagery',
}


def print_data_requirements():
    """Print required data schema and file paths"""
    print("=" * 80)
    print("NETS DATA FILE REQUIREMENTS")
    print("=" * 80)
    
    print("\n[PRODUCTION DATA PATH]")
    print(f"  Location: {NETS_PRODUCTION_PATH}")
    print(f"  Purpose: Full dataset for real processing")
    print(f"  Expected size: Thousands of records")
    
    print("\n[TEST DATA PATH]")
    print(f"  Location: {NETS_TEST_PATH}")
    print(f"  Purpose: Small subset for testing (5-20 records recommended)")
    print(f"  Expected size: < 50 KB")
    
    print("\n[REQUIRED COLUMNS]")
    for col, desc in REQUIRED_COLUMNS.items():
        print(f"  - {col:25s} : {desc}")
    
    print("\n[OPTIONAL ENRICHMENT COLUMNS]")
    for col, desc in OPTIONAL_ENRICHMENT_COLUMNS.items():
        print(f"  - {col:25s} : {desc}")
    
    print("\n[TARGET NAICS CODES]")
    print("  - 722513 : Limited-Service Restaurants (Quick Service Restaurants)")
    print("  - 446110 : Pharmacies")
    
    print("\n[MINNEAPOLIS ZIP CODES] (for geographic filtering)")
    zips = ["55401", "55402", "55403", "55404", "55405", "55406", "55407", 
            "55408", "55409", "55410", "55411", "55412", "55413", "55414", "55415"]
    print(f"  {', '.join(zips)}")
    
    print("\n" + "=" * 80)
    print("USAGE INSTRUCTIONS")
    print("=" * 80)
    
    print("\n[FOR TESTING]")
    print("  1. Create a small CSV file at:")
    print(f"     {NETS_TEST_PATH}")
    print("  2. Include 5-20 sample records with required columns")
    print("  3. Run: python scripts/run_pipeline.py --test")
    
    print("\n[FOR PRODUCTION]")
    print("  1. Place your full NETS CSV file at:")
    print(f"     {NETS_PRODUCTION_PATH}")
    print("  2. Ensure all required columns are present")
    print("  3. Run: python scripts/run_pipeline.py --input data/raw/nets_minneapolis_full.csv")
    
    print("\n[ALTERNATIVE INPUT]")
    print("  You can also specify any CSV path:")
    print("  python scripts/run_pipeline.py --input /path/to/your/nets_data.csv")
    
    print("\n" + "=" * 80)


def check_data_files():
    """Check if data files exist"""
    print("\n[DATA FILE STATUS]")
    
    if NETS_PRODUCTION_PATH.exists():
        size_mb = NETS_PRODUCTION_PATH.stat().st_size / 1024 / 1024
        print(f"  [OK] Production data found: {NETS_PRODUCTION_PATH} ({size_mb:.2f} MB)")
    else:
        print(f"  [!] Production data NOT found: {NETS_PRODUCTION_PATH}")
        print(f"      Place your NETS CSV file here when ready")
    
    if NETS_TEST_PATH.exists():
        size_kb = NETS_TEST_PATH.stat().st_size / 1024
        print(f"  [OK] Test data found: {NETS_TEST_PATH} ({size_kb:.2f} KB)")
    else:
        print(f"  [!] Test data NOT found: {NETS_TEST_PATH}")
        print(f"      Create a small test CSV here for testing")
    
    print()


if __name__ == "__main__":
    print_data_requirements()
    check_data_files()


# Minneapolis geographic bounds (approximate)
MINNEAPOLIS_BOUNDS = {
 'lat_min': 44.8899,
 'lat_max': 45.0428,
 'lon_min': -93.3223,
 'lon_max': -93.1833
}

TARGET_ZIP_CODES = [
 "55401", "55402", "55403", "55404", "55405",
 "55406", "55407", "55408", "55409", "55410",
 "55411", "55412", "55413", "55414", "55415"
]

QSR_NAMES = [
 "McDonald's", "Subway", "Chipotle Mexican Grill", "Taco Bell", "Panera Bread",
 "Starbucks", "Arby's", "Chick-fil-A", "Popeyes", "In-N-Out Burger",
 "Five Guys", "Shake Shack", "Burger King", "Wendy's", "Panda Express"
]

PHARMACY_NAMES = [
 "CVS Pharmacy", "Walgreens", "Target Pharmacy", "Costco Pharmacy",
 "Rite Aid", "Duane Reade", "Kroger Pharmacy", "Safeway Pharmacy"
]

def generate_test_fixture_data(num_qsr: int = 5, num_pharmacy: int = 3) -> pd.DataFrame:
    """
    Generate minimal test fixture data for unit testing
    
    Args:
        num_qsr: Number of quick service restaurants (default: 5 for testing)
        num_pharmacy: Number of pharmacies (default: 3 for testing)
    
    Returns:
        DataFrame with NETS-like structure
    """
    logger.info(f"Generating test fixture data: {num_qsr} QSR + {num_pharmacy} Pharmacies")
    
    records = []
    duns_counter = 1000000
    
    # Quick Service Restaurants (NAICS 722513)
    for i in range(num_qsr):
        lat = np.random.uniform(MINNEAPOLIS_BOUNDS['lat_min'], MINNEAPOLIS_BOUNDS['lat_max'])
        lon = np.random.uniform(MINNEAPOLIS_BOUNDS['lon_min'], MINNEAPOLIS_BOUNDS['lon_max'])
        
        zip_code = np.random.choice(TARGET_ZIP_CODES)
        
        records.append({
            'duns_id': str(duns_counter + i),
            'company_name': np.random.choice(QSR_NAMES),
            'naics_code': '722513',
            'naics_title': 'Limited-Service Restaurants',
            'latitude': lat,
            'longitude': lon,
            'zip_code': zip_code,
            'street_address': f"{np.random.randint(1, 10000)} Main St",
            'city': 'Minneapolis',
            'state': 'MN',
            'phone': f"({np.random.randint(200, 999)})-{np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}",
            'website': None,
            'year_established': np.random.randint(2000, 2023),
            'year_closed': None if np.random.random() > 0.1 else np.random.randint(2020, 2026),
            'employee_count_raw': np.random.randint(4, 50) if np.random.random() > 0.3 else None,
            'sic_code': '5812'
        })
    
    # Pharmacies (NAICS 446110)
    for i in range(num_pharmacy):
        lat = np.random.uniform(MINNEAPOLIS_BOUNDS['lat_min'], MINNEAPOLIS_BOUNDS['lat_max'])
        lon = np.random.uniform(MINNEAPOLIS_BOUNDS['lon_min'], MINNEAPOLIS_BOUNDS['lon_max'])
        
        zip_code = np.random.choice(TARGET_ZIP_CODES)
        
        records.append({
            'duns_id': str(duns_counter + num_qsr + i),
            'company_name': np.random.choice(PHARMACY_NAMES),
            'naics_code': '446110',
            'naics_title': 'Pharmacies',
            'latitude': lat,
            'longitude': lon,
            'zip_code': zip_code,
            'street_address': f"{np.random.randint(1, 10000)} Medical Ave",
            'city': 'Minneapolis',
            'state': 'MN',
            'phone': f"({np.random.randint(200, 999)})-{np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}",
            'website': None,
            'year_established': np.random.randint(1995, 2023),
            'year_closed': None if np.random.random() > 0.08 else np.random.randint(2021, 2026),
            'employee_count_raw': np.random.randint(3, 35) if np.random.random() > 0.4 else None,
            'sic_code': '5912'
        })
    
    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} total records")
    return df


def generate_enrichment_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add optional enrichment columns to simulate external data
    
    Args:
        df: Base NETS data
    
    Returns:
        DataFrame with enriched columns
    """
    logger.info("Adding enrichment features...")
    
    # LinkedIn employee counts (some missing)
    df['linkedin_employee_count'] = df.apply(
        lambda x: np.random.randint(max(1, x['employee_count_raw'] - 3), x['employee_count_raw'] + 5)
        if pd.notna(x['employee_count_raw']) and np.random.random() > 0.5
        else None,
        axis=1
    )
    
    # Review data
    base_date = datetime.now()
    df['review_count_3m'] = np.random.randint(0, 15)
    df['review_count_6_12m'] = df['review_count_3m'] + np.random.randint(0, 20)
    df['last_review_date'] = df.apply(
        lambda x: (base_date - timedelta(days=np.random.randint(1, 90))).strftime('%Y-%m-%d')
        if np.random.random() > 0.15
        else None,
        axis=1
    )
    
    # Job postings
    df['job_postings_6m'] = np.random.randint(0, 5)
    df['job_postings_peak'] = df['job_postings_6m'].apply(
        lambda x: max(1, x + np.random.randint(-1, 2))
    )
    
    # Building area
    df['estimated_area_sqm'] = df['naics_code'].apply(
        lambda x: np.random.randint(400, 600) if x == '722513' else np.random.randint(500, 700)
    )
    
    # Street view indicators
    df['street_view_active'] = np.random.choice([True, False], size=len(df), p=[0.7, 0.3])
    df['signage_visible'] = np.random.choice([True, False], size=len(df), p=[0.8, 0.2])
    
    logger.info("Enrichment features added successfully")
    return df


def main():
    """Main function to generate test fixture data"""
    # Create test fixtures directory if it doesn't exist
    test_dir = Path("tests/fixtures")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    df = generate_test_fixture_data(num_qsr=5, num_pharmacy=3)
    df = generate_enrichment_data(df)
    
    # Save to fixtures directory
    output_path = test_dir / "nets_test_fixture_small.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Test fixture saved to {output_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST FIXTURE GENERATION SUMMARY")
    print("="*70)
    print(f"Total Records: {len(df)}")
    print(f"\nBy Industry:")
    print(df['naics_code'].value_counts())
    print(f"\nBy ZIP Code (sample):")
    print(df['zip_code'].value_counts().head(5))
    print(f"\nData Completeness:")
    print(f" Employee counts: {(df['employee_count_raw'].notna().sum() / len(df) * 100):.1f}%")
    print(f" LinkedIn data: {(df['linkedin_employee_count'].notna().sum() / len(df) * 100):.1f}%")
    print(f" Review data: {(df['last_review_date'].notna().sum() / len(df) * 100):.1f}%")
    print(f" Active businesses: {((df['year_closed'].isna()).sum() / len(df) * 100):.1f}%")
    print("="*70 + "\n")
    
    return df


if __name__ == "__main__":
    main()
