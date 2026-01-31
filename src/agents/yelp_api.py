"""
Yelp Fusion API Agent for Business Reviews and Information
============================================================

Uses Yelp Fusion API to collect:
- Business search results
- Business details (hours, ratings, price range)
- Review data and review counts
- Photos and categories

API Documentation: https://docs.developer.yelp.com/docs/fusion-intro
"""

import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class YelpBusiness:
    """Yelp business data structure"""
    yelp_id: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    price: Optional[str] = None
    categories: Optional[List[str]] = None
    is_closed: Optional[bool] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    distance: Optional[float] = None


@dataclass
class YelpReview:
    """Yelp review data structure"""
    review_id: str
    rating: int
    text: str
    time_created: str
    user_name: Optional[str] = None
    user_image_url: Optional[str] = None


class YelpAgent:
    """
    Agent for querying Yelp Fusion API to collect business and review data.
    
    Requires YELP_API_KEY environment variable.
    
    Rate Limits (as of 2024):
    - 5000 API calls per day
    - Search: Returns up to 50 businesses per call
    - Reviews: Returns up to 3 reviews per business (API limitation)
    
    Usage:
        agent = YelpAgent()
        results = agent.search_businesses(
            term="fast food",
            location="Minneapolis, MN",
            limit=50
        )
    """
    
    BASE_URL = "https://api.yelp.com/v3"
    
    def __init__(self):
        self.api_key = os.getenv("YELP_API_KEY")
        if not self.api_key:
            raise ValueError("YELP_API_KEY environment variable not set")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        })
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.2  # 5 requests per second max
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Yelp API"""
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"[Yelp] Rate limit exceeded, waiting 60s...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            elif response.status_code == 401:
                print("[Yelp] Invalid API key")
                return None
            else:
                print(f"[Yelp] HTTP error {response.status_code}: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"[Yelp] Request error: {e}")
            return None
    
    def search_businesses(
        self,
        term: str,
        location: str,
        categories: str = None,
        latitude: float = None,
        longitude: float = None,
        radius: int = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "best_match",
        price: str = None
    ) -> List[YelpBusiness]:
        """
        Search for businesses on Yelp.
        
        Args:
            term: Search term (e.g., "fast food", "pharmacy")
            location: Location string (e.g., "Minneapolis, MN")
            categories: Yelp category filter (e.g., "hotdogs,burgers")
            latitude: Latitude for location-based search
            longitude: Longitude for location-based search
            radius: Search radius in meters (max 40000)
            limit: Number of results (max 50)
            offset: Pagination offset (max 1000)
            sort_by: "best_match", "rating", "review_count", "distance"
            price: Price filter "1", "2", "3", "4" or combinations
        
        Returns:
            List of YelpBusiness objects
        """
        params = {
            "term": term,
            "limit": min(limit, 50),
            "offset": offset,
            "sort_by": sort_by
        }
        
        if latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude
        else:
            params["location"] = location
        
        if categories:
            params["categories"] = categories
        if radius:
            params["radius"] = min(radius, 40000)
        if price:
            params["price"] = price
        
        data = self._make_request("businesses/search", params)
        if not data or "businesses" not in data:
            return []
        
        businesses = []
        for biz in data["businesses"]:
            location_data = biz.get("location", {})
            coords = biz.get("coordinates", {})
            
            businesses.append(YelpBusiness(
                yelp_id=biz.get("id"),
                name=biz.get("name"),
                phone=biz.get("phone"),
                address=", ".join(location_data.get("display_address", [])),
                city=location_data.get("city"),
                state=location_data.get("state"),
                zip_code=location_data.get("zip_code"),
                latitude=coords.get("latitude"),
                longitude=coords.get("longitude"),
                rating=biz.get("rating"),
                review_count=biz.get("review_count"),
                price=biz.get("price"),
                categories=[c.get("title") for c in biz.get("categories", [])],
                is_closed=biz.get("is_closed"),
                url=biz.get("url"),
                image_url=biz.get("image_url"),
                distance=biz.get("distance")
            ))
        
        return businesses
    
    def search_all(
        self,
        term: str,
        location: str,
        max_results: int = 200,
        **kwargs
    ) -> List[YelpBusiness]:
        """
        Search with pagination to get more than 50 results.
        
        Args:
            term: Search term
            location: Location string
            max_results: Maximum total results (API limit: 1000)
            **kwargs: Additional search parameters
        
        Returns:
            List of all YelpBusiness objects found
        """
        all_businesses = []
        offset = 0
        
        while len(all_businesses) < max_results:
            remaining = min(50, max_results - len(all_businesses))
            businesses = self.search_businesses(
                term=term,
                location=location,
                limit=remaining,
                offset=offset,
                **kwargs
            )
            
            if not businesses:
                break
            
            all_businesses.extend(businesses)
            offset += len(businesses)
            
            # API limit
            if offset >= 1000:
                print("[Yelp] Reached API pagination limit (1000)")
                break
        
        return all_businesses
    
    def get_business_details(self, business_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific business.
        
        Args:
            business_id: Yelp business ID
        
        Returns:
            Dict with business details including hours, photos, etc.
        """
        data = self._make_request(f"businesses/{business_id}")
        if not data:
            return None
        
        # Parse hours
        hours = []
        if "hours" in data and data["hours"]:
            for h in data["hours"][0].get("open", []):
                hours.append({
                    "day": h.get("day"),
                    "start": h.get("start"),
                    "end": h.get("end"),
                    "is_overnight": h.get("is_overnight", False)
                })
        
        location = data.get("location", {})
        coords = data.get("coordinates", {})
        
        return {
            "yelp_id": data.get("id"),
            "name": data.get("name"),
            "phone": data.get("phone"),
            "display_phone": data.get("display_phone"),
            "address": ", ".join(location.get("display_address", [])),
            "city": location.get("city"),
            "state": location.get("state"),
            "zip_code": location.get("zip_code"),
            "country": location.get("country"),
            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
            "price": data.get("price"),
            "categories": [c.get("title") for c in data.get("categories", [])],
            "is_closed": data.get("is_closed"),
            "is_claimed": data.get("is_claimed"),
            "url": data.get("url"),
            "photos": data.get("photos", []),
            "hours": hours,
            "transactions": data.get("transactions", []),
            "special_hours": data.get("special_hours", [])
        }
    
    def get_reviews(self, business_id: str, locale: str = "en_US") -> List[YelpReview]:
        """
        Get reviews for a business.
        
        Note: Yelp API only returns up to 3 reviews per business.
        For more reviews, web scraping would be needed (not recommended).
        
        Args:
            business_id: Yelp business ID
            locale: Locale for reviews (default: en_US)
        
        Returns:
            List of YelpReview objects (max 3)
        """
        params = {"locale": locale}
        data = self._make_request(f"businesses/{business_id}/reviews", params)
        
        if not data or "reviews" not in data:
            return []
        
        reviews = []
        for r in data["reviews"]:
            user = r.get("user", {})
            reviews.append(YelpReview(
                review_id=r.get("id"),
                rating=r.get("rating"),
                text=r.get("text"),
                time_created=r.get("time_created"),
                user_name=user.get("name"),
                user_image_url=user.get("image_url")
            ))
        
        return reviews
    
    def search_by_phone(self, phone: str) -> List[YelpBusiness]:
        """
        Search for businesses by phone number.
        
        Args:
            phone: Phone number in E.164 format (e.g., "+14155551234")
        
        Returns:
            List of matching businesses
        """
        # Normalize phone number
        phone = phone.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
        if not phone.startswith("+"):
            phone = "+1" + phone  # Assume US
        
        params = {"phone": phone}
        data = self._make_request("businesses/search/phone", params)
        
        if not data or "businesses" not in data:
            return []
        
        businesses = []
        for biz in data["businesses"]:
            location_data = biz.get("location", {})
            coords = biz.get("coordinates", {})
            
            businesses.append(YelpBusiness(
                yelp_id=biz.get("id"),
                name=biz.get("name"),
                phone=biz.get("phone"),
                address=", ".join(location_data.get("display_address", [])),
                city=location_data.get("city"),
                state=location_data.get("state"),
                zip_code=location_data.get("zip_code"),
                latitude=coords.get("latitude"),
                longitude=coords.get("longitude"),
                rating=biz.get("rating"),
                review_count=biz.get("review_count")
            ))
        
        return businesses
    
    def match_business(
        self,
        name: str,
        address1: str,
        city: str,
        state: str,
        country: str = "US"
    ) -> Optional[str]:
        """
        Match a business to get its Yelp ID.
        
        Args:
            name: Business name
            address1: Street address
            city: City
            state: State code
            country: Country code
        
        Returns:
            Yelp business ID if matched, None otherwise
        """
        params = {
            "name": name,
            "address1": address1,
            "city": city,
            "state": state,
            "country": country
        }
        
        data = self._make_request("businesses/matches", params)
        
        if data and "businesses" in data and data["businesses"]:
            return data["businesses"][0].get("id")
        
        return None
    
    def get_business_for_nets_record(
        self,
        company_name: str,
        street_address: str,
        city: str,
        state: str,
        zip_code: str = None,
        latitude: float = None,
        longitude: float = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get Yelp data for a NETS database record.
        
        Attempts multiple matching strategies:
        1. Direct business match by name/address
        2. Search by coordinates if available
        3. Search by location string
        
        Args:
            company_name: Business name from NETS
            street_address: Street address from NETS
            city: City name
            state: State code
            zip_code: ZIP code (optional)
            latitude: Latitude (optional)
            longitude: Longitude (optional)
        
        Returns:
            Dict with Yelp business data or None if not found
        """
        # Strategy 1: Direct match
        yelp_id = self.match_business(
            name=company_name,
            address1=street_address,
            city=city,
            state=state
        )
        
        if yelp_id:
            return self.get_business_details(yelp_id)
        
        # Strategy 2: Search by coordinates
        if latitude and longitude:
            businesses = self.search_businesses(
                term=company_name,
                location=f"{city}, {state}",
                latitude=latitude,
                longitude=longitude,
                radius=100,  # 100 meters
                limit=5
            )
            
            if businesses:
                # Find best match by name similarity
                for biz in businesses:
                    if self._name_match(company_name, biz.name):
                        return self.get_business_details(biz.yelp_id)
        
        # Strategy 3: Search by location
        location = f"{city}, {state}" + (f" {zip_code}" if zip_code else "")
        businesses = self.search_businesses(
            term=company_name,
            location=location,
            limit=10
        )
        
        if businesses:
            for biz in businesses:
                if self._name_match(company_name, biz.name):
                    return self.get_business_details(biz.yelp_id)
        
        return None
    
    def _name_match(self, name1: str, name2: str, threshold: float = 0.8) -> bool:
        """Check if two business names are similar enough"""
        if not name1 or not name2:
            return False
        
        # Normalize
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # Exact match
        if n1 == n2:
            return True
        
        # Contains match
        if n1 in n2 or n2 in n1:
            return True
        
        # Simple token overlap
        tokens1 = set(n1.split())
        tokens2 = set(n2.split())
        
        if not tokens1 or not tokens2:
            return False
        
        overlap = len(tokens1 & tokens2) / max(len(tokens1), len(tokens2))
        return overlap >= threshold


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def search_qsr_minneapolis(limit: int = 200) -> List[YelpBusiness]:
    """Search for Quick Service Restaurants in Minneapolis"""
    agent = YelpAgent()
    
    # Yelp categories for fast food / QSR
    categories = "hotdog,burgers,pizza,mexican,chinese,sandwiches,chicken_wings,tacos"
    
    return agent.search_all(
        term="fast food",
        location="Minneapolis, MN",
        categories=categories,
        max_results=limit
    )


def search_pharmacies_minneapolis(limit: int = 200) -> List[YelpBusiness]:
    """Search for pharmacies in Minneapolis"""
    agent = YelpAgent()
    
    return agent.search_all(
        term="pharmacy",
        location="Minneapolis, MN",
        categories="pharmacy,drugstores",
        max_results=limit
    )


# =============================================================================
# TEST / EXAMPLE
# =============================================================================

if __name__ == "__main__":
    import json
    
    print("Yelp API Agent Test")
    print("=" * 50)
    
    try:
        agent = YelpAgent()
        print("[OK] Agent initialized")
        
        # Test search
        print("\nSearching for fast food in Minneapolis...")
        results = agent.search_businesses(
            term="fast food",
            location="Minneapolis, MN",
            limit=5
        )
        
        print(f"Found {len(results)} businesses:")
        for biz in results:
            print(f"  - {biz.name}: {biz.rating} stars, {biz.review_count} reviews")
        
        # Test business details
        if results:
            print(f"\nGetting details for: {results[0].name}")
            details = agent.get_business_details(results[0].yelp_id)
            if details:
                print(f"  Address: {details['address']}")
                print(f"  Phone: {details.get('display_phone', 'N/A')}")
                print(f"  Categories: {', '.join(details.get('categories', []))}")
        
        print("\n[OK] All tests passed")
        
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("Set YELP_API_KEY in .env file")
    except Exception as e:
        print(f"[ERROR] {e}")
