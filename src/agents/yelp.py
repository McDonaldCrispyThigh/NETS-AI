import requests
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("YELP_API_KEY")

class YelpAgent:
    def __init__(self):
        if not API_KEY:
            print("Warning: YELP_API_KEY is missing in .env")
            self.headers = None
        else:
            self.headers = {'Authorization': f'Bearer {API_KEY}'}
        self.base_url = "https://api.yelp.com/v3/businesses"

    def search_businesses(self, term, location=None, latitude=None, longitude=None, limit=50, offset=0, radius=2000):
        """
        Search Yelp for businesses.
        
        Args:
            term (str): Search term
            location (str): Location text (optional)
            latitude (float): Latitude (optional)
            longitude (float): Longitude (optional)
            limit (int): Max results per call (<=50)
            offset (int): Pagination offset
            radius (int): Search radius in meters (<=40000)
        """
        if not self.headers:
            return []

        url = f"{self.base_url}/search"
        params = {
            'term': term,
            'limit': min(limit, 50),
            'offset': offset,
            'radius': min(radius, 40000)
        }
        if location:
            params['location'] = location
        if latitude and longitude:
            params['latitude'] = latitude
            params['longitude'] = longitude

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('businesses', [])
            else:
                print(f"Yelp Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"Error calling Yelp: {e}")
            return []

    def get_business_details(self, yelp_id):
        """
        Get detailed info (categories, hours, etc.)
        """
        if not self.headers:
            return {}

        url = f"{self.base_url}/{yelp_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"Error getting details: {e}")
            return {}

    def get_reviews(self, yelp_id):
        """
        Get Yelp reviews (Yelp API returns up to 3 reviews).
        """
        if not self.headers:
            return []

        url = f"{self.base_url}/{yelp_id}/reviews"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get('reviews', [])
            return []
        except Exception as e:
            print(f"Error getting reviews: {e}")
            return []

# Test
if __name__ == "__main__":
    agent = YelpAgent()
    results = agent.search_businesses("Starbucks", "Boulder, CO")
    print(f"Found {len(results)} shops on Yelp.")