import googlemaps
import os
import time
import math
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

    def geocode_location(self, location_text):
        """
        Geocode a location string to latitude/longitude.

        Args:
            location_text (str): e.g., "55401 Minneapolis MN"

        Returns:
            dict: {"lat": float, "lng": float} or None
        """
        if not self.client:
            return None
        try:
            results = self.client.geocode(location_text)
            if not results:
                return None
            loc = results[0].get('geometry', {}).get('location')
            if not loc:
                return None
            return {"lat": loc.get('lat'), "lng": loc.get('lng')}
        except Exception:
            return None

    def _meters_to_degrees(self, meters, latitude):
        """
        Convert meters to degrees latitude/longitude at a given latitude.
        """
        lat_deg = meters / 111320.0
        lng_deg = meters / (111320.0 * math.cos(math.radians(latitude))) if latitude else 0
        return lat_deg, lng_deg

    def generate_grid_points(self, center_lat, center_lng, radius_m, spacing_m):
        """
        Generate grid points around a center within a radius.

        Args:
            center_lat (float): Center latitude
            center_lng (float): Center longitude
            radius_m (int): Radius in meters
            spacing_m (int): Grid spacing in meters

        Returns:
            list: List of (lat, lng) tuples
        """
        lat_step, lng_step = self._meters_to_degrees(spacing_m, center_lat)
        lat_radius, lng_radius = self._meters_to_degrees(radius_m, center_lat)

        points = []
        lat = center_lat - lat_radius
        while lat <= center_lat + lat_radius:
            lng = center_lng - lng_radius
            while lng <= center_lng + lng_radius:
                points.append((lat, lng))
                lng += lng_step
            lat += lat_step
        return points

    def search_places_grid(self, keyword, center_lat, center_lng, radius_m=800, spacing_m=800):
        """
        Grid-based search using Places Nearby to avoid 60-result cap.

        Args:
            keyword (str): Search keyword (e.g., "coffee shop")
            center_lat (float): Center latitude
            center_lng (float): Center longitude
            radius_m (int): Nearby search radius
            spacing_m (int): Grid spacing between query points

        Returns:
            list: Deduplicated place results
        """
        if not self.client:
            return []

        all_results = {}
        grid_points = self.generate_grid_points(center_lat, center_lng, radius_m, spacing_m)

        for idx, (lat, lng) in enumerate(grid_points, 1):
            next_token = None
            for page_num in range(3):
                try:
                    response = None
                    if next_token:
                        attempts = 0
                        while attempts < 5:
                            time.sleep(2 + attempts)
                            response = self.client.places_nearby(
                                location=(lat, lng),
                                radius=radius_m,
                                keyword=keyword,
                                page_token=next_token
                            )
                            if response.get('status') == 'OK':
                                break
                            attempts += 1
                    else:
                        response = self.client.places_nearby(
                            location=(lat, lng),
                            radius=radius_m,
                            keyword=keyword
                        )

                    if response and response.get('status') == 'OK':
                        results = response.get('results', [])
                        for place in results:
                            pid = place.get('place_id')
                            if pid:
                                all_results[pid] = place

                        next_token = response.get('next_page_token')
                        if not next_token:
                            break
                    else:
                        break
                except Exception:
                    break

        return list(all_results.values())

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
                    'reviews', 'rating', 'user_ratings_total', 'url',
                    'serves_beer', 'serves_wine', 'serves_breakfast', 
                    'serves_lunch', 'serves_dinner' 
                ]
            )
            return result.get('result', {})
        except Exception as e:
            return {}