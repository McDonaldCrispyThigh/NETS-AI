import os
import sys
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from skills.google_maps import GoogleMapsAgent

# ==========================================
# 1. ZIP CODE STRATEGY (To break the 60 limit)
# ==========================================
# Minneapolis Zip Codes (You can add more)
TARGET_ZIP_CODES = [
    "55401", "55402", "55403", "55404", "55405", 
    "55406", "55407", "55408", "55409", "55410", 
    "55411", "55412", "55413", "55414", "55415",
    "55454", "55455"
]

# ==========================================
# 2. FIXED CSV STRUCTURE
# ==========================================
FINAL_COLUMNS = [
    "Company", "Calculated_NAICS", "Target_NAICS", "Is_Target_Match", "Confidence", 
    "Match_Reasoning", "Business_Status", "Review_Count", "Has_Reviews",
    "Latitude", "Longitude", "Street_Address", "City", "State", "Zip_Code",
    "Operating_Hours", "Hard_Attributes", "Price_Level", "Business_Website", 
    "Employees_Estimated", "Year_Established", "Last_Review_Date"
]

# ==========================================
# 3. FULL CONFIGURATION
# ==========================================
CATEGORY_CONFIG = {
    # --- 1. Libraries ---
    "library": {
        "search_term": "Public Library",
        "target_naics": "519120",
        "sic_code": "8231",
        "definition": "Facility that lends books and provides quiet study areas. Key signs: 'Librarian', 'Checkout', 'Computers'. Non-commercial."
    },
    # --- 2. Parks ---
    "park": {
        "search_term": "Park",
        "target_naics": "712190", 
        "sic_code": "7999",
        "definition": "Designated outdoor area for nature and recreation. Key signs: 'Trail', 'Playground', 'Grass'. Distinct from 'Mobile Home Park' (Residential)."
    },
    # --- 3. Coffee Shops ---
    "coffee": {
        "search_term": "Coffee Shop",
        "target_naics": "722515",
        "sic_code": "5812",
        # Logic: Morning Hours + Breakfast > Alcohol
        "definition": "Focuses on coffee/tea and light food. Key signs: Opens early (6-8 AM), serves breakfast. If it opens early, it is a Coffee Shop even if it has beer."
    },
    # --- 4. Gyms ---
    "gym": {
        "search_term": "Gym",
        "target_naics": "713940",
        "sic_code": "7991",
        "definition": "Facility for physical exercise. Key signs: 'Weights', 'Treadmills', 'Membership', 'Classes'. Distinct from 'Playground equipment store'."
    },
    # --- 5. Grocery Stores ---
    "grocery": {
        "search_term": "Grocery Store",
        "target_naics": "445110",
        "sic_code": "5411",
        "definition": "Retail store primarily selling fresh food, produce, and meats. Distinct from 'Convenience Store' (Gas stations) or 'Liquor Store'."
    },
    # --- 6. Civic & Social Orgs ---
    "civic": {
        "search_term": "Community Center",
        "target_naics": "813410",
        "sic_code": "8641",
        "definition": "Non-profit facility for social interaction and community support. Key signs: 'Volunteers', 'Community Events', 'Hall Rental'."
    },
    # --- 7. Religious Orgs ---
    "religion": {
        "search_term": "Place of Worship",
        "target_naics": "813110",
        "sic_code": "8661",
        "definition": "Facility for religious services. Key signs: 'Service', 'Prayer', 'Worship', 'Church/Mosque/Synagogue'."
    }
}

CURRENT_TASK = "coffee"  
TARGET_CITY_NAME = "Minneapolis" # Just the name, we append zip

# ==========================================
# 4. MAIN PROGRAM
# ==========================================
def main():
    load_dotenv()
    print(f">>> Starting Scientific Data Collection: [{CURRENT_TASK}] using ZIP CODES...")

    if CURRENT_TASK not in CATEGORY_CONFIG:
        print(f"Error: Task '{CURRENT_TASK}' not found.")
        return
    
    config = CATEGORY_CONFIG[CURRENT_TASK]
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    maps_agent = GoogleMapsAgent()
    
    # --- STEP 1: MASSIVE SEARCH (Loop through Zips) ---
    all_raw_places = {} # Use dict to remove duplicates automatically (Key = place_id)
    
    print(f">>> Strategy: Scanning {len(TARGET_ZIP_CODES)} Zip Codes to bypass Google limits.")
    
    for zip_code in TARGET_ZIP_CODES:
        query = f"{config['search_term']} in {TARGET_CITY_NAME} {zip_code}"
        print(f"\n--- Searching Zip: {zip_code} ---")
        
        # search_places now handles the 3-page limit per query robustly
        results = maps_agent.search_places(query)
        
        print(f"    Found {len(results)} places in {zip_code}.")
        
        # Add to dictionary (De-duplication)
        for place in results:
            pid = place['place_id']
            if pid not in all_raw_places:
                place['_source_zip'] = zip_code # Track where we found it
                all_raw_places[pid] = place

    unique_places = list(all_raw_places.values())
    print(f"\n>>> TOTAL UNIQUE PLACES FOUND: {len(unique_places)}")
    print(">>> Starting AI Analysis & Fact Extraction...")
    
    processed_data = []
    today_str = datetime.now().strftime('%Y-%m-%d')

    # --- STEP 2: PROCESS EACH UNIQUE PLACE ---
    for i, place in enumerate(unique_places): 
        try:
            # Progress bar
            print(f"[{i+1}/{len(unique_places)}] Fetching details for: {place.get('name')}")
            details = maps_agent.get_place_details(place['place_id'])
        except Exception:
            continue

        name = details.get('name')
        
        # Facts extraction
        geometry = details.get('geometry', {}).get('location', {})
        lat = geometry.get('lat', None)
        lng = geometry.get('lng', None)
        
        # Extract Zip from address if possible, or use source zip
        addr = details.get('formatted_address', '')
        
        attrs_list = []
        if details.get('serves_breakfast'): attrs_list.append("Breakfast")
        if details.get('serves_lunch'): attrs_list.append("Lunch")
        if details.get('serves_dinner'): attrs_list.append("Dinner")
        if details.get('serves_beer'): attrs_list.append("Beer")
        if details.get('serves_wine'): attrs_list.append("Wine")
        attr_str = ", ".join(attrs_list) if attrs_list else "None"

        opening_hours_data = details.get('opening_hours', {}).get('weekday_text', [])
        operating_hours = "; ".join(opening_hours_data) if opening_hours_data else "Unknown"
        price_level = details.get('price_level', 'N/A')

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

        # AI Prompt
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
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            ai_data = json.loads(response.choices[0].message.content.replace("```json", "").replace("```", "").strip())
            
            row = {
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
                "State": "MN",
                "Zip_Code": place.get('_source_zip'),
                "Operating_Hours": operating_hours,
                "Hard_Attributes": attr_str,
                "Price_Level": price_level,
                "Business_Website": details.get('website'),
                "Employees_Estimated": ai_data.get("Employees"),
                "Year_Established": ai_data.get("Year_Established"),
                "Last_Review_Date": last_review_date
            }
            processed_data.append(row)
            
        except Exception as e:
            print(f"    [Error] {e}")

    # --- SAVE ---
    if processed_data:
        # Get current time like "20231027_1530"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Add timestamp to filename so it never conflicts with open Excel files
        filename = f"Minneapolis_{CURRENT_TASK}_{timestamp}.csv"
        output_path = os.path.join(os.path.dirname(__file__), f'../data/{filename}')
        
        df = pd.DataFrame(processed_data)
        df = df.reindex(columns=FINAL_COLUMNS)
        
        df.to_csv(output_path, index=False)
        print(f">>> Success! Saved to {filename}")
        print(f">>> Total Unique Records: {len(df)}")

if __name__ == "__main__":
    main()