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
        
        # We try to fetch up to 5 pages (Google's Limit per query)
        for page_num in range(5): 
            try:
                response = None
                
                # --- RETRY LOGIC FOR TOKEN ---
                # If we have a token, we must wait until it is valid.
                if next_token:
                    attempts = 0
                    while attempts < 5:
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

    def search_nearby(self, lat: float, lon: float,
                      keyword: str = "Pharmacy", radius: int = 1500) -> list:
        """
        Location-biased Text Search centered on (lat, lon).

        Uses places() (Text Search) with location+radius so Google ranks results
        by proximity to the given point. Different center points return different
        top-60 results -- this is the mechanism for exceeding the per-query cap.
        """
        if not self.client:
            return []

        all_results = []
        next_token = None
        _places = getattr(self.client, "places")  # type: ignore[attr-defined]

        for page_num in range(5):
            try:
                response = None
                if next_token:
                    attempts = 0
                    while attempts < 5:
                        print(f"    ... Grid page {page_num + 1} (attempt {attempts + 1})...")
                        time.sleep(2 + attempts)
                        try:
                            response = _places(
                                query=keyword,
                                location=(lat, lon),
                                radius=radius,
                                page_token=next_token,
                            )
                            if response["status"] == "OK":
                                break
                        except Exception as e:
                            print(f"    [Error] {e}. Retrying...")
                        attempts += 1
                else:
                    response = _places(
                        query=keyword,
                        location=(lat, lon),
                        radius=radius,
                    )

                if response and response.get("status") in ("OK", "ZERO_RESULTS"):
                    all_results.extend(response.get("results", []))
                    next_token = response.get("next_page_token")
                    if not next_token:
                        break
                else:
                    break
            except Exception as e:
                print(f"Grid search error: {e}")
                break

        return all_results

    def get_place_details(self, place_id):
        if not self.client:
            return {}
        try:
            # reviews_sort="newest" ensures the 5 returned reviews are the
            # 5 most recent, making Last_Review_Date the actual latest date.
            # Google Places API hard-caps at 5 reviews regardless of sort order.
            result = self.client.place(
                place_id=place_id,
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number',
                    'type', 'business_status', 'price_level',
                    'geometry', 'website', 'opening_hours',
                    'reviews',
                    'serves_beer', 'serves_wine', 'serves_breakfast',
                    'serves_lunch', 'serves_dinner'
                ],
                reviews_sort="newest",
            )
            return result.get('result', {})
        except Exception as e:
            return {}