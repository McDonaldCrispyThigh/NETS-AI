import os
import sys
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Make sure Python can find the 'skills' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skills.google_maps import GoogleMapsAgent

def main():
    # 1. Start the program
    load_dotenv()
    print(">>> Starting the AI Agent (Review Mode)...")

    # Check if we have the OpenAI Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is missing in .env file")
        return
    
    # Connect to OpenAI and Google Maps
    client = OpenAI(api_key=api_key)
    maps_agent = GoogleMapsAgent()
    
    # 2. Set the search target
    target_city = "Minneapolis, MN"
    target_category = "Coffee Shop"
    query = f"{target_category} in {target_city}"
    
    print(f">>> Step 1: Searching Google Maps for '{query}'...")
    
    # Get the list of places from Google Maps
    raw_results = maps_agent.search_places(query)
    print(f">>> Found {len(raw_results)} places. Now checking reviews...")
    
    processed_data = []
    
    # 3. Process each place one by one
    # We only check the first 5 places to save money during tests
    for place in raw_results[:5]: 
        details = maps_agent.get_place_details(place['place_id'])
        name = details.get('name')
        
        print(f"    -> Checking: {name}...")

        # --- A. Get the reviews ---
        reviews_list = details.get('reviews', [])
        reviews_text = ""
        last_review_date = "Unknown"
        
        if reviews_list:
            # 1. Find the date of the newest review
            timestamps = [r.get('time', 0) for r in reviews_list]
            if timestamps:
                latest_ts = max(timestamps)
                # Convert the time to a readable format (YYYY-MM-DD)
                last_review_date = datetime.fromtimestamp(latest_ts).strftime('%Y-%m-%d')
            
            # 2. Combine reviews into one text for the AI
            # We only use the first 3 reviews to keep it short
            texts = [f"- {r.get('text')[:200]}..." for r in reviews_list[:3] if r.get('text')]
            reviews_text = "\n".join(texts)
        else:
            reviews_text = "No reviews available."

        # --- B. Create the instructions for the AI ---
        system_instruction = """
        You are a data assistant for a university thesis.
        
        YOUR TASK: Use the customer reviews to answer two questions:
        1. **Is the business still open?** (Check the date of the last review).
        2. **What kind of business is it?** (Check what people are eating or drinking).
           - If they talk about "latte" or "coffee", it is a Coffee Shop (722515).
           - If they talk about "bread", it might be a Bakery (311811).
           - If they talk about "cocktails", it might be a Bar (722410).
        """

        user_prompt = f"""
        Business Info:
        - Name: {name}
        - Address: {details.get('formatted_address')}
        - Google Types: {", ".join(details.get('types', []))}
        
        REVIEW EVIDENCE:
        Date of Last Review: {last_review_date}
        What people said:
        {reviews_text}
        
        Please fill in this JSON:
        {{
            "NAICS": "The 6-digit NAICS code (based on reviews)",
            "SIC": "The 4-digit SIC code",
            "BusinessStatus": "Active or Inactive (Is the last review recent?)",
            "YearEstablished": "Year (integer) or null",
            "Employees": "Estimated number of employees (integer) or null",
            "Reasoning": "One simple sentence explaining why you chose this NAICS code"
        }}
        """

        try:
            # Ask the AI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0
            )
            
            # Read the AI's answer
            ai_content = response.choices[0].message.content
            # Clean the answer
            ai_content = ai_content.replace("```json", "").replace("```", "").strip()
            ai_data = json.loads(ai_content)
            
            # Save the data
            row = {
                "Company": name,
                "City": "Minneapolis",
                "Last_Review_Date": last_review_date,
                "AI_Predicted_Status": ai_data.get("BusinessStatus"),
                "NAICS": ai_data.get("NAICS"),
                "Reasoning": ai_data.get("Reasoning"),
                "Employees": ai_data.get("Employees")
            }
            processed_data.append(row)
            
        except Exception as e:
            print(f"    [Error] Could not process {name}: {e}")

    # 4. Save the results to a file
    if processed_data:
        # Create the 'data' folder if it does not exist
        os.makedirs(os.path.join(os.path.dirname(__file__), '../data'), exist_ok=True)
        output_path = os.path.join(os.path.dirname(__file__), '../data/Minneapolis_Coffee_Reviews.csv')
        
        df = pd.DataFrame(processed_data)
        df.to_csv(output_path, index=False)
        
        print(f">>> Success! The data is saved in {output_path}")
        # Show a preview of the reasoning
        print(df[['Company', 'Last_Review_Date', 'Reasoning']].head())
    else:
        print(">>> No data found.")

if __name__ == "__main__":
    main()