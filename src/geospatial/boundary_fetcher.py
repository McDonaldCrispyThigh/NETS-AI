"""
Dynamic City Boundary Fetcher
Downloads and caches city boundaries from OpenStreetMap Nominatim API.
No hardcoded coordinates - all boundaries fetched at runtime.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)

# Cache directory for downloaded boundaries
# Path: src/geospatial/boundary_fetcher.py -> parent.parent.parent = project root
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "boundaries"

# OpenStreetMap Nominatim API (free, no key required)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# US Census Bureau TIGERweb API
CENSUS_URL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer/0/query"


@dataclass
class CityBoundary:
    """Container for city boundary data"""
    city_name: str
    state: str
    min_lon: float
    max_lon: float
    min_lat: float
    max_lat: float
    source: str
    fetched_at: str
    polygon: Optional[List] = None  # Full polygon if available
    
    def as_tuple(self) -> Tuple[float, float, float, float]:
        """Return bounds as (min_lon, min_lat, max_lon, max_lat)"""
        return (self.min_lon, self.min_lat, self.max_lon, self.max_lat)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "city_name": self.city_name,
            "state": self.state,
            "min_lon": self.min_lon,
            "max_lon": self.max_lon,
            "min_lat": self.min_lat,
            "max_lat": self.max_lat,
            "source": self.source,
            "fetched_at": self.fetched_at,
            "polygon": self.polygon
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CityBoundary":
        """Create from dictionary"""
        return cls(
            city_name=data["city_name"],
            state=data["state"],
            min_lon=data["min_lon"],
            max_lon=data["max_lon"],
            min_lat=data["min_lat"],
            max_lat=data["max_lat"],
            source=data["source"],
            fetched_at=data["fetched_at"],
            polygon=data.get("polygon")
        )


class BoundaryFetcher:
    """
    Fetch city boundaries from external APIs.
    Caches results locally to avoid repeated API calls.
    """
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        """Initialize fetcher with cache directory."""
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NETS-Enhancement/1.0 (Research Project)"
        })
    
    def get_boundary(
        self, 
        city: str, 
        state: str, 
        force_refresh: bool = False
    ) -> Optional[CityBoundary]:
        """
        Get city boundary, fetching from API if not cached.
        
        Args:
            city: City name (e.g., "Minneapolis")
            state: State abbreviation (e.g., "MN")
            force_refresh: If True, ignore cache and fetch fresh data
            
        Returns:
            CityBoundary object or None if fetch fails
        """
        cache_key = f"{city.lower()}_{state.lower()}"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Check cache first
        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    logger.info(f"Loaded cached boundary for {city}, {state}")
                    return CityBoundary.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Cache corrupted for {city}, {state}: {e}")
        
        # Fetch from API
        boundary = self._fetch_from_nominatim(city, state)
        
        if boundary is None:
            # Fallback to Census Bureau
            boundary = self._fetch_from_census(city, state)
        
        if boundary:
            # Cache the result
            self._save_to_cache(boundary, cache_file)
        
        return boundary
    
    def _fetch_from_nominatim(self, city: str, state: str) -> Optional[CityBoundary]:
        """
        Fetch boundary from OpenStreetMap Nominatim API.
        
        Args:
            city: City name
            state: State abbreviation
            
        Returns:
            CityBoundary or None
        """
        try:
            params = {
                "q": f"{city}, {state}, USA",
                "format": "json",
                "polygon_geojson": 1,
                "limit": 1,
                "addressdetails": 1
            }
            
            response = self.session.get(NOMINATIM_URL, params=params, timeout=10)
            response.raise_for_status()
            
            # Respect Nominatim rate limit (1 request/second)
            time.sleep(1.1)
            
            results = response.json()
            
            if not results:
                logger.warning(f"No results from Nominatim for {city}, {state}")
                return None
            
            result = results[0]
            boundingbox = result.get("boundingbox", [])
            
            if len(boundingbox) != 4:
                logger.warning(f"Invalid bounding box from Nominatim: {boundingbox}")
                return None
            
            # Nominatim returns [min_lat, max_lat, min_lon, max_lon]
            min_lat, max_lat, min_lon, max_lon = map(float, boundingbox)
            
            # Extract polygon if available
            polygon = None
            geojson = result.get("geojson")
            if geojson and geojson.get("type") in ["Polygon", "MultiPolygon"]:
                polygon = geojson.get("coordinates")
            
            from datetime import datetime
            
            boundary = CityBoundary(
                city_name=city,
                state=state,
                min_lon=min_lon,
                max_lon=max_lon,
                min_lat=min_lat,
                max_lat=max_lat,
                source="OpenStreetMap Nominatim",
                fetched_at=datetime.now().isoformat(),
                polygon=polygon
            )
            
            logger.info(f"Fetched boundary for {city}, {state} from Nominatim")
            return boundary
            
        except requests.RequestException as e:
            logger.error(f"Nominatim API error for {city}, {state}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Nominatim response: {e}")
            return None
    
    def _fetch_from_census(self, city: str, state: str) -> Optional[CityBoundary]:
        """
        Fetch boundary from US Census Bureau TIGERweb API.
        Fallback if Nominatim fails.
        
        Args:
            city: City name
            state: State abbreviation
            
        Returns:
            CityBoundary or None
        """
        try:
            # Census uses full state names
            state_names = {
                "MN": "Minnesota",
                "CO": "Colorado",
                "CA": "California",
                "TX": "Texas",
                "NY": "New York",
                "IL": "Illinois",
                "WA": "Washington",
                "OR": "Oregon",
                "FL": "Florida",
                "GA": "Georgia",
            }
            
            state_full = state_names.get(state.upper(), state)
            
            params = {
                "where": f"NAME='{city}' AND STATE='{state_full}'",
                "outFields": "NAME,STATE,GEOID",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "json"
            }
            
            response = self.session.get(CENSUS_URL, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            if not features:
                logger.warning(f"No results from Census for {city}, {state}")
                return None
            
            # Get geometry extent
            geometry = features[0].get("geometry", {})
            rings = geometry.get("rings", [[]])
            
            if not rings or not rings[0]:
                logger.warning(f"No geometry from Census for {city}, {state}")
                return None
            
            # Calculate bounding box from polygon rings
            coords = rings[0]
            lons = [p[0] for p in coords]
            lats = [p[1] for p in coords]
            
            from datetime import datetime
            
            boundary = CityBoundary(
                city_name=city,
                state=state,
                min_lon=min(lons),
                max_lon=max(lons),
                min_lat=min(lats),
                max_lat=max(lats),
                source="US Census Bureau TIGERweb",
                fetched_at=datetime.now().isoformat(),
                polygon=rings
            )
            
            logger.info(f"Fetched boundary for {city}, {state} from Census")
            return boundary
            
        except requests.RequestException as e:
            logger.error(f"Census API error for {city}, {state}: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Census response: {e}")
            return None
    
    def _save_to_cache(self, boundary: CityBoundary, cache_file: Path):
        """Save boundary to cache file."""
        try:
            with open(cache_file, "w") as f:
                json.dump(boundary.to_dict(), f, indent=2)
            logger.info(f"Cached boundary to {cache_file}")
        except IOError as e:
            logger.warning(f"Failed to cache boundary: {e}")
    
    def get_zip_codes(self, city: str, state: str) -> Optional[List[str]]:
        """
        Fetch ZIP codes for a city from Census data.
        
        Args:
            city: City name
            state: State abbreviation
            
        Returns:
            List of ZIP code strings or None
        """
        cache_key = f"{city.lower()}_{state.lower()}_zipcodes"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Check cache
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    return data.get("zip_codes", [])
            except json.JSONDecodeError:
                pass
        
        # Fetch from Census ZCTA API
        try:
            # Use Census Geocoder to get ZCTAs overlapping city
            zcta_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/ZCTA520/MapServer/0/query"
            
            # First get city boundary
            boundary = self.get_boundary(city, state)
            if not boundary:
                return None
            
            # Query ZCTAs within bounding box
            params = {
                "geometry": f"{boundary.min_lon},{boundary.min_lat},{boundary.max_lon},{boundary.max_lat}",
                "geometryType": "esriGeometryEnvelope",
                "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects",
                "outFields": "ZCTA5CE20",
                "returnGeometry": "false",
                "f": "json"
            }
            
            response = self.session.get(zcta_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            zip_codes = [
                f["attributes"]["ZCTA5CE20"]
                for f in features
                if "attributes" in f and "ZCTA5CE20" in f["attributes"]
            ]
            
            # Cache result
            if zip_codes:
                with open(cache_file, "w") as f:
                    json.dump({"zip_codes": zip_codes}, f, indent=2)
            
            return zip_codes
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch ZIP codes: {e}")
            return None


# Singleton instance
_fetcher = None


def get_fetcher() -> BoundaryFetcher:
    """Get singleton BoundaryFetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = BoundaryFetcher()
    return _fetcher


def fetch_city_boundary(city: str, state: str) -> Optional[CityBoundary]:
    """
    Convenience function to fetch city boundary.
    
    Args:
        city: City name
        state: State abbreviation
        
    Returns:
        CityBoundary or None
    """
    return get_fetcher().get_boundary(city, state)


def fetch_city_zip_codes(city: str, state: str) -> Optional[List[str]]:
    """
    Convenience function to fetch city ZIP codes.
    
    Args:
        city: City name
        state: State abbreviation
        
    Returns:
        List of ZIP codes or None
    """
    return get_fetcher().get_zip_codes(city, state)
