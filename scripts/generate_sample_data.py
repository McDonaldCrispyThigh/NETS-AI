"""
Generate realistic sample NETS data for Minneapolis
For testing and demonstration purposes
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Sample business names
QSR_NAMES = [
    "McDonald's", "Subway", "Chipotle Mexican Grill", "Taco Bell", "Panera Bread",
    "Starbucks", "Arby's", "Chick-fil-A", "Popeyes", "In-N-Out Burger",
    "Five Guys", "Shake Shack", "Burger King", "Wendy's", "Panda Express",
    "Thai Express", "Pho King", "Ramen House", "Taco John's", "Jimmy John's",
    "Jersey Mike's Subs", "Firehouse Subs", "Local Café", "Quick Noodle", "Falafel King",
    "Buffalo Wild Wings", "Applebee's Bar & Grill", "Olive Garden", "Outback Steakhouse",
    "Texas Roadhouse", "The Cheesecake Factory", "California Pizza Kitchen"
]

PHARMACY_NAMES = [
    "CVS Pharmacy", "Walgreens", "Target Pharmacy", "Costco Pharmacy",
    "Rite Aid", "Duane Reade", "Kroger Pharmacy", "Safeway Pharmacy",
    "Independent Pharmacy #1", "Independent Pharmacy #2", "Community Pharmacy",
    "Health & Wellness Pharmacy", "24-Hour Pharmacy", "Express Pharmacy",
    "Medical Center Pharmacy", "University Pharmacy", "Downtown Pharmacy",
    "Northside Pharmacy", "Southside Pharmacy", "Eastside Pharmacy", "Westside Pharmacy"
]

def generate_sample_nets_data(num_qsr: int = 150, num_pharmacy: int = 80) -> pd.DataFrame:
    """
    Generate realistic NETS sample data
    
    Args:
        num_qsr: Number of quick service restaurants
        num_pharmacy: Number of pharmacies
        
    Returns:
        DataFrame with NETS-like structure
    """
    logger.info(f"Generating sample data: {num_qsr} QSR + {num_pharmacy} Pharmacies")
    
    records = []
    duns_counter = 1000000
    
    # Quick Service Restaurants (NAICS 722513)
    for i in range(num_qsr):
        lat = np.random.uniform(MINNEAPOLIS_BOUNDS['lat_min'], MINNEAPOLIS_BOUNDS['lat_max'])
        lon = np.random.uniform(MINNEAPOLIS_BOUNDS['lon_min'], MINNEAPOLIS_BOUNDS['lon_max'])
        
        # Assign to nearest ZIP code (simplified)
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
            'website': f"https://www.{np.random.choice(QSR_NAMES).lower().replace(' ', '')}.com",
            'year_established': np.random.randint(2000, 2023),
            'year_closed': None if np.random.random() > 0.1 else np.random.randint(2020, 2026),
            'employee_count_raw': np.random.randint(4, 50) if np.random.random() > 0.3 else None,
            'sic_code': '5812',  # Eating places
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
            'sic_code': '5912',  # Drug stores
        })
    
    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} total records")
    return df


def generate_enrichment_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add enrichment columns to simulate external data
    
    Args:
        df: Base NETS data
        
    Returns:
        DataFrame with enriched columns
    """
    logger.info("Generating enrichment features...")
    
    # LinkedIn employee counts (some missing)
    df['linkedin_employee_count'] = df.apply(
        lambda x: np.random.randint(x['employee_count_raw'] - 3, x['employee_count_raw'] + 5)
        if pd.notna(x['employee_count_raw']) and np.random.random() > 0.5
        else None,
        axis=1
    )
    
    # Review data
    base_date = datetime.now()
    df['review_count_3m'] = np.random.randint(0, 30)
    df['review_count_6_12m'] = df['review_count_3m'] + np.random.randint(0, 40)
    df['last_review_date'] = df.apply(
        lambda x: (base_date - timedelta(days=np.random.randint(1, 90))).strftime('%Y-%m-%d')
        if np.random.random() > 0.15
        else None,
        axis=1
    )
    
    # Job postings (for growth signal)
    df['job_postings_6m'] = np.random.randint(0, 8)
    df['job_postings_peak'] = df['job_postings_6m'].apply(
        lambda x: max(1, x + np.random.randint(-2, 3))
    )
    
    # Building area estimation
    df['estimated_area_sqm'] = df['naics_code'].apply(
        lambda x: np.random.randint(400, 600) if x == '722513' else np.random.randint(500, 700)
    )
    
    # Street view indicators
    df['street_view_active'] = np.random.choice([True, False], size=len(df), p=[0.7, 0.3])
    df['signage_visible'] = np.random.choice([True, False], size=len(df), p=[0.8, 0.2])
    
    logger.info("Enrichment data generated successfully")
    return df


def main():
    """Main function"""
    # Generate data
    df = generate_sample_nets_data(num_qsr=150, num_pharmacy=80)
    df = generate_enrichment_data(df)
    
    # Save to CSV
    output_path = Path("data/raw/nets_minneapolis_sample.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Sample data saved to {output_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("SAMPLE NETS DATA GENERATION SUMMARY")
    print("="*70)
    print(f"Total Records: {len(df)}")
    print(f"\nBy Industry:")
    print(df['naics_code'].value_counts())
    print(f"\nBy ZIP Code (sample):")
    print(df['zip_code'].value_counts().head(10))
    print(f"\nData Completeness:")
    print(f"  Employee counts: {(df['employee_count_raw'].notna().sum() / len(df) * 100):.1f}%")
    print(f"  LinkedIn data: {(df['linkedin_employee_count'].notna().sum() / len(df) * 100):.1f}%")
    print(f"  Review data: {(df['last_review_date'].notna().sum() / len(df) * 100):.1f}%")
    print(f"  Active businesses: {((df['year_closed'].isna()).sum() / len(df) * 100):.1f}%")
    print("="*70 + "\n")
    
    return df


if __name__ == "__main__":
    main()
