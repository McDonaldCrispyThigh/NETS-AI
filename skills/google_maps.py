import googlemaps
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class GoogleMapsAgent:
    def __init__(self):
        if not API_KEY:
            print("Warning: Missing GOOGLE_MAPS_API_KEY in .env")
            self.client = None
        else:
            self.client = googlemaps.Client(key=API_KEY)

    def search_places(self, query): 
        """
        Robust Search that fights for every page.
        Automatically handles pagination up to the API limit (60 results).
        """
        if not self.client:
            return []
        
        all_results = []
        next_token = None
        
        # We try to fetch up to 3 pages (Google's Limit per query)
        for page_num in range(3): 
            try:
                response = None
                
                # --- RETRY LOGIC FOR TOKEN ---
                # If we have a token, we must wait until it is valid.
                if next_token:
                    attempts = 0
                    while attempts < 3:
                        print(f"    ... Fetching Page {page_num + 1} (Attempt {attempts+1})...")
                        time.sleep(2 + attempts) # Wait 2s, then 3s, then 4s...
                        try:
                            response = self.client.places(query=query, page_token=next_token)
                            if response['status'] == 'OK':
                                break # Success!
                            else:
                                print(f"    [Google Status: {response['status']}] Retrying...")
                        except Exception as e:
                            print(f"    [Error] {e}. Retrying...")
                        
                        attempts += 1
                else:
                    # First page (No token needed)
                    response = self.client.places(query=query)
                
                # --- PROCESS RESULTS ---
                if response and response.get('status') == 'OK':
                    results = response['results']
                    all_results.extend(results)
                    
                    # Check for next page
                    next_token = response.get('next_page_token')
                    if not next_token:
                        print("    ... No more pages for this specific query.")
                        break
                else:
                    print("    ... Failed to get valid response.")
                    break
            
            except Exception as e:
                print(f"Search Critical Error: {e}")
                break
                
        return all_results

    def get_place_details(self, place_id):
        # ... (Keep existing logic) ...
        if not self.client:
            return {}
        try:
            result = self.client.place(
                place_id=place_id, 
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number', 
                    'type', 'business_status', 'price_level',
                    'geometry', 'website', 'opening_hours',
                    'reviews',
                    'serves_beer', 'serves_wine', 'serves_breakfast', 
                    'serves_lunch', 'serves_dinner' 
                ]
            )
            return result.get('result', {})
        except Exception as e:
            return {}