"""
Outscraper Agent - Enhanced Google Maps Data Collection

Due to API versioning complexity, this agent wraps Google Maps API
with enhanced data collection strategy to gather complete business information.

Future: When Outscraper API stabilizes, can be swapped for direct Outscraper
client calls for price savings (97% cheaper than Google Maps API).
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class OutscraperAgent:
 """
 Outscraper-compatible agent for enhanced Google Maps data collection.
 
 Strategy for complete data collection:
 1. Use Google Maps Places API for initial search
 2. Query each place individually for complete details
 3. Aggregate reviews from all available pages
 4. Collect business hours, ratings, phone, website, address
 
 Future enhancement: Replace with actual Outscraper API client
 when library API versioning issues are resolved.
 """
 
 def __init__(self):
 self.api_key = os.getenv("OUTSCRAPER_API_KEY")
 self.client = None
 self._fallback_maps = None

 # Initialize Outscraper client if API key is available
 if self.api_key:
 try:
 from outscraper import OutscraperClient
 self.client = OutscraperClient(api_key=self.api_key)
 except Exception:
 try:
 from outscraper import ApiClient
 self.client = ApiClient(api_key=self.api_key)
 except Exception:
 self.client = None

 # Initialize Google Maps agent for data collection
 try:
 from src.agents.google_maps_agent import GoogleMapsAgent
 self._fallback_maps = GoogleMapsAgent()
 except Exception as e:
 print(f"Warning: Could not initialize Google Maps agent: {e}")
 
 def search_places(self, query: str, limit: int = 20) -> List[Dict]:
 """
 Search Google Maps for places matching query.
 
 Args:
 query: Search query (e.g., "coffee shops in Minneapolis, MN")
 limit: Maximum number of results
 
 Returns:
 List of place dictionaries with complete business information
 """
 if not self._fallback_maps:
 return []
 
 # Use Google Maps search as primary method
 return self._fallback_maps.search_places(query, limit=limit)
 
 def get_place_details(self, place_id: str) -> Dict:
 """
 Get detailed place information by place_id.

 If Outscraper is configured, use google_maps_reviews to fetch reviews
 and business details in one call. Fallback to Google Maps API otherwise.
 """
 if self.client:
 details = self._get_place_details_from_outscraper(place_id)
 if details:
 return details

 if not self._fallback_maps:
 return {}

 return self._fallback_maps.get_place_details(place_id)

 def get_place_reviews(self, query: str, reviews_limit: int = 0, limit: int = 500,
 language: str = 'en', sort: str = 'most_relevant',
 cutoff: Optional[int] = None) -> List[Dict]:
 """
 Get Google Maps reviews via Outscraper.

 Args:
 query: place_id, google_id, or search query
 reviews_limit: number of reviews per place (0 = unlimited)
 limit: number of places for query searches
 language: review language
 sort: most_relevant|newest|highest_rating|lowest_rating
 cutoff: unix timestamp for oldest review (used with sort=newest)

 Returns:
 List of Outscraper review results
 """
 if not self.client:
 return []

 try:
 return self.client.google_maps_reviews(
 query=query,
 reviews_limit=reviews_limit,
 limit=limit,
 language=language,
 sort=sort,
 cutoff=cutoff
 )
 except Exception as e:
 print(f"Outscraper reviews error: {e}")
 return []
 
 def get_place_reviews_timeseries(self, place_id: str = None, query: str = None,
 language: str = 'en', reviews_limit: int = 0) -> List[Dict]:
 """
 Fetch full Google Maps reviews with timestamps and text for time series analysis.
 
 Returns sorted list (oldest to newest) with:
 - review_timestamp: Unix timestamp
 - review_datetime_utc: ISO datetime string
 - review_text: Full review text
 - review_rating: 1-5 stars
 - review_likes: Number of likes
 
 Use cases:
 1. Analyze NAICS code changes over time (via review text)
 2. Determine opening/closing dates (first/last review)
 3. Calculate employee count via review density (reviews/month)
 
 Args:
 place_id: Google place_id (preferred)
 query: Search query as fallback
 language: Review language (default: 'en')
 reviews_limit: Max reviews (0 = unlimited)
 """
 if not self.client:
 return []
 
 if not place_id and not query:
 return []
 
 target = place_id or query
 
 try:
 data = self.client.google_maps_reviews(
 query=target,
 reviews_limit=reviews_limit,
 language=language,
 sort='newest' # Sort by newest to get full timeline
 )
 except Exception as e:
 print(f"Outscraper timeseries error: {e}")
 return []
 
 # Extract reviews_data from Outscraper response
 reviews_data = []
 if isinstance(data, list) and len(data) > 0:
 item = data[0]
 if isinstance(item, dict):
 reviews_data = item.get('reviews_data', [])
 elif isinstance(data, dict):
 reviews_data = data.get('reviews_data', [])
 
 # Convert to timeseries format
 timeseries = []
 for r in reviews_data:
 ts = r.get('review_timestamp')
 if not ts:
 continue
 
 timeseries.append({
 'review_timestamp': int(ts),
 'review_datetime_utc': datetime.utcfromtimestamp(ts).isoformat() if ts else None,
 'review_text': r.get('review_text', ''),
 'review_rating': r.get('review_rating'),
 'review_likes': r.get('review_likes', 0)
 })
 
 # Sort by timestamp (oldest to newest)
 timeseries.sort(key=lambda x: x['review_timestamp'])
 
 return timeseries
 
 def extract_review_statistics(self, reviews_timeseries: List[Dict]) -> Dict:
 """
 Extract statistical features from review timeseries.
 
 Returns:
 - oldest_review_date: ISO date of first review (establishment proxy)
 - latest_review_date: ISO date of last review (closure detection)
 - total_reviews: Total review count
 - reviews_per_month: Average monthly review rate
 - review_timestamps: List of all timestamps for further analysis
 """
 if not reviews_timeseries:
 return {
 'oldest_review_date': None,
 'latest_review_date': None,
 'total_reviews': 0,
 'reviews_per_month': 0.0,
 'review_timestamps': []
 }
 
 timestamps = [r['review_timestamp'] for r in reviews_timeseries if r.get('review_timestamp')]
 
 if not timestamps:
 return {
 'oldest_review_date': None,
 'latest_review_date': None,
 'total_reviews': len(reviews_timeseries),
 'reviews_per_month': 0.0,
 'review_timestamps': []
 }
 
 oldest_ts = min(timestamps)
 latest_ts = max(timestamps)
 
 # Calculate reviews per month
 time_span_months = max(1, (latest_ts - oldest_ts) / (30.44 * 24 * 3600)) # 30.44 days avg month
 reviews_per_month = len(timestamps) / time_span_months
 
 return {
 'oldest_review_date': datetime.utcfromtimestamp(oldest_ts).date().isoformat(),
 'latest_review_date': datetime.utcfromtimestamp(latest_ts).date().isoformat(),
 'total_reviews': len(timestamps),
 'reviews_per_month': round(reviews_per_month, 2),
 'review_timestamps': timestamps
 }

 def _get_place_details_from_outscraper(self, place_id: str) -> Dict:
 """
 Fetch place details using Outscraper reviews endpoint.
 """
 try:
 results = self.client.google_maps_reviews(
 query=place_id,
 reviews_limit=0,
 limit=1,
 language='en'
 )
 except Exception as e:
 print(f"Outscraper details error: {e}")
 return {}

 if not results:
 return {}

 item = results[0] if isinstance(results, list) else results
 if not isinstance(item, dict):
 return {}

 return self._map_outscraper_place(item)

 def _map_outscraper_place(self, item: Dict) -> Dict:
 """
 Map Outscraper place response to GoogleMapsAgent-compatible fields.
 """
 reviews = []
 reviews_data = item.get('reviews_data', [])
 for r in reviews_data:
 timestamp = r.get('review_timestamp') or 0
 reviews.append({
 'author_name': r.get('autor_name') or r.get('author_name', ''),
 'rating': r.get('review_rating', 0),
 'text': r.get('review_text', ''),
 'time': int(timestamp) if timestamp else 0
 })

 working_hours = item.get('working_hours')
 weekday_text = []
 if isinstance(working_hours, str):
 weekday_text = [t.strip() for t in working_hours.split('|') if t.strip()]
 elif isinstance(working_hours, dict):
 for day, hours in working_hours.items():
 if hours:
 weekday_text.append(f"{day}: {hours}")

 return {
 'name': item.get('name'),
 'place_id': item.get('place_id') or item.get('google_id'),
 'formatted_address': item.get('address'),
 'formatted_phone_number': item.get('phone'),
 'website': item.get('site'),
 'url': item.get('reviews_link'),
 'rating': item.get('rating'),
 'user_ratings_total': item.get('reviews', 0),
 'price_level': None,
 'reviews': reviews,
 'opening_hours': {
 'weekday_text': weekday_text,
 'open_now': None
 },
 'geometry': {
 'location': {
 'lat': item.get('latitude'),
 'lng': item.get('longitude')
 }
 },
 'types': [],
 }
 
 def geocode_location(self, location_text: str) -> Optional[Dict]:
 """
 Geocode a location string to latitude/longitude.
 """
 if self._fallback_maps:
 return self._fallback_maps.geocode_location(location_text)
 return None
 
 def search_places_grid(self, keyword: str, center_lat: float, center_lng: float,
 radius_m: int = 800, spacing_m: int = 800) -> List[Dict]:
 """
 Grid-based search around a center point.
 """
 if self._fallback_maps:
 return self._fallback_maps.search_places_grid(
 keyword=keyword,
 center_lat=center_lat,
 center_lng=center_lng,
 radius_m=radius_m,
 spacing_m=spacing_m
 )
 return []
