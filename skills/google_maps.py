import googlemaps
import os
from dotenv import load_dotenv

# Load the API Key from the .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class GoogleMapsAgent:
    def __init__(self):
        # Check if the key exists
        if not API_KEY:
            print("Warning: GOOGLE_MAPS_API_KEY is missing in .env")
            self.client = None
        else:
            self.client = googlemaps.Client(key=API_KEY)

    def search_places(self, query, location=None):
        """
        Search for a place on Google Maps.
        """
        if not self.client:
            return []
        
        try:
            # Use the Places API to search
            results = self.client.places(query=query)
            if results['status'] == 'OK':
                return results['results']
            else:
                return []
        except Exception as e:
            print(f"Error searching Google Maps: {e}")
            return []

    def get_place_details(self, place_id):
        """
        Get details about a specific place (like address, phone, type).
        """
        if not self.client:
            return {}

        try:
            # FIX: Changed 'types' to 'type' in the fields list
            # The API is strict: request 'type' (singular), get back 'types' (plural)
            result = self.client.place(
                place_id=place_id, 
                fields=['name', 'formatted_address', 'formatted_phone_number', 'type', 'permanently_closed', 'reviews']
            )
            return result.get('result', {})
        except Exception as e:
            print(f"Error getting details: {e}")
            return {}

# Test code
if __name__ == "__main__":
    agent = GoogleMapsAgent()
    print(agent.search_places("Coffee shops in Boulder, CO"))