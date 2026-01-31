"""
Dynamic City Configuration
All boundaries and ZIP codes are fetched from external APIs.
No hardcoded geographic constants.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class CityConfig:
    """
    Dynamic city configuration.
    Geographic data (bounds, ZIP codes) fetched at runtime.
    """
    city_name: str
    state: str
    timezone: str
    
    # Target NAICS codes for this city
    naics_codes: Dict[str, str] = field(default_factory=dict)
    
    # Employee estimation baselines (from BLS/Census data)
    employee_baselines: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Data source configuration
    sos_url: Optional[str] = None
    sos_enabled: bool = False
    
    # Cached boundary data (fetched dynamically)
    _boundary: Optional[Any] = field(default=None, repr=False)
    _zip_codes: Optional[List[str]] = field(default=None, repr=False)
    
    @property
    def city_key(self) -> str:
        """Return city key in format 'city_state'"""
        return f"{self.city_name.lower()}_{self.state.lower()}"
    
    def get_bounds(self) -> Optional[tuple]:
        """
        Get city bounds, fetching from API if needed.
        
        Returns:
            Tuple of (min_lon, min_lat, max_lon, max_lat) or None
        """
        if self._boundary is None:
            self._fetch_boundary()
        
        if self._boundary:
            return self._boundary.as_tuple()
        return None
    
    def get_zip_codes(self) -> List[str]:
        """
        Get city ZIP codes, fetching from API if needed.
        
        Returns:
            List of ZIP code strings
        """
        if self._zip_codes is None:
            self._fetch_zip_codes()
        
        return self._zip_codes or []
    
    def _fetch_boundary(self):
        """Fetch boundary from external API."""
        try:
            from src.geospatial.boundary_fetcher import fetch_city_boundary
            self._boundary = fetch_city_boundary(self.city_name, self.state)
            if self._boundary:
                logger.info(f"Fetched boundary for {self.city_name}, {self.state}")
            else:
                logger.warning(f"Failed to fetch boundary for {self.city_name}, {self.state}")
        except ImportError:
            logger.error("boundary_fetcher module not available")
    
    def _fetch_zip_codes(self):
        """Fetch ZIP codes from external API."""
        try:
            from src.geospatial.boundary_fetcher import fetch_city_zip_codes
            self._zip_codes = fetch_city_zip_codes(self.city_name, self.state)
            if self._zip_codes:
                logger.info(f"Fetched {len(self._zip_codes)} ZIP codes for {self.city_name}")
            else:
                logger.warning(f"Failed to fetch ZIP codes for {self.city_name}")
                self._zip_codes = []
        except ImportError:
            logger.error("boundary_fetcher module not available")
            self._zip_codes = []
    
    def is_within_bounds(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within city bounds."""
        bounds = self.get_bounds()
        if not bounds:
            return True  # No bounds = accept all
        
        min_lon, min_lat, max_lon, max_lat = bounds
        return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat
    
    def is_valid_zip(self, zip_code: str) -> bool:
        """Check if ZIP code is valid for this city."""
        zips = self.get_zip_codes()
        if not zips:
            return True  # No ZIP list = accept all
        return zip_code in zips
    
    def get_employee_baseline(self, naics_code: str) -> Dict[str, float]:
        """Get employee estimation baseline for NAICS code."""
        return self.employee_baselines.get(naics_code, {
            "median": 10,
            "mean": 12.0,
            "std": 6.0,
            "min_typical": 2,
            "max_typical": 40,
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes cached data)."""
        return {
            "city_name": self.city_name,
            "state": self.state,
            "timezone": self.timezone,
            "naics_codes": self.naics_codes,
            "employee_baselines": self.employee_baselines,
            "sos_url": self.sos_url,
            "sos_enabled": self.sos_enabled,
        }


# Default NAICS codes (QSR + Pharmacies)
DEFAULT_NAICS = {
    "722513": "Limited-Service Restaurants",
    "446110": "Pharmacies and Drug Stores",
}

# Default employee baselines (from BLS QCEW national averages)
DEFAULT_BASELINES = {
    "722513": {
        "median": 12,
        "mean": 15.3,
        "std": 8.7,
        "min_typical": 3,
        "max_typical": 50,
        "avg_reviews_per_month": 8.5,
        "avg_employees": 15,
        "min_employees": 3,
        "max_employees": 50,
        "employees_per_sqm": 0.08,
    },
    "446110": {
        "median": 8,
        "mean": 10.2,
        "std": 6.5,
        "min_typical": 2,
        "max_typical": 35,
        "avg_reviews_per_month": 3.2,
        "avg_employees": 10,
        "min_employees": 2,
        "max_employees": 35,
        "employees_per_sqm": 0.05,
    },
}


def create_city_config(
    city: str,
    state: str,
    timezone: str = "America/Chicago",
    naics_codes: Dict[str, str] = None,
    employee_baselines: Dict[str, Dict] = None,
    sos_url: str = None,
) -> CityConfig:
    """
    Factory function to create a city configuration.
    
    Args:
        city: City name
        state: State abbreviation
        timezone: IANA timezone string
        naics_codes: Target NAICS codes (uses default if None)
        employee_baselines: Employee estimation baselines (uses default if None)
        sos_url: Secretary of State business lookup URL
        
    Returns:
        CityConfig instance
    """
    return CityConfig(
        city_name=city,
        state=state,
        timezone=timezone,
        naics_codes=naics_codes or DEFAULT_NAICS.copy(),
        employee_baselines=employee_baselines or DEFAULT_BASELINES.copy(),
        sos_url=sos_url,
        sos_enabled=sos_url is not None,
    )


# Pre-defined city configurations (boundaries fetched dynamically)
CITY_CONFIGS: Dict[str, CityConfig] = {}


def get_city_config(city_key: str) -> Optional[CityConfig]:
    """
    Get or create city configuration by key.
    
    Args:
        city_key: City key in format 'city_state' (e.g., 'minneapolis_mn')
        
    Returns:
        CityConfig instance or None
    """
    if city_key in CITY_CONFIGS:
        return CITY_CONFIGS[city_key]
    
    # Parse city key
    parts = city_key.rsplit("_", 1)
    if len(parts) != 2:
        logger.error(f"Invalid city key format: {city_key}")
        return None
    
    city_name, state = parts
    city_name = city_name.replace("_", " ").title()
    state = state.upper()
    
    # Timezone mapping
    timezone_map = {
        "MN": "America/Chicago",
        "CO": "America/Denver",
        "CA": "America/Los_Angeles",
        "NY": "America/New_York",
        "TX": "America/Chicago",
        "IL": "America/Chicago",
        "WA": "America/Los_Angeles",
        "FL": "America/New_York",
    }
    
    timezone = timezone_map.get(state, "America/Chicago")
    
    # Create config with dynamic boundary fetching
    config = create_city_config(
        city=city_name,
        state=state,
        timezone=timezone,
    )
    
    # Cache for future use
    CITY_CONFIGS[city_key] = config
    
    return config


def register_city_config(config: CityConfig):
    """Register a city configuration."""
    CITY_CONFIGS[config.city_key] = config


def list_available_cities() -> List[str]:
    """List all registered city keys."""
    return list(CITY_CONFIGS.keys())
