import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import *
from src.agents.google_maps_agent import GoogleMapsAgent


def validate_task(task_name):
    """Validate that the task exists in configuration"""
    if task_name not in CATEGORY_CONFIG:
        available = ", ".join(CATEGORY_CONFIG.keys())
        raise ValueError(f"Task '{task_name}' not found. Available: {available}")
    return task_name


def validate_env():
    """Check required environment variables"""
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        missing.append("GOOGLE_MAPS_API_KEY")
    
    if missing:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")


def process_place(place, details, config, client, today_str):
    """Process a single place and extract AI analysis"""
    
    name = details.get('name', 'Unknown')
    geometry = details.get('geometry', {}).get('location', {})
    lat = geometry.get('lat')
    lng = geometry.get('lng')
    addr = details.get('formatted_address', '')
    
    # Extract attributes
    attrs_list = []
    if details.get('serves_breakfast'): 
        attrs_list.append("Breakfast")
    if details.get('serves_lunch'): 
        attrs_list.append("Lunch")
    if details.get('serves_dinner'): 
        attrs_list.append("Dinner")
    if details.get('serves_beer'): 
        attrs_list.append("Beer")
    if details.get('serves_wine'): 
        attrs_list.append("Wine")
    attr_str = ", ".join(attrs_list) if attrs_list else "None"

    # Operating hours
    opening_hours_data = details.get('opening_hours', {}).get('weekday_text', [])
    operating_hours = "; ".join(opening_hours_data) if opening_hours_data else "Unknown"
    
    price_level = details.get('price_level', 'N/A')

    # Reviews processing
    reviews_list = details.get('reviews', [])
    review_count = len(reviews_list)
    reviews_text = ""
    last_review_date = "N/A"
    has_reviews = False

    if reviews_list:
        has_reviews = True
        timestamps = [r.get('time', 0) for r in reviews_list]
        if timestamps:
            last_review_date = datetime.fromtimestamp(max(timestamps)).strftime('%Y-%m-%d')
        texts = [f"- {r.get('text')[:200]}..." for r in reviews_list[:3] if r.get('text')]
        reviews_text = "\n".join(texts)
    else:
        reviews_text = "NO REVIEWS. Judge based on Name, Hours, and Attributes only."

    # AI Analysis
    system_instruction = f"""
You are a data researcher. Today is {today_str}.
TASK: Decide the NAICS code for '{name}'.
Target: {config['search_term']} (NAICS {config['target_naics']}).
Definition: {config['definition']}

LOGIC (Use FACTS):
1. **Hours**: Opens 6-8 AM -> Likely Coffee/Bakery. Opens 4 PM -> Likely Bar.
2. **Attributes**: Breakfast -> Coffee. Dinner+Beer+No Breakfast -> Bar.
3. **Reviews**: Confirm "Vibe".
"""

    user_prompt = f"""
Name: {name}
FACTS: Hours: {operating_hours} | Attrs: {attr_str} | Price: {price_level}
REVIEWS: {reviews_text}

Return JSON:
{{
    "Calculated_NAICS": "6-digit code",
    "Employees": "Integer or null",
    "Year_Established": "Integer or null",
    "Status": "Active/Inactive",
    "Confidence": "High/Low",
    "Reasoning": "Brief explanation."
}}
"""

    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=AI_TEMPERATURE
        )
        
        ai_data = json.loads(
            response.choices[0].message.content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        
        return {
            "Company": name,
            "Calculated_NAICS": ai_data.get("Calculated_NAICS"),
            "Target_NAICS": config['target_naics'],
            "Is_Target_Match": (ai_data.get("Calculated_NAICS") == config['target_naics']),
            "Confidence": ai_data.get("Confidence"),
            "Match_Reasoning": ai_data.get("Reasoning"),
            "Business_Status": ai_data.get("Status"),
            "Review_Count": review_count,
            "Has_Reviews": "Yes" if has_reviews else "No",
            "Latitude": lat,
            "Longitude": lng,
            "Street_Address": addr,
            "City": TARGET_CITY_NAME,
            "State": DEFAULT_STATE,
            "Zip_Code": place.get('_source_zip'),
            "Operating_Hours": operating_hours,
            "Hard_Attributes": attr_str,
            "Price_Level": price_level,
            "Business_Website": details.get('website'),
            "Employees_Estimated": ai_data.get("Employees"),
            "Year_Established": ai_data.get("Year_Established"),
            "Last_Review_Date": last_review_date
        }
        
    except json.JSONDecodeError as e:
        print(f"    [Warning] Failed to parse AI response: {e}")
        return None
    except Exception as e:
        print(f"    [Error] {e}")
        return None


def main():
    # ========== ARGUMENT PARSING ==========
    parser = argparse.ArgumentParser(
        description="AI-BDD: Collect business data using Google Maps + OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python code/main.py --task coffee
  python code/main.py --task gym --city Minneapolis
  python code/main.py --list
        """
    )
    
    parser.add_argument(
        "--task", 
        type=str, 
        default=DEFAULT_TASK,
        help=f"Business category to collect (default: {DEFAULT_TASK})"
    )
    
    parser.add_argument(
        "--city",
        type=str,
        default=TARGET_CITY_NAME,
        help=f"Target city (default: {TARGET_CITY_NAME})"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available business categories"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # ========== LIST MODE ==========
    if args.list:
        print("\nAvailable Business Categories:")
        print("-" * 50)
        for task_name, task_config in CATEGORY_CONFIG.items():
            print(f"  {task_name:<12} -> {task_config['search_term']}")
            print(f"  {'':12}    NAICS: {task_config['target_naics']}")
        print()
        return 0
    
    # ========== VALIDATION ==========
    try:
        load_dotenv()
        validate_env()
        validate_task(args.task)
    except (EnvironmentError, ValueError) as e:
        print(f"Error: {e}")
        return 1
    
    # ========== INITIALIZATION ==========
    print(f"Starting Data Collection: [{args.task}] in {args.city}")
    print(f"Using {len(TARGET_ZIP_CODES)} zip codes to bypass Google limits\n")
    
    config = CATEGORY_CONFIG[args.task]
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    maps_agent = GoogleMapsAgent()
    
    # ========== STEP 1: SEARCH PHASE ==========
    all_raw_places = {}
    
    for zip_code in TARGET_ZIP_CODES:
        query = f"{config['search_term']} in {args.city} {zip_code}"
        if args.verbose:
            print(f"Searching: {query}")
        
        results = maps_agent.search_places(query)
        print(f"   Found {len(results)} places in {zip_code}")
        
        # Deduplicate
        for place in results:
            pid = place['place_id']
            if pid not in all_raw_places:
                place['_source_zip'] = zip_code
                all_raw_places[pid] = place
    
    unique_places = list(all_raw_places.values())
    print(f"\nTotal Unique Places: {len(unique_places)}")
    
    if not unique_places:
        print("No places found. Check your API key and network connection.")
        return 1
    
    # ========== STEP 2: ANALYSIS PHASE ==========
    print(f"Starting AI analysis ({len(unique_places)} places)...\n")
    
    processed_data = []
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    for idx, place in enumerate(unique_places, 1):
        try:
            place_name = place.get('name', 'Unknown')
            print(f"[{idx}/{len(unique_places)}] {place_name}...", end=" ", flush=True)
            
            details = maps_agent.get_place_details(place['place_id'])
            row = process_place(place, details, config, client, today_str)
            
            if row:
                processed_data.append(row)
                status = "MATCH" if row['Is_Target_Match'] else "NO_MATCH"
                print(f"{status}")
            else:
                print("NO_DATA")
                
        except Exception as e:
            print(f"ERROR ({str(e)[:30]})")
            continue
    
    # ========== STEP 3: SAVE PHASE ==========
    if not processed_data:
        print("\n❌ No data to save!")
        return 1
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{args.city}_{args.task}_{timestamp}.csv"
    output_dir = os.path.join(os.path.dirname(__file__), DEFAULT_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    df = pd.DataFrame(processed_data)
    df = df.reindex(columns=FINAL_COLUMNS)
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Complete!")
    print(f"   Records: {len(df)}")
    print(f"   Matched: {df['Is_Target_Match'].sum()}")
    print(f"   File: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
