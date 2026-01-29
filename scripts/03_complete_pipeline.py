"""
AI-BDD Complete Data Collection Pipeline
Integrates: Google Maps + Wayback Machine + GPT Analysis
"""

import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import *
from src.agents.google_maps_agent import GoogleMapsAgent
from src.agents.wayback_agent import WaybackAgent
from src.agents.gpt_analyzer import GPTAnalyzer
from src.agents.yelp import YelpAgent
from src.data.sos_loader import SOSLoader
from src.data.external_signals import ExternalSignalsLoader
from src.models.employee_estimator import EmployeeEstimator
from src.utils.logger import setup_logger
from src.utils.helpers import (
    check_website_status,
    is_recent_activity,
    calculate_confidence_score,
    calculate_api_cost,
    normalize_name,
    calculate_review_velocity
)

# Setup logger
logger = setup_logger("AI-BDD-Pipeline")


def validate_env():
    """Check required environment variables"""
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        missing.append("GOOGLE_MAPS_API_KEY")
    
    if missing:
        raise EnvironmentError(f"Missing: {', '.join(missing)}")


def haversine_km(lat1, lon1, lat2, lon2):
    """Compute great-circle distance in kilometers."""
    import math
    if None in (lat1, lon1, lat2, lon2):
        return None
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_best_yelp_match(yelp_results, name, latitude, longitude):
    """Find best Yelp match by name similarity and distance."""
    if not yelp_results:
        return None
    target = normalize_name(name)
    best = None
    best_score = 0
    for item in yelp_results:
        y_name = normalize_name(item.get('name'))
        if not y_name:
            continue
        name_score = 1.0 if y_name == target else 0.0
        dist_km = None
        coords = item.get('coordinates', {})
        if coords and latitude and longitude:
            dist_km = haversine_km(latitude, longitude, coords.get('latitude'), coords.get('longitude'))
        dist_score = 1.0 if dist_km is not None and dist_km <= 0.5 else 0.0
        score = name_score * 0.7 + dist_score * 0.3
        if score > best_score:
            best = item
            best_score = score
    return best


def collect_business_data(place_id: str, maps_agent: GoogleMapsAgent) -> dict:
    """Collect comprehensive data from Google Maps"""
    details = maps_agent.get_place_details(place_id)
    
    # Basic info
    data = {
        'name': details.get('name', 'Unknown'),
        'place_id': place_id,
        'address': details.get('formatted_address', ''),
        'phone': details.get('formatted_phone_number', ''),
        'website': details.get('website', ''),
        'google_url': details.get('url', ''),
    }
    
    # Location
    geometry = details.get('geometry', {}).get('location', {})
    data['latitude'] = geometry.get('lat')
    data['longitude'] = geometry.get('lng')
    
    # Rating and reviews
    data['google_rating'] = details.get('rating')
    data['google_reviews_total'] = details.get('user_ratings_total', 0)
    data['price_level'] = details.get('price_level')
    
    # Reviews
    reviews = details.get('reviews', [])
    data['google_reviews_returned'] = len(reviews)
    
    if reviews:
        timestamps = [r.get('time', 0) for r in reviews if r.get('time')]
        if timestamps:
            data['last_review_date'] = datetime.fromtimestamp(max(timestamps)).strftime('%Y-%m-%d')
            data['oldest_review_date'] = datetime.fromtimestamp(min(timestamps)).strftime('%Y-%m-%d')
        
        # Extract review snippets (limited by API)
        data['review_snippets'] = " ... ".join([
            r.get('text', '')[:100] for r in reviews[:5] if r.get('text')
        ])
    else:
        data['last_review_date'] = None
        data['oldest_review_date'] = None
        data['review_snippets'] = ''
    
    # Hours
    hours = details.get('opening_hours', {})
    data['operating_hours'] = "; ".join(hours.get('weekday_text', []))
    data['is_open_now'] = hours.get('open_now', None)
    
    # Attributes
    attrs = []
    if details.get('serves_breakfast'): attrs.append('Breakfast')
    if details.get('serves_lunch'): attrs.append('Lunch')
    if details.get('serves_dinner'): attrs.append('Dinner')
    if details.get('serves_beer'): attrs.append('Beer')
    if details.get('serves_wine'): attrs.append('Wine')
    if details.get('takeout'): attrs.append('Takeout')
    if details.get('delivery'): attrs.append('Delivery')
    if details.get('dine_in'): attrs.append('Dine-in')
    data['attributes'] = ", ".join(attrs) if attrs else "None"
    
    # Business types
    data['google_types'] = ", ".join(details.get('types', []))
    
    return data


def enhance_with_wayback(business_data: dict, wayback_agent: WaybackAgent) -> dict:
    """Add Wayback Machine validation data"""
    website = business_data.get('website')
    
    if not website:
        business_data['wayback_first_snapshot'] = None
        business_data['wayback_last_snapshot'] = None
        business_data['wayback_snapshot_count'] = 0
        return business_data
    
    logger.info(f"  Checking Wayback for: {website}")
    
    # Get first snapshot (establishment date validation)
    first = wayback_agent.get_first_snapshot(website)
    if first:
        business_data['wayback_first_snapshot'] = first['date'].strftime('%Y-%m-%d')
        business_data['wayback_first_year'] = first['year']
    else:
        business_data['wayback_first_snapshot'] = None
        business_data['wayback_first_year'] = None
    
    # Get last snapshot (closure detection)
    last = wayback_agent.get_last_snapshot(website)
    if last:
        business_data['wayback_last_snapshot'] = last['date'].strftime('%Y-%m-%d')
        business_data['wayback_last_year'] = last['year']
    else:
        business_data['wayback_last_snapshot'] = None
        business_data['wayback_last_year'] = None
    
    # Snapshot count (activity indicator)
    count = wayback_agent.get_snapshot_count(website)
    business_data['wayback_snapshot_count'] = count
    
    return business_data


def enhance_with_gpt(business_data: dict, gpt_analyzer: GPTAnalyzer, config: dict) -> dict:
    """Add GPT-4o-mini analysis"""
    logger.info(f"  Running GPT analysis...")
    
    # Classify business status
    status_result = gpt_analyzer.classify_business_status(business_data)
    business_data['ai_status'] = status_result.get('status')
    business_data['ai_status_confidence'] = status_result.get('confidence')
    business_data['ai_status_reasoning'] = status_result.get('reasoning')
    business_data['ai_risk_factors'] = ", ".join(status_result.get('risk_factors', []))
    
    # Estimate employment
    employment_result = gpt_analyzer.estimate_employment({
        **business_data,
        'category': config.get('search_term')
    })
    business_data['ai_employees_min'] = employment_result.get('min_employees')
    business_data['ai_employees_max'] = employment_result.get('max_employees')
    business_data['ai_employees_estimate'] = employment_result.get('best_estimate')
    business_data['ai_employees_confidence'] = employment_result.get('confidence')
    
    # Verify NAICS
    naics_result = gpt_analyzer.verify_naics_classification(
        business_data,
        config['target_naics'],
        config['definition']
    )
    business_data['ai_naics_match'] = naics_result.get('is_match')
    business_data['ai_naics_suggested'] = naics_result.get('actual_naics_suggestion')
    business_data['ai_naics_confidence'] = naics_result.get('confidence')
    business_data['ai_naics_reasoning'] = naics_result.get('reasoning')
    
    return business_data


def calculate_overall_confidence(business_data: dict) -> str:
    """Calculate overall data confidence score"""
    last_review_date = business_data.get('last_review_date')
    yelp_last_review = business_data.get('yelp_last_review_date')
    if yelp_last_review and (not last_review_date or yelp_last_review > last_review_date):
        last_review_date = yelp_last_review

    review_count_total = max(
        business_data.get('google_reviews_total', 0) or 0,
        business_data.get('yelp_review_count', 0) or 0
    )
    indicators = {
        'has_recent_reviews': is_recent_activity(last_review_date or '', 180),
        'review_count': review_count_total,
        'website_accessible': business_data.get('website_status_code') == 200,
        'has_hours': bool(business_data.get('operating_hours')),
        'wayback_verified': business_data.get('wayback_snapshot_count', 0) > 0
    }
    
    return calculate_confidence_score(indicators)


def main():
    # ========== ARGUMENT PARSING ==========
    parser = argparse.ArgumentParser(
        description="AI-BDD Complete Pipeline: Google Maps + Wayback + GPT Analysis"
    )
    
    parser.add_argument("--task", type=str, default=DEFAULT_TASK,
                       help=f"Business category (default: {DEFAULT_TASK})")
    parser.add_argument("--city", type=str, default=TARGET_CITY_NAME,
                       help=f"Target city (default: {TARGET_CITY_NAME})")
    parser.add_argument("--list", action="store_true",
                       help="List available categories")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit number of businesses to process")
    parser.add_argument("--skip-wayback", action="store_true",
                       help="Skip Wayback Machine validation (faster)")
    parser.add_argument("--skip-gpt", action="store_true",
                       help="Skip GPT analysis (saves API cost)")
    parser.add_argument("--disable-grid-search", action="store_true",
                       help="Disable grid-based Google Maps search")
    parser.add_argument("--grid-radius", type=int, default=GRID_SEARCH_RADIUS_M,
                       help="Grid search radius in meters")
    parser.add_argument("--grid-spacing", type=int, default=GRID_SEARCH_SPACING_M,
                       help="Grid spacing in meters")
    parser.add_argument("--sos-registry", type=str, default=SOS_REGISTRY_PATH,
                       help="Path to SOS registry CSV")
    parser.add_argument("--external-signals", type=str, default=EXTERNAL_SIGNALS_PATH,
                       help="Path to external signals CSV")
    
    args = parser.parse_args()
    
    # ========== LIST MODE ==========
    if args.list:
        print("\nAvailable Business Categories:")
        print("-" * 60)
        for task, cfg in CATEGORY_CONFIG.items():
            print(f"  {task:<12} -> {cfg['search_term']:<25} NAICS: {cfg['target_naics']}")
        print()
        return 0
    
    # ========== VALIDATION ==========
    try:
        load_dotenv()
        validate_env()
        if args.task not in CATEGORY_CONFIG:
            raise ValueError(f"Invalid task: {args.task}")
    except Exception as e:
        logger.error(f"{e}")
        return 1
    
    # ========== INITIALIZATION ==========
    config = CATEGORY_CONFIG[args.task]
    logger.info(f"AI-BDD Pipeline: {args.task} in {args.city}")
    logger.info(f"Target NAICS: {config['target_naics']}")
    
    # Initialize agents
    maps_agent = GoogleMapsAgent()
    wayback_agent = WaybackAgent() if not args.skip_wayback else None
    gpt_analyzer = GPTAnalyzer(model=AI_MODEL, temperature=AI_TEMPERATURE) if not args.skip_gpt else None
    yelp_agent = YelpAgent()

    # Optional external data
    sos_loader = SOSLoader(args.sos_registry)
    external_signals = ExternalSignalsLoader(args.external_signals)
    
    # ========== STEP 1: SEARCH ==========
    logger.info(f"\nStep 1: Searching Google Maps...")
    all_places = {}
    
    for zip_code in TARGET_ZIP_CODES:
        if args.disable_grid_search:
            query = f"{config['search_term']} in {args.city} {zip_code}"
            results = maps_agent.search_places(query)
        else:
            center = maps_agent.geocode_location(f"{zip_code} {args.city} {DEFAULT_STATE}")
            if not center:
                results = []
            else:
                results = maps_agent.search_places_grid(
                    keyword=config['search_term'],
                    center_lat=center['lat'],
                    center_lng=center['lng'],
                    radius_m=args.grid_radius,
                    spacing_m=args.grid_spacing
                )
        logger.info(f"   Zip {zip_code}: {len(results)} places")
        
        for place in results:
            pid = place['place_id']
            if pid not in all_places:
                place['_source_zip'] = zip_code
                all_places[pid] = place
    
    unique_places = list(all_places.values())
    logger.info(f"\nFound {len(unique_places)} unique places")
    
    if args.limit:
        unique_places = unique_places[:args.limit]
        logger.info(f"Limited to {args.limit} places for testing")
    
    # Estimate cost
    costs = calculate_api_cost(len(unique_places), gpt_calls_per_place=3)
    logger.info(f"Estimated API cost: {costs['formatted_total']}")
    
    # ========== STEP 2: COLLECT & ANALYZE ==========
    logger.info(f"\nStep 2: Collecting detailed data...")
    processed_data = []
    
    for idx, place in enumerate(unique_places, 1):
        try:
            name = place.get('name', 'Unknown')
            logger.info(f"[{idx}/{len(unique_places)}] {name}")
            
            # Get Google Maps data
            business_data = collect_business_data(place['place_id'], maps_agent)
            business_data['source_zip'] = place.get('_source_zip')
            business_data['target_naics'] = config['target_naics']
            business_data['category'] = args.task
            
            # Check website accessibility
            if business_data.get('website'):
                website_status = check_website_status(business_data['website'])
                business_data['website_status_code'] = website_status.get('status_code')
                business_data['website_accessible'] = website_status.get('accessible', False)
            else:
                business_data['website_status_code'] = None
                business_data['website_accessible'] = False

            # Yelp enrichment (API-based)
            yelp_match = None
            if yelp_agent and business_data.get('latitude') and business_data.get('longitude'):
                yelp_results = yelp_agent.search_businesses(
                    term=business_data.get('name'),
                    latitude=business_data.get('latitude'),
                    longitude=business_data.get('longitude'),
                    limit=50,
                    radius=2000
                )
                yelp_match = find_best_yelp_match(
                    yelp_results,
                    business_data.get('name'),
                    business_data.get('latitude'),
                    business_data.get('longitude')
                )

            if yelp_match:
                yelp_id = yelp_match.get('id')
                business_data['yelp_id'] = yelp_id
                business_data['yelp_rating'] = yelp_match.get('rating')
                business_data['yelp_review_count'] = yelp_match.get('review_count')
                business_data['yelp_url'] = yelp_match.get('url')
                business_data['yelp_categories'] = ", ".join([c.get('title') for c in yelp_match.get('categories', [])])

                yelp_reviews = yelp_agent.get_reviews(yelp_id) if yelp_id else []
                if yelp_reviews:
                    business_data['yelp_review_snippets'] = " ... ".join([
                        r.get('text', '')[:100] for r in yelp_reviews if r.get('text')
                    ])
                    yelp_dates = [r.get('time_created') for r in yelp_reviews if r.get('time_created')]
                    business_data['yelp_last_review_date'] = max(yelp_dates) if yelp_dates else None
                else:
                    business_data['yelp_review_snippets'] = ''
                    business_data['yelp_last_review_date'] = None
            else:
                business_data['yelp_id'] = None
                business_data['yelp_rating'] = None
                business_data['yelp_review_count'] = None
                business_data['yelp_url'] = None
                business_data['yelp_categories'] = None
                business_data['yelp_review_snippets'] = ''
                business_data['yelp_last_review_date'] = None

            # Review velocity estimation
            business_data['reviews_per_month'] = calculate_review_velocity(
                business_data.get('google_reviews_total', 0),
                business_data.get('oldest_review_date'),
                business_data.get('last_review_date')
            )

            # SOS registry match (optional)
            sos_record = sos_loader.match(
                business_data.get('name', ''),
                business_data.get('address', '')
            ) if sos_loader else None
            if sos_record:
                business_data.update(sos_record)

            # External signals match (optional)
            ext_record = external_signals.match(
                business_data.get('name', ''),
                business_data.get('address', '')
            ) if external_signals else None
            if ext_record:
                business_data.update(ext_record)

            # Employee estimation (multi-signal)
            estimator = EmployeeEstimator(args.task)
            combined = estimator.combine_estimates({
                'linkedin_employee_count': business_data.get('linkedin_employee_count'),
                'job_postings_12m': business_data.get('job_postings_12m'),
                'building_area_m2': business_data.get('building_area_m2'),
                'popular_times_peak': business_data.get('popular_times_peak'),
                'sos_partner_count': business_data.get('sos_partner_count'),
                'reviews_per_month': business_data.get('reviews_per_month')
            })
            business_data['employee_estimate'] = combined.get('employee_estimate')
            business_data['employee_estimate_min'] = combined.get('employee_estimate_min')
            business_data['employee_estimate_max'] = combined.get('employee_estimate_max')
            business_data['employee_estimate_methods'] = ", ".join(combined.get('employee_estimate_methods', []))
            
            # Wayback validation
            if wayback_agent and business_data.get('website'):
                business_data = enhance_with_wayback(business_data, wayback_agent)
            
            # GPT analysis
            if gpt_analyzer:
                business_data = enhance_with_gpt(business_data, gpt_analyzer, config)
            
            # Calculate confidence
            business_data['overall_confidence'] = calculate_overall_confidence(business_data)
            business_data['collection_date'] = datetime.now().strftime('%Y-%m-%d')
            
            processed_data.append(business_data)
            logger.info(f"  Complete (Confidence: {business_data['overall_confidence']})")
            
        except Exception as e:
            logger.error(f"  Error: {str(e)[:100]}")
            continue
    
    # ========== STEP 3: SAVE ==========
    if not processed_data:
        logger.error("\nNo data collected!")
        return 1
    
    logger.info(f"\nStep 3: Saving results...")
    
    # Create DataFrame
    df = pd.DataFrame(processed_data)
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"ai_bdd_{args.city}_{args.task}_{timestamp}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # Summary stats
    logger.info(f"\n" + "="*60)
    logger.info(f"COMPLETE!")
    logger.info(f"="*60)
    logger.info(f"   Total businesses: {len(df)}")
    logger.info(f"   Active (AI): {df['ai_status'].value_counts().get('Active', 0)}")
    logger.info(f"   Inactive (AI): {df['ai_status'].value_counts().get('Inactive', 0)}")
    logger.info(f"   High confidence: {(df['overall_confidence'] == 'High').sum()}")
    logger.info(f"   With website: {df['website'].notna().sum()}")
    logger.info(f"   Wayback verified: {(df['wayback_snapshot_count'] > 0).sum()}")
    logger.info(f"\nOutput: {output_file}")
    logger.info(f"="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
